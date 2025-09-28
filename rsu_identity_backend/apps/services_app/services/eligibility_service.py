# ===================================================================
# RSU GABON - SERVICE ELIGIBILITY MIS À JOUR
# Intégration programmes paramétrables par administrateurs
# ===================================================================

import logging
from typing import Dict, List, Optional
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Avg, Q

from apps.identity_app.models import PersonIdentity
from ..models import SocialProgramEligibility, VulnerabilityAssessment, SocialProgram
from services.base_service import BaseService

logger = logging.getLogger(__name__)


class EligibilityService(BaseService):
    """
    Service de calcul éligibilité programmes sociaux
    MISE À JOUR: Utilise programmes paramétrables par administrateurs
    """

    def __init__(self):
        super().__init__()
        # Chargement dynamique des programmes depuis base de données
        self.refresh_programs_cache()
    
    def refresh_programs_cache(self):
        """Actualise le cache des programmes actifs"""
        self.active_programs = {
            program.code: program 
            for program in SocialProgram.objects.filter(is_active=True)
        }
        self.log_operation('programs_cache_refreshed', {
            'active_programs_count': len(self.active_programs)
        })

    def get_program_criteria(self, program_code: str) -> Dict:
        """
        Récupère critères programme depuis configuration administrateur
        
        Args:
            program_code: Code du programme
            
        Returns:
            Dict: Critères configurés par l'administrateur
        """
        if program_code not in self.active_programs:
            self.refresh_programs_cache()  # Actualiser cache
            
        if program_code not in self.active_programs:
            raise ValueError(f"Programme {program_code} non actif ou inexistant")
        
        program = self.active_programs[program_code]
        
        # Conversion format unifié
        criteria = {
            'name': program.name,
            'vulnerability_threshold': program.eligibility_criteria.get('vulnerability_threshold', 50),
            'age_min': program.eligibility_criteria.get('age_min', 0),
            'age_max': program.eligibility_criteria.get('age_max'),
            'priority_provinces': program.target_provinces or [],
            'estimated_benefit_fcfa': float(program.benefit_amount_fcfa),
            'duration_months': program.duration_months,
            
            # Critères spécifiques paramétrables
            'requires_children': program.eligibility_criteria.get('requires_children', False),
            'min_children': program.eligibility_criteria.get('min_children', 1),
            'gender_preference': program.eligibility_criteria.get('gender_preference'),
            'special_conditions': program.eligibility_criteria.get('special_conditions', []),
            'max_beneficiaries': program.max_beneficiaries,
            'current_beneficiaries': program.current_beneficiaries,
            
            # Informations budgétaires
            'budget_available': program.is_budget_available,
            'can_accept_new': program.can_accept_new_beneficiaries,
            'program_type': program.program_type,
            'automated_enrollment': program.automated_enrollment,
            'requires_documents': program.requires_documents,
        }
        
        return criteria

    def calculate_program_eligibility(
        self, 
        person_id: int, 
        program_code: str, 
        recalculate: bool = False
    ) -> SocialProgramEligibility:
        """
        Calcule éligibilité avec programmes paramétrables
        
        Args:
            person_id: ID de la personne
            program_code: Code du programme social
            recalculate: Forcer recalcul si éligibilité existe
            
        Returns:
            SocialProgramEligibility: Éligibilité calculée et sauvegardée
        """
        try:
            person = PersonIdentity.objects.get(id=person_id)
            
            # Vérifier que le programme existe et est actif
            criteria = self.get_program_criteria(program_code)
            program = self.active_programs[program_code]
            
            # Vérifier si programme peut accepter nouveaux bénéficiaires
            if not criteria['can_accept_new']:
                logger.warning(f"Programme {program_code} ne peut pas accepter de nouveaux bénéficiaires")
                return self._create_program_full_eligibility(person, program_code)
            
            # Vérifier éligibilité existante
            existing_eligibility = SocialProgramEligibility.objects.filter(
                person=person,
                program_code=program_code
            ).order_by('-calculated_at').first()
            
            if existing_eligibility and not recalculate:
                # Éligibilité récente existe (< 3 mois)
                days_since = (timezone.now() - existing_eligibility.calculated_at).days
                if days_since < 90:  # 3 mois
                    self.log_operation(
                        'eligibility_skipped', 
                        {
                            'person_id': person_id, 
                            'program_code': program_code,
                            'reason': 'recent_eligibility_exists'
                        }
                    )
                    return existing_eligibility
            
            # Calcul nouvelle éligibilité avec critères administrateur
            eligibility_data = self._calculate_program_eligibility_score(
                person, program_code, criteria
            )
            
            # Sauvegarde avec transaction
            with transaction.atomic():
                eligibility = SocialProgramEligibility.objects.create(
                    person=person,
                    program_code=program_code,
                    **eligibility_data
                )
                
                # Si fortement recommandé et inscription automatique activée
                if (criteria['automated_enrollment'] and 
                    eligibility.recommendation_level == 'HIGHLY_RECOMMENDED'):
                    self._auto_enroll_beneficiary(person, program, eligibility)
                
                self.log_operation(
                    'eligibility_calculated', 
                    {
                        'person_id': person_id,
                        'program_code': program_code,
                        'eligibility_score': float(eligibility.eligibility_score),
                        'recommendation_level': eligibility.recommendation_level,
                        'auto_enrolled': criteria['automated_enrollment']
                    }
                )
                
                return eligibility
                
        except PersonIdentity.DoesNotExist:
            logger.error(f"PersonIdentity {person_id} not found")
            raise ValueError(f"Personne avec ID {person_id} introuvable")
        except Exception as e:
            logger.error(f"Erreur calcul éligibilité {program_code} pour {person_id}: {str(e)}")
            raise

    def _calculate_program_eligibility_score(
        self, 
        person: PersonIdentity, 
        program_code: str,
        criteria: Dict
    ) -> Dict:
        """
        Calcule score éligibilité avec critères paramétrables
        
        Args:
            person: Instance PersonIdentity
            program_code: Code programme social
            criteria: Critères configurés par administrateur
            
        Returns:
            Dict: Données éligibilité complètes
        """
        score = 0.0
        criteria_met = {}
        missing_documents = []
        recommendation_level = 'NOT_ELIGIBLE'
        
        # 1. Vérification critères d'âge (paramétrables)
        age_eligible = self._check_age_criteria(person, criteria)
        if age_eligible:
            score += 20
            criteria_met['age_criteria'] = True
        else:
            criteria_met['age_criteria'] = False
            return self._create_ineligible_result(
                score, criteria_met, missing_documents, 
                f"Âge requis: {criteria.get('age_min', 0)}-{criteria.get('age_max', '∞')} ans"
            )
        
        # 2. Vérification vulnérabilité (seuil paramétrable)
        vulnerability_score = self._get_vulnerability_score(person)
        vulnerability_threshold = criteria['vulnerability_threshold']
        vulnerability_eligible = vulnerability_score >= vulnerability_threshold
        
        if vulnerability_eligible:
            # Score progressif basé sur seuil administrateur
            vulnerability_bonus = min(40, (vulnerability_score - vulnerability_threshold) / 2)
            score += 20 + vulnerability_bonus
            criteria_met['vulnerability_criteria'] = True
        else:
            score += 10  # Score partiel même si sous seuil
            criteria_met['vulnerability_criteria'] = False
            missing_documents.append(f"Score vulnérabilité minimum requis: {vulnerability_threshold}")
        
        # 3. Critères spécifiques paramétrables
        program_bonus = self._calculate_parametrizable_criteria(
            person, program_code, criteria, criteria_met, missing_documents
        )
        score += program_bonus
        
        # 4. Bonus géographique (provinces paramétrables)
        priority_provinces = criteria.get('priority_provinces', [])
        if priority_provinces and person.province in priority_provinces:
            score += 15  # Bonus plus élevé pour zones administrateur
            criteria_met['geographic_priority'] = True
        
        # 5. Vérification documents requis (paramétrables)
        required_docs = criteria.get('requires_documents', [])
        if required_docs:
            missing_documents.extend([
                f"Document requis: {doc}" for doc in required_docs
            ])
            criteria_met['documents_check'] = False
        else:
            criteria_met['documents_check'] = True
        
        # 6. Conditions spéciales paramétrables
        special_conditions = criteria.get('special_conditions', [])
        special_bonus = self._check_special_conditions(
            person, special_conditions, criteria_met
        )
        score += special_bonus
        
        # Normalisation score (0-100)
        final_score = min(100.0, max(0.0, score))
        
        # Détermination niveau recommandation
        recommendation_level = self._determine_recommendation_level(
            final_score, criteria_met, program_code, criteria
        )
        
        # Calcul montant estimé (configuré par administrateur)
        estimated_amount = self._calculate_estimated_benefit_parametrizable(
            person, criteria, final_score
        )
        
        return {
            'eligibility_score': Decimal(str(round(final_score, 2))),
            'recommendation_level': recommendation_level,
            'criteria_met': criteria_met,
            'missing_documents': missing_documents,
            'estimated_benefit_amount': estimated_amount
        }

    def _calculate_parametrizable_criteria(
        self, 
        person: PersonIdentity, 
        program_code: str, 
        criteria: Dict,
        criteria_met: Dict,
        missing_documents: List
    ) -> float:
        """Calcule bonus basés sur critères paramétrables administrateur"""
        bonus = 0.0
        
        # Critère enfants (paramétrable)
        if criteria.get('requires_children', False):
            min_children = criteria.get('min_children', 1)
            if hasattr(person, 'household') and person.household:
                children_count = getattr(person.household, 'members_under_15', 0)
                if children_count >= min_children:
                    bonus += 20 + (children_count * 3)  # Bonus paramétrable
                    criteria_met['has_required_children'] = True
                else:
                    criteria_met['has_required_children'] = False
                    missing_documents.append(f'Minimum {min_children} enfant(s) requis')
            else:
                criteria_met['has_required_children'] = False
                missing_documents.append('Composition ménage avec enfants requise')
        
        # Préférence genre (paramétrable)
        gender_preference = criteria.get('gender_preference')
        if gender_preference and person.gender == gender_preference:
            bonus += 12
            criteria_met['gender_preference_met'] = True
        
        # Type de programme (paramétrable)
        program_type = criteria.get('program_type')
        if program_type == 'CASH_TRANSFER':
            # Bonus pour transferts monétaires directs
            if person.age and 18 <= person.age <= 65:
                bonus += 8
                criteria_met['cash_transfer_eligible'] = True
        
        elif program_type == 'TRAINING':
            # Bonus formation selon âge optimal
            if person.age and 16 <= person.age <= 35:
                bonus += 15
                criteria_met['training_age_optimal'] = True
        
        elif program_type == 'HEALTHCARE':
            # Bonus santé pour groupes vulnérables
            if person.age and (person.age < 5 or person.age > 65):
                bonus += 18
                criteria_met['health_vulnerable_group'] = True
            
            if person.gender == 'F' and person.age and 15 <= person.age <= 49:
                bonus += 12  # Santé reproductive
                criteria_met['reproductive_health_priority'] = True
        
        elif program_type == 'EDUCATION':
            # Bonus éducation selon âge scolaire
            if person.age and 6 <= person.age <= 25:
                bonus += 20
                criteria_met['education_age_range'] = True
        
        return min(25.0, bonus)  # Max 25 points bonus paramétrables

    def _check_special_conditions(
        self, 
        person: PersonIdentity, 
        special_conditions: List[str],
        criteria_met: Dict
    ) -> float:
        """Vérifie conditions spéciales paramétrables"""
        bonus = 0.0
        conditions_met = []
        
        for condition in special_conditions:
            if condition == 'handicap':
                # Estimation handicap (nécessiterait évaluation médicale)
                if person.age and person.age > 70:
                    bonus += 15
                    conditions_met.append('handicap_age_related')
            
            elif condition == 'orphelin':
                # Estimation orphelinage (complexe sans données familiales)
                if person.age and person.age < 18:
                    if not hasattr(person, 'household') or not person.household:
                        bonus += 20
                        conditions_met.append('potential_orphan')
            
            elif condition == 'femme_enceinte':
                # Estimation basée sur âge reproductif
                if person.gender == 'F' and person.age and 15 <= person.age <= 45:
                    bonus += 10
                    conditions_met.append('reproductive_age')
            
            elif condition == 'chef_menage_femme':
                # Chef de ménage féminin
                if (person.gender == 'F' and 
                    hasattr(person, 'household') and person.household and
                    person.household.head_of_household == person):
                    bonus += 18
                    conditions_met.append('female_head_household')
            
            elif condition == 'grande_famille':
                # Famille nombreuse
                if hasattr(person, 'household') and person.household:
                    total_members = getattr(person.household, 'total_members', 1)
                    if total_members > 6:
                        bonus += 12
                        conditions_met.append('large_family')
        
        criteria_met['special_conditions_met'] = conditions_met
        return min(30.0, bonus)  # Max 30 points conditions spéciales

    def _calculate_estimated_benefit_parametrizable(
        self, 
        person: PersonIdentity, 
        criteria: Dict, 
        score: float
    ) -> Optional[Decimal]:
        """Calcule montant basé sur configuration administrateur"""
        base_amount = criteria.get('estimated_benefit_fcfa', 0)
        
        if base_amount == 0:
            return None
        
        # Ajustements selon paramètres programme
        multiplier = 1.0
        
        # Ajustement selon type programme
        program_type = criteria.get('program_type')
        if program_type == 'CASH_TRANSFER':
            # Transfert direct - montant fixe généralement
            pass
        elif program_type == 'IN_KIND':
            # Aide en nature - peut varier selon taille famille
            if hasattr(person, 'household') and person.household:
                total_members = getattr(person.household, 'total_members', 1)
                multiplier = min(2.0, 1 + (total_members - 1) * 0.2)
        elif program_type == 'CREDIT':
            # Montant crédit selon score éligibilité
            if score >= 80:
                multiplier = 1.5
            elif score >= 60:
                multiplier = 1.2
            else:
                multiplier = 0.8
        
        # Ajustement géographique (si configuré)
        priority_provinces = criteria.get('priority_provinces', [])
        if priority_provinces and person.province in priority_provinces:
            multiplier *= 1.1  # Bonus 10% zones prioritaires
        
        # Ajustement coût de la vie par province
        cost_adjustments = {
            'ESTUAIRE': 1.3,      # Libreville - coût élevé
            'OGOOUE_MARITIME': 1.2,  # Port-Gentil
            'NYANGA': 0.9,        # Zone rurale - coût moindre
            'OGOOUE_LOLO': 0.9,
        }
        
        province_multiplier = cost_adjustments.get(person.province, 1.0)
        multiplier *= province_multiplier
        
        final_amount = base_amount * multiplier
        return Decimal(str(round(final_amount, 0)))

    def _auto_enroll_beneficiary(
        self, 
        person: PersonIdentity, 
        program: SocialProgram, 
        eligibility: SocialProgramEligibility
    ):
        """Inscription automatique si configurée par administrateur"""
        try:
            if program.add_beneficiary():
                eligibility.enrollment_status = 'ENROLLED'
                eligibility.enrollment_date = timezone.now()
                eligibility.save(update_fields=['enrollment_status', 'enrollment_date'])
                
                self.log_operation(
                    'auto_enrollment_success',
                    {
                        'person_id': person.id,
                        'program_code': program.code,
                        'enrollment_date': eligibility.enrollment_date.isoformat()
                    }
                )
            else:
                # Programme plein - mettre en liste d'attente
                eligibility.enrollment_status = 'PENDING_ENROLLMENT'
                eligibility.save(update_fields=['enrollment_status'])
                
                self.log_operation(
                    'auto_enrollment_pending',
                    {
                        'person_id': person.id,
                        'program_code': program.code,
                        'reason': 'program_capacity_reached'
                    }
                )
        except Exception as e:
            logger.error(f"Erreur inscription automatique {person.id} dans {program.code}: {str(e)}")

    def _create_program_full_eligibility(
        self, 
        person: PersonIdentity, 
        program_code: str
    ) -> SocialProgramEligibility:
        """Crée éligibilité pour programme plein"""
        return SocialProgramEligibility.objects.create(
            person=person,
            program_code=program_code,
            eligibility_score=Decimal('0.00'),
            recommendation_level='NOT_ELIGIBLE',
            criteria_met={'program_status': 'full_or_inactive'},
            missing_documents=['Programme temporairement fermé ou budget épuisé'],
            estimated_benefit_amount=None
        )

    def get_all_active_programs(self) -> Dict[str, Dict]:
        """Retourne tous les programmes actifs configurés"""
        self.refresh_programs_cache()
        
        programs_info = {}
        for code, program in self.active_programs.items():
            programs_info[code] = {
                'name': program.name,
                'description': program.description,
                'program_type': program.program_type,
                'benefit_amount_fcfa': float(program.benefit_amount_fcfa),
                'duration_months': program.duration_months,
                'can_accept_new': program.can_accept_new_beneficiaries,
                'current_beneficiaries': program.current_beneficiaries,
                'max_beneficiaries': program.max_beneficiaries,
                'budget_remaining': float(program.budget_remaining_fcfa),
                'target_provinces': program.target_provinces,
                'automated_enrollment': program.automated_enrollment,
                'priority_level': program.priority_level,
                'responsible_ministry': program.responsible_ministry
            }
        
        return programs_info

    def get_program_budget_status(self, program_code: str) -> Dict:
        """Retourne statut budgétaire détaillé d'un programme"""
        if program_code not in self.active_programs:
            self.refresh_programs_cache()
        
        if program_code not in self.active_programs:
            raise ValueError(f"Programme {program_code} non trouvé")
        
        program = self.active_programs[program_code]
        
        return {
            'program_code': program_code,
            'program_name': program.name,
            'budget_total_fcfa': float(program.budget_total_fcfa),
            'budget_used_fcfa': float(program.budget_used_fcfa),
            'budget_remaining_fcfa': float(program.budget_remaining_fcfa),
            'utilization_percentage': program.budget_utilization_percentage,
            'estimated_beneficiaries_possible': program.estimated_beneficiaries_possible,
            'current_beneficiaries': program.current_beneficiaries,
            'max_beneficiaries': program.max_beneficiaries,
            'can_accept_new': program.can_accept_new_beneficiaries,
            'is_budget_available': program.is_budget_available,
            'benefit_amount_fcfa': float(program.benefit_amount_fcfa)
        }