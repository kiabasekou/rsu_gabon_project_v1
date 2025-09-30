# ===================================================================
# RSU GABON - SERVICE ELIGIBILITY COMPLET
# Matching intelligent personne ↔ programmes sociaux
# ===================================================================

import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Avg, Q

from apps.identity_app.models import PersonIdentity
from ..models import (
    SocialProgramEligibility, 
    VulnerabilityAssessment, 
    SocialProgram
)

from .base_service import BaseService

logger = logging.getLogger(__name__)


class EligibilityService(BaseService):
    """
    Service de calcul éligibilité programmes sociaux
    Utilise programmes paramétrables par administrateurs
    """
    
    # Pondérations scoring éligibilité
    SCORING_WEIGHTS = {
        'vulnerability_score': 0.40,      # Score vulnérabilité
        'profile_matching': 0.30,         # Adéquation profil/programme
        'need_urgency': 0.20,             # Urgence besoin
        'absorption_capacity': 0.10       # Capacité absorption aide
    }

    def __init__(self):
        super().__init__()
        # Chargement dynamique programmes depuis base de données
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
            self.refresh_programs_cache()
            
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

    @transaction.atomic
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
            person = PersonIdentity.objects.select_related('household').get(id=person_id)
            
            # Vérifier que le programme existe et est actif
            criteria = self.get_program_criteria(program_code)
            program = self.active_programs[program_code]
            
            # Vérifier si programme peut accepter nouveaux bénéficiaires
            if not criteria['can_accept_new']:
                logger.warning(f"Programme {program_code} fermé aux nouvelles inscriptions")
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
            
            # Sauvegarde
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
        blocking_factors = []
        
        # 1. Vérification critères d'âge (paramétrables)
        age_eligible, age_score = self._check_age_criteria(person, criteria)
        criteria_met['age_criteria'] = age_eligible
        score += age_score
        
        if not age_eligible:
            blocking_factors.append(
                f"Âge requis: {criteria.get('age_min', 0)}-{criteria.get('age_max', '∞')} ans"
            )
            return self._create_ineligible_result(
                score, criteria_met, blocking_factors, missing_documents
            )
        
        # 2. Vérification vulnérabilité (pondération 40%)
        vuln_eligible, vuln_score = self._check_vulnerability_criteria(person, criteria)
        criteria_met['vulnerability_criteria'] = vuln_eligible
        score += vuln_score * self.SCORING_WEIGHTS['vulnerability_score']
        
        if not vuln_eligible:
            blocking_factors.append(
                f"Score vulnérabilité insuffisant (seuil: {criteria['vulnerability_threshold']})"
            )
        
        # 3. Adéquation profil/programme (pondération 30%)
        profile_eligible, profile_score, profile_factors = self._check_profile_matching(
            person, criteria
        )
        criteria_met['profile_matching'] = profile_eligible
        criteria_met['profile_factors'] = profile_factors
        score += profile_score * self.SCORING_WEIGHTS['profile_matching']
        
        if not profile_eligible:
            blocking_factors.extend(profile_factors)
        
        # 4. Urgence besoin (pondération 20%)
        urgency_score = self._calculate_need_urgency(person, criteria)
        score += urgency_score * self.SCORING_WEIGHTS['need_urgency']
        
        # 5. Capacité absorption aide (pondération 10%)
        absorption_score = self._calculate_absorption_capacity(person, criteria)
        score += absorption_score * self.SCORING_WEIGHTS['absorption_capacity']
        
        # 6. Province prioritaire (bonus)
        if criteria['priority_provinces'] and person.province in criteria['priority_provinces']:
            score += 10
            criteria_met['priority_province'] = True
        else:
            criteria_met['priority_province'] = False
        
        # Score final (0-100)
        final_score = min(score, 100.0)
        
        # Déterminer niveau recommandation
        recommendation_level = self._determine_recommendation_level(
            final_score, 
            blocking_factors
        )
        
        # Priorité traitement
        processing_priority = self._determine_processing_priority(
            final_score, 
            person, 
            criteria
        )
        
        # Documents requis
        if criteria['requires_documents']:
            missing_documents = self._identify_missing_documents(person, criteria)
        
        # Montant bénéfice estimé
        estimated_benefit = self._calculate_estimated_benefit(person, criteria)
        
        return {
            'eligibility_score': Decimal(str(round(final_score, 2))),
            'recommendation_level': recommendation_level,
            'processing_priority': processing_priority,
            'criteria_met': criteria_met,
            'blocking_factors': blocking_factors,
            'missing_documents': missing_documents,
            'estimated_benefit_amount': estimated_benefit,
            'calculated_at': timezone.now()
        }

    def _check_age_criteria(
        self, 
        person: PersonIdentity, 
        criteria: Dict
    ) -> Tuple[bool, float]:
        """
        Vérifie critères d'âge
        
        Returns:
            Tuple[bool, float]: (éligible, score 0-20)
        """
        age = person.age or 0
        age_min = criteria.get('age_min', 0)
        age_max = criteria.get('age_max')
        
        if age_max:
            eligible = age_min <= age <= age_max
        else:
            eligible = age >= age_min
        
        score = 20.0 if eligible else 0.0
        
        return eligible, score

    def _check_vulnerability_criteria(
        self, 
        person: PersonIdentity, 
        criteria: Dict
    ) -> Tuple[bool, float]:
        """
        Vérifie critères vulnérabilité
        
        Returns:
            Tuple[bool, float]: (éligible, score 0-100)
        """
        try:
            # Récupérer dernière évaluation vulnérabilité
            assessment = VulnerabilityAssessment.objects.filter(
                person=person,
                is_active=True
            ).order_by('-assessment_date').first()
            
            if not assessment:
                # Pas d'évaluation = score neutre
                return True, 50.0
            
            vuln_score = float(assessment.global_score)
            threshold = criteria.get('vulnerability_threshold', 50)
            
            eligible = vuln_score >= threshold
            
            return eligible, vuln_score
            
        except Exception as e:
            logger.error(f"Erreur check vulnerability: {str(e)}")
            return True, 50.0

    def _check_profile_matching(
        self, 
        person: PersonIdentity, 
        criteria: Dict
    ) -> Tuple[bool, float, List[str]]:
        """
        Vérifie adéquation profil personne / programme
        
        Returns:
            Tuple[bool, float, List[str]]: (éligible, score 0-100, facteurs)
        """
        score = 0.0
        factors = []
        eligible = True
        
        household = person.household
        
        # 1. Genre (si préférence)
        gender_pref = criteria.get('gender_preference')
        if gender_pref:
            if person.gender == gender_pref:
                score += 20
            else:
                eligible = False
                factors.append(f"Genre requis: {gender_pref}")
        else:
            score += 10  # Pas de contrainte = bonus
        
        # 2. Enfants à charge
        if criteria.get('requires_children', False):
            min_children = criteria.get('min_children', 1)
            children_count = household.children_count if household else 0
            
            if children_count >= min_children:
                score += 30
            else:
                eligible = False
                factors.append(f"Nécessite au moins {min_children} enfant(s)")
        else:
            score += 15
        
        # 3. Conditions spéciales
        special_conditions = criteria.get('special_conditions', [])
        if special_conditions:
            conditions_met = self._check_special_conditions(person, special_conditions)
            if conditions_met:
                score += 30
            else:
                eligible = False
                factors.append("Conditions spéciales non remplies")
        else:
            score += 15
        
        # 4. Statut emploi (pour programmes formation/insertion)
        if criteria.get('program_type') == 'EMPLOYMENT':
            employment_status = household.primary_income_source if household else None
            if employment_status in ['UNEMPLOYED', 'INFORMAL']:
                score += 20
            elif employment_status:
                score += 10
        else:
            score += 10
        
        # 5. Chef de ménage vulnérable (bonus)
        if household and household.head_of_household_id == person.id:
            if person.gender == 'F' or (person.age and person.age >= 60):
                score += 15
        
        return eligible, min(score, 100.0), factors

    def _calculate_need_urgency(
        self, 
        person: PersonIdentity, 
        criteria: Dict
    ) -> float:
        """
        Calcule urgence du besoin (0-100)
        
        Seuils Gabon (FCFA/mois):
        - Extrême pauvreté: < 50,000 (survie minimale)
        - Pauvreté: < 100,000 (difficultés économiques)
        """
        urgency_score = 0.0
        
        household = person.household
        
        # 1. Niveau revenus
        if household and household.monthly_income:
            if household.monthly_income < 50000:  # Extrême pauvreté
                urgency_score += 40
            elif household.monthly_income < 100000:  # Pauvreté
                urgency_score += 25
        else:
            urgency_score += 20  # Absence info = urgence modérée
        
        # 2. Vulnérabilités aggravantes
        if person.has_disability:
            urgency_score += 15
        if person.has_chronic_illness:
            urgency_score += 10
        
        # 3. Situation familiale
        if household:
            if household.children_count and household.children_count >= 4:
                urgency_score += 15
            if household.elderly_count and household.elderly_count >= 1:
                urgency_score += 10
        
        # 4. Zone isolée
        if person.province in ['NYANGA', 'OGOOUE_LOLO', 'OGOOUE_IVINDO']:
            urgency_score += 10
        
        return min(urgency_score, 100.0)

    def _calculate_absorption_capacity(
        self, 
        person: PersonIdentity, 
        criteria: Dict
    ) -> float:
        """
        Calcule capacité absorption aide (0-100)
        Évite gaspillage ressources
        """
        capacity_score = 50.0  # Score de base
        
        # 1. Niveau éducation (capacité compréhension)
        education = person.education_level
        if education in ['UNIVERSITY', 'HIGHER']:
            capacity_score += 20
        elif education in ['SECONDARY', 'VOCATIONAL']:
            capacity_score += 10
        elif education == 'PRIMARY':
            capacity_score += 5
        
        # 2. Accès services (facilite utilisation aide)
        household = person.household
        if household and household.has_bank_account:
            capacity_score += 15
        
        # 3. Réseau social (soutien utilisation)
        if household and household.household_size and household.household_size > 1:
            capacity_score += 10
        
        # 4. Âge (capacité gestion)
        age = person.age or 30
        if 25 <= age <= 55:
            capacity_score += 15  # Âge productif optimal
        elif 18 <= age < 25 or 55 < age <= 65:
            capacity_score += 10
        
        return min(capacity_score, 100.0)

    def _check_special_conditions(
        self, 
        person: PersonIdentity, 
        conditions: List[str]
    ) -> bool:
        """Vérifie conditions spéciales du programme"""
        for condition in conditions:
            if condition == 'IS_DISABLED' and not person.has_disability:
                return False
            elif condition == 'IS_FEMALE' and person.gender != 'F':
                return False
            elif condition == 'IS_RURAL' and hasattr(person, 'residence_type'):
                if person.residence_type != 'RURAL':
                    return False
        return True

    def _determine_recommendation_level(
        self, 
        score: float, 
        blocking_factors: List[str]
    ) -> str:
        """Détermine niveau recommandation"""
        if blocking_factors:
            return 'NOT_ELIGIBLE'
        elif score >= 80:
            return 'HIGHLY_RECOMMENDED'
        elif score >= 60:
            return 'RECOMMENDED'
        elif score >= 40:
            return 'CONDITIONALLY_ELIGIBLE'
        else:
            return 'NOT_ELIGIBLE'

    def _determine_processing_priority(
        self, 
        score: float, 
        person: PersonIdentity,
        criteria: Dict
    ) -> str:
        """Détermine priorité traitement"""
        if score >= 80:
            return 'URGENT'
        elif score >= 65:
            # Vérifier urgence contextuelle
            household = person.household
            if household and household.monthly_income and household.monthly_income < 50000:
                return 'URGENT'
            return 'HIGH'
        elif score >= 50:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _identify_missing_documents(
        self, 
        person: PersonIdentity, 
        criteria: Dict
    ) -> List[str]:
        """Identifie documents manquants"""
        missing = []
        
        # Documents standards
        if not person.national_id_number:
            missing.append("Carte d'identité nationale")
        
        if not person.birth_certificate_number:
            missing.append("Acte de naissance")
        
        # Documents ménage
        household = person.household
        if not household:
            missing.append("Déclaration de composition ménage")
        
        # Documents revenus
        if criteria.get('program_type') in ['CASH_TRANSFER', 'SUBSIDY']:
            if not household or not household.monthly_income:
                missing.append("Justificatif de revenus")
        
        return missing

    def _calculate_estimated_benefit(
        self, 
        person: PersonIdentity, 
        criteria: Dict
    ) -> Optional[Decimal]:
        """Calcule montant bénéfice estimé"""
        base_amount = criteria.get('estimated_benefit_fcfa', 0)
        
        if not base_amount:
            return None
        
        # Ajustements selon taille ménage
        household = person.household
        if household and household.household_size:
            if household.household_size >= 6:
                base_amount *= 1.2  # +20%
            elif household.household_size >= 4:
                base_amount *= 1.1  # +10%
        
        return Decimal(str(round(base_amount, 2)))

    def _create_ineligible_result(
        self,
        score: float,
        criteria_met: Dict,
        blocking_factors: List[str],
        missing_documents: List[str]
    ) -> Dict:
        """Crée résultat d'inéligibilité"""
        return {
            'eligibility_score': Decimal(str(round(score, 2))),
            'recommendation_level': 'NOT_ELIGIBLE',
            'processing_priority': 'LOW',
            'criteria_met': criteria_met,
            'blocking_factors': blocking_factors,
            'missing_documents': missing_documents,
            'estimated_benefit_amount': None,
            'calculated_at': timezone.now()
        }

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
            processing_priority='LOW',
            criteria_met={'program_status': 'full_or_inactive'},
            blocking_factors=['Programme temporairement fermé ou budget épuisé'],
            missing_documents=[],
            estimated_benefit_amount=None
        )

    def _auto_enroll_beneficiary(
        self, 
        person: PersonIdentity, 
        program: SocialProgram,
        eligibility: SocialProgramEligibility
    ):
        """Inscription automatique si critères remplis"""
        try:
            # Vérifier capacité programme
            if program.can_accept_new_beneficiaries:
                # Mettre à jour statut
                eligibility.enrollment_status = 'AUTO_ENROLLED'
                eligibility.enrollment_date = timezone.now()
                eligibility.save(update_fields=['enrollment_status', 'enrollment_date'])
                
                # Incrémenter compteur bénéficiaires
                program.current_beneficiaries += 1
                program.save(update_fields=['current_beneficiaries'])
                
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
            logger.error(f"Erreur inscription auto {person.id} dans {program.code}: {str(e)}")

    def calculate_eligibility_for_all_programs(
        self, 
        person_id: int
    ) -> Dict[str, SocialProgramEligibility]:
        """
        Calcule éligibilité pour tous programmes actifs
        
        Args:
            person_id: ID de la personne
            
        Returns:
            Dict[str, SocialProgramEligibility]: Éligibilités par programme
        """
        try:
            self.refresh_programs_cache()
            
            eligibilities = {}
            
            for program_code in self.active_programs.keys():
                try:
                    eligibility = self.calculate_program_eligibility(
                        person_id=person_id,
                        program_code=program_code,
                        recalculate=False
                    )
                    eligibilities[program_code] = eligibility
                    
                except Exception as e:
                    logger.error(f"Erreur calcul éligibilité {program_code}: {str(e)}")
                    continue
            
            self.log_operation(
                'all_programs_eligibility_calculated',
                {
                    'person_id': person_id,
                    'programs_evaluated': len(eligibilities)
                }
            )
            
            return eligibilities
            
        except Exception as e:
            logger.error(f"Erreur calcul éligibilité tous programmes: {str(e)}")
            raise

    def get_recommended_programs(
        self, 
        person_id: int, 
        min_score: float = 60.0
    ) -> List[Dict]:
        """
        Récupère programmes recommandés pour une personne
        
        Args:
            person_id: ID de la personne
            min_score: Score minimum d'éligibilité
            
        Returns:
            List[Dict]: Programmes recommandés avec détails
        """
        try:
            # Calculer éligibilités
            eligibilities = self.calculate_eligibility_for_all_programs(person_id)
            
            # Filtrer et trier
            recommended = []
            
            for program_code, eligibility in eligibilities.items():
                if (float(eligibility.eligibility_score) >= min_score and
                    eligibility.recommendation_level in ['HIGHLY_RECOMMENDED', 'RECOMMENDED']):
                    
                    program = self.active_programs.get(program_code)
                    
                    recommended.append({
                        'program_code': program_code,
                        'program_name': program.name if program else program_code,
                        'program_type': program.program_type if program else None,
                        'eligibility_score': float(eligibility.eligibility_score),
                        'recommendation_level': eligibility.recommendation_level,
                        'processing_priority': eligibility.processing_priority,
                        'estimated_benefit': float(eligibility.estimated_benefit_amount) if eligibility.estimated_benefit_amount else None,
                        'duration_months': program.duration_months if program else None,
                        'blocking_factors': eligibility.blocking_factors,
                        'missing_documents': eligibility.missing_documents,
                        'can_enroll': program.can_accept_new_beneficiaries if program else False
                    })
            
            # Trier par score décroissant
            recommended.sort(key=lambda x: x['eligibility_score'], reverse=True)
            
            self.log_operation(
                'recommended_programs_retrieved',
                {
                    'person_id': person_id,
                    'programs_recommended': len(recommended)
                }
            )
            
            return recommended
            
        except Exception as e:
            logger.error(f"Erreur récupération programmes recommandés: {str(e)}")
            raise

    def bulk_calculate_eligibility(
        self,
        person_ids: List[int],
        program_code: str,
        batch_size: int = 50
    ) -> Dict:
        """
        Calcul éligibilité en masse pour un programme
        
        Args:
            person_ids: Liste IDs personnes
            program_code: Code du programme
            batch_size: Taille des lots
            
        Returns:
            Dict: Statistiques succès/erreurs
        """
        try:
            results = {
                'success': 0,
                'errors': 0,
                'highly_recommended': 0,
                'recommended': 0,
                'conditionally_eligible': 0,
                'not_eligible': 0,
                'details': []
            }
            
            persons = PersonIdentity.objects.filter(id__in=person_ids)
            total_persons = persons.count()
            
            self.log_operation(
                'bulk_eligibility_started',
                {
                    'total_persons': total_persons,
                    'program_code': program_code,
                    'batch_size': batch_size
                }
            )
            
            # Traitement par lots
            for i in range(0, total_persons, batch_size):
                batch_persons = persons[i:i + batch_size]
                
                for person in batch_persons:
                    try:
                        eligibility = self.calculate_program_eligibility(
                            person_id=person.id,
                            program_code=program_code,
                            recalculate=False
                        )
                        
                        results['success'] += 1
                        
                        # Comptage par niveau
                        if eligibility.recommendation_level == 'HIGHLY_RECOMMENDED':
                            results['highly_recommended'] += 1
                        elif eligibility.recommendation_level == 'RECOMMENDED':
                            results['recommended'] += 1
                        elif eligibility.recommendation_level == 'CONDITIONALLY_ELIGIBLE':
                            results['conditionally_eligible'] += 1
                        else:
                            results['not_eligible'] += 1
                        
                        results['details'].append({
                            'person_id': person.id,
                            'status': 'success',
                            'eligibility_score': float(eligibility.eligibility_score),
                            'recommendation_level': eligibility.recommendation_level
                        })
                        
                    except Exception as e:
                        results['errors'] += 1
                        results['details'].append({
                            'person_id': person.id,
                            'status': 'error',
                            'error': str(e)
                        })
                        logger.error(f"Erreur éligibilité personne {person.id}: {str(e)}")
            
            self.log_operation(
                'bulk_eligibility_completed',
                {
                    'total_processed': results['success'] + results['errors'],
                    'success': results['success'],
                    'errors': results['errors'],
                    'highly_recommended': results['highly_recommended']
                }
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur bulk eligibility: {str(e)}")
            raise

    def get_eligibility_statistics(
        self, 
        program_code: str = None,
        province: str = None
    ) -> Dict:
        """
        Génère statistiques éligibilité pour dashboards
        
        Args:
            program_code: Filtrer par programme (optionnel)
            province: Filtrer par province (optionnel)
            
        Returns:
            Dict: Statistiques complètes
        """
        try:
            queryset = SocialProgramEligibility.objects.all()
            
            # Filtres
            if program_code:
                queryset = queryset.filter(program_code=program_code)
            if province:
                queryset = queryset.filter(person__province=province)
            
            total_evaluations = queryset.count()
            
            if total_evaluations == 0:
                return {
                    'total_evaluations': 0,
                    'message': 'Aucune évaluation disponible'
                }
            
            # Distribution par niveau recommandation
            recommendation_dist = queryset.values('recommendation_level').annotate(
                count=Count('id')
            ).order_by('recommendation_level')
            
            # Scores moyens
            avg_scores = queryset.aggregate(
                avg_eligibility=Avg('eligibility_score')
            )
            
            # Distribution priorité traitement
            priority_dist = queryset.values('processing_priority').annotate(
                count=Count('id')
            ).order_by('processing_priority')
            
            # Top programmes demandés
            if not program_code:
                program_stats = queryset.values('program_code').annotate(
                    count=Count('id'),
                    avg_score=Avg('eligibility_score')
                ).order_by('-count')[:10]
            else:
                program_stats = []
            
            # Statistiques par province
            province_stats = queryset.values('person__province').annotate(
                count=Count('id'),
                avg_score=Avg('eligibility_score')
            ).order_by('-count')[:5]
            
            statistics = {
                'total_evaluations': total_evaluations,
                'recommendation_distribution': {
                    item['recommendation_level']: item['count']
                    for item in recommendation_dist
                },
                'average_eligibility_score': float(avg_scores['avg_eligibility'] or 0),
                'priority_distribution': {
                    item['processing_priority']: item['count']
                    for item in priority_dist
                },
                'top_programs': [
                    {
                        'program_code': item['program_code'],
                        'evaluations': item['count'],
                        'avg_score': float(item['avg_score'])
                    }
                    for item in program_stats
                ],
                'top_provinces': [
                    {
                        'province': item['person__province'],
                        'evaluations': item['count'],
                        'avg_score': float(item['avg_score'])
                    }
                    for item in province_stats
                ],
                'filters_applied': {
                    'program_code': program_code,
                    'province': province
                }
            }
            
            self.log_operation(
                'eligibility_statistics_generated',
                {'total_evaluations': total_evaluations}
            )
            
            return statistics
            
        except Exception as e:
            logger.error(f"Erreur génération statistiques: {str(e)}")
            raise

    def get_priority_beneficiaries(
        self,
        program_code: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Récupère bénéficiaires prioritaires pour un programme
        
        Args:
            program_code: Code du programme
            limit: Nombre maximum de résultats
            
        Returns:
            List[Dict]: Bénéficiaires prioritaires avec détails
        """
        try:
            eligibilities = SocialProgramEligibility.objects.filter(
                program_code=program_code,
                recommendation_level__in=['HIGHLY_RECOMMENDED', 'RECOMMENDED']
            ).select_related('person').order_by(
                '-eligibility_score',
                'calculated_at'
            )[:limit]
            
            beneficiaries = []
            
            for eligibility in eligibilities:
                person = eligibility.person
                
                beneficiaries.append({
                    'person_id': person.id,
                    'rsu_id': person.rsu_id,
                    'full_name': person.full_name,
                    'age': person.age,
                    'gender': person.gender,
                    'province': person.province,
                    'eligibility_score': float(eligibility.eligibility_score),
                    'recommendation_level': eligibility.recommendation_level,
                    'processing_priority': eligibility.processing_priority,
                    'estimated_benefit': float(eligibility.estimated_benefit_amount) if eligibility.estimated_benefit_amount else None,
                    'blocking_factors': eligibility.blocking_factors,
                    'missing_documents': eligibility.missing_documents,
                    'calculated_at': eligibility.calculated_at.isoformat()
                })
            
            self.log_operation(
                'priority_beneficiaries_retrieved',
                {
                    'program_code': program_code,
                    'count': len(beneficiaries)
                }
            )
            
            return beneficiaries
            
        except Exception as e:
            logger.error(f"Erreur récupération bénéficiaires prioritaires: {str(e)}")
            raise

    def get_all_active_programs(self) -> Dict[str, Dict]:
        """Retourne tous les programmes actifs configurés"""
        self.refresh_programs_cache()
        
        programs_info = {}
        for code, program in self.active_programs.items():
            programs_info[code] = {
                'code': program.code,
                'name': program.name,
                'program_type': program.program_type,
                'benefit_amount': float(program.benefit_amount_fcfa),
                'duration_months': program.duration_months,
                'current_beneficiaries': program.current_beneficiaries,
                'max_beneficiaries': program.max_beneficiaries,
                'can_accept_new': program.can_accept_new_beneficiaries,
                'budget_available': program.is_budget_available,
                'target_provinces': program.target_provinces or [],
                'eligibility_criteria': program.eligibility_criteria
            }
        
        return programs_info

    def match_person_to_best_program(
        self, 
        person_id: int
    ) -> Optional[Dict]:
        """
        Trouve le meilleur programme pour une personne
        
        Args:
            person_id: ID de la personne
            
        Returns:
            Dict: Meilleur programme avec détails ou None
        """
        try:
            recommended = self.get_recommended_programs(person_id, min_score=40.0)
            
            if not recommended:
                return None
            
            # Retourner le programme avec le meilleur score
            best_match = recommended[0]
            
            self.log_operation(
                'best_program_matched',
                {
                    'person_id': person_id,
                    'program_code': best_match['program_code'],
                    'eligibility_score': best_match['eligibility_score']
                }
            )
            
            return best_match
            
        except Exception as e:
            logger.error(f"Erreur matching meilleur programme: {str(e)}")
            raise