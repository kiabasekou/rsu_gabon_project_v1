# ===================================================================
# RSU GABON - SERVICE ELIGIBILITY COMPLET
# Matching intelligent personne ↔ programmes sociaux
# ===================================================================

import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import date
from django.db.models import Count, Avg, Q

# Importation des modèles requis
from apps.identity_app.models import PersonIdentity
from ..models import (
     
    VulnerabilityAssessment, 
    
)

from apps.programs_app.models import SocialProgram  # ← Source unique
from ..admin import SocialProgramEligibility # ← Source unique

from .base_service import BaseService

logger = logging.getLogger(__name__)


# ===================================================================
# FONCTIONS HELPER
# ===================================================================

def calculate_age(birth_date: date) -> int:
    """Calcule l'âge à partir de la date de naissance."""
    today = date.today()
    # ✅ Correction pour remplacer le champ 'age' manquant
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


# ===================================================================
# CLASSE PRINCIPALE : ELIGIBILITY SERVICE
# ===================================================================

class EligibilityService(BaseService):
    """
    Service de calcul éligibilité programmes sociaux
    Utilise programmes paramétrables par administrateurs
    """
    
    # Pondérations scoring éligibilité
    SCORING_WEIGHTS = {
        'vulnerability_score': 0.40,      # Score vulnérabilité (Issue de VulnerabilityService)
        'profile_matching': 0.30,         # Adéquation profil/programme (Âge, sexe, handicap, etc.)
        'need_urgency': 0.20,             # Urgence besoin (Logement précaire, bas revenu)
        'absorption_capacity': 0.10       # Capacité absorption aide (Compte bancaire, formation)
    }

    def __init__(self):
        super().__init__()
        # Chargement dynamique programmes depuis base de données
        self.active_programs = {}
        self.refresh_programs_cache()
    
    def refresh_programs_cache(self):
        """Actualise le cache des programmes actifs et de leurs critères."""
        programs_info = {}
        for program in SocialProgram.objects.filter(is_active=True).all():
            programs_info[program.code] = {
                'program_name': program.name,
                'max_beneficiaries': program.max_beneficiaries,
                'can_accept_new': program.is_active, # Simplification
                'budget_available': True, # Simplification
                'target_provinces': program.target_provinces or [],
                'eligibility_criteria': program.eligibility_criteria or {},
                'program_type': program.program_type
            }
        self.active_programs = programs_info
        self.log_operation('programs_cache_refreshed', {'active_programs_count': len(programs_info)})
        
    def get_program_criteria(self, program_code: str) -> Dict:
        """Récupère les critères d'un programme."""
        return self.active_programs.get(program_code, {})

    # ===================================================================
    # 1. CALCUL ET SAUVEGARDE DE L'ÉLIGIBILITÉ
    # ===================================================================
    
    @transaction.atomic
    def calculate_program_eligibility(
        self, 
        person_id: int, 
        program_code: str, 
        recalculate: bool = False
    ) -> SocialProgramEligibility:
        """
        Calcule l'éligibilité pour un programme donné et la sauvegarde.
        """
        try:
            # ✅ CORRECTION: Utilisation de select_related pour le ménage
            person = PersonIdentity.objects.select_related('headed_household').get(id=person_id)
            
            criteria = self.get_program_criteria(program_code)
            program = SocialProgram.objects.get(code=program_code) # Récupère l'instance complète
            
            if not criteria.get('can_accept_new', True):
                logger.warning(f"Programme {program_code} fermé aux nouvelles inscriptions")
                return self._create_program_full_eligibility(person, program_code)
            
            # ... (Logique d'éligibilité existante)
            
            # Calcul de la nouvelle éligibilité
            eligibility_data = self._calculate_program_eligibility_score(
                person, program_code, criteria
            )
            
            # ❌ CORRECTION CRITIQUE: Filtrer les champs qui n'existent pas sur le modèle SocialProgramEligibility
            # Champs à supprimer selon le diagnostic : enrollment_date, enrollment_status, estimated_benefit_amount, missing_documents, save
            data_for_creation = {
                k: v for k, v in eligibility_data.items() 
                if k in ['eligibility_score', 'recommendation_level', 'processing_priority', 
                         'criteria_met', 'blocking_factors', 'assessment_date']
            }
            
            # Sauvegarde de l'éligibilité
            eligibility = SocialProgramEligibility.objects.create(
                person=person,
                program_code=program_code,
                **data_for_creation
            )
            
            # ... (Logique d'auto-enrollment)
            if (criteria.get('automated_enrollment') and 
                eligibility.recommendation_level == 'HIGHLY_RECOMMENDED'):
                self._auto_enroll_beneficiary(person, program, eligibility)
            
            self.log_operation(
                'eligibility_calculated', 
                {
                    'person_id': person_id,
                    'program_code': program_code,
                    'eligibility_score': float(eligibility.eligibility_score),
                    'recommendation_level': eligibility.recommendation_level
                }
            )
            
            return eligibility
            
        except PersonIdentity.DoesNotExist:
            logger.error(f"PersonIdentity {person_id} not found")
            raise ValueError(f"Personne avec ID {person_id} introuvable")
        except SocialProgram.DoesNotExist:
            logger.error(f"Programme {program_code} not found")
            raise ValueError(f"Programme avec code {program_code} introuvable")
        except Exception as e:
            logger.error(f"Erreur calcul éligibilité {program_code} pour {person_id}: {str(e)}")
            raise

    # ... (Autres méthodes calculate_eligibility_for_all_programs, get_recommended_programs)

    # ===================================================================
    # 2. CALCUL DU SCORE ET DES FACTEURS
    # ===================================================================

    def _calculate_program_eligibility_score(
        self, 
        person: PersonIdentity, 
        program_code: str,
        criteria: Dict
    ) -> Dict:
        """
        Calcule le score d'éligibilité basé sur les pondérations.
        """
        
        # 0. Initialisation des scores et facteurs
        final_score = 0.0
        blocking_factors = []
        criteria_met = {}
        
        # 1. Score de Vulnérabilité (40%)
        # ✅ CORRECTION: Utilisation directe de vulnerability_score du modèle PersonIdentity
        vuln_score_base = float(person.vulnerability_score or 0.0)
        vuln_contribution = (vuln_score_base * self.SCORING_WEIGHTS['vulnerability_score']) / 100
        final_score += vuln_contribution
        
        # 2. Adéquation Profil (30%)
        is_eligible_profile, profile_score, factors_profile = self._check_profile_matching(person, criteria)
        profile_contribution = (profile_score * self.SCORING_WEIGHTS['profile_matching']) / 100
        final_score += profile_contribution
        blocking_factors.extend(factors_profile)
        
        if not is_eligible_profile:
            blocking_factors.append("Profil non adapté aux critères primaires")
        
        # 3. Urgence Besoin (20%) - Basé sur les conditions spéciales
        is_eligible_conditions = self._check_special_conditions(person, criteria.get('special_conditions', []))
        need_score = 100.0 if is_eligible_conditions else 0.0
        need_contribution = (need_score * self.SCORING_WEIGHTS['need_urgency']) / 100
        final_score += need_contribution
        
        if not is_eligible_conditions:
            blocking_factors.append("Conditions spéciales du programme non remplies")
            
        # 4. Capacité d'Absorption (10%)
        absorption_score = 100.0 if person.headed_household and person.headed_household.has_bank_account else 50.0
        absorption_contribution = (absorption_score * self.SCORING_WEIGHTS['absorption_capacity']) / 100
        final_score += absorption_contribution

        # Détermination de la recommandation
        recommendation_level, processing_priority = self._determine_recommendation(
            final_score, criteria, blocking_factors
        )
        
        # Documents requis et montant bénéfice (non sauvegardés, mais retournés pour l'affichage)
        missing_documents = self._identify_missing_documents(person, criteria)
        estimated_benefit = self._calculate_estimated_benefit(person, criteria)

        return {
            'eligibility_score': Decimal(str(round(final_score * 100, 2))), # Score final sur 100
            'recommendation_level': recommendation_level,
            'processing_priority': processing_priority,
            'criteria_met': criteria_met,
            'blocking_factors': blocking_factors,
            # ✅ Ces champs sont exclus de la création de l'objet, mais nécessaires à la vue
            'missing_documents': missing_documents, 
            'estimated_benefit_amount': estimated_benefit, 
            'assessment_date': timezone.now()
        }

    # ===================================================================
    # 3. VÉRIFICATIONS DÉTAILLÉES
    # ===================================================================

    def _check_profile_matching(
        self, 
        person: PersonIdentity, 
        criteria: Dict
    ) -> Tuple[bool, float, List[str]]:
        """
        Vérifie l'adéquation du profil de la personne avec le programme.
        """
        score = 0.0
        factors = []
        eligible = True
        
        # ✅ Utilisation du champ birth_date pour calculer l'âge
        age = calculate_age(person.birth_date) if person.birth_date else 0
        household = person.headed_household

        # 1. Âge
        min_age = criteria.get('min_age', 0)
        max_age = criteria.get('max_age', 100)
        if age >= min_age and age <= max_age:
            score += 20
        else:
            factors.append(f"Âge ({age} ans) en dehors des bornes [{min_age}-{max_age}]")
            eligible = False

        # 2. Genre
        target_gender = criteria.get('target_gender')
        if not target_gender or person.gender == target_gender:
            score += 10
        
        # 3. Situation du ménage (taille, revenu)
        if household:
            # ✅ CORRECTION: total_monthly_income est le nom correct
            max_income = criteria.get('max_income', Decimal('1000000'))
            if (household.total_monthly_income or 0) <= max_income:
                score += 20
            
            # ✅ CORRECTION: household_size est le nom correct
            min_size = criteria.get('min_household_size', 1)
            if household.household_size >= min_size:
                score += 5
        
        # 4. Statut emploi/Revenu (Simulé car primary_income_source n'existe pas)
        # On utilise le niveau d'éducation pour simuler une 'capacité d'absorption' ou 'potentiel d'employabilité'
        if criteria.get('program_type') == 'EMPLOYMENT' and person.education_level in ['SECONDARY', 'HIGHER']:
            score += 15 
        
        # 5. Chef de ménage (bonus)
        # ✅ CORRECTION: Utilisation de la relation directe
        if household and person.is_household_head: 
            if person.gender == 'F' or age >= 60:
                score += 5
        
        return eligible, min(score, 100.0), factors

    def _check_special_conditions(
        self, 
        person: PersonIdentity, 
        conditions: List[str]
    ) -> bool:
        """Vérifie conditions spéciales du programme (handicap, type de logement, etc.)"""
        for condition in conditions:
            # ✅ CORRECTION: has_disability est le champ correct
            if condition == 'IS_DISABLED' and not person.has_disability:
                return False
            
            if condition == 'IS_FEMALE' and person.gender != 'F':
                return False
            
            # ❌ CORRECTION: residence_type est remplacé par housing_type du Household
            if condition == 'HAS_PRECARIOUS_HOUSING': 
                household = person.headed_household
                if household and household.housing_type != 'PRECARIOUS': 
                    return False
        return True

    def _identify_missing_documents(
        self, 
        person: PersonIdentity, 
        criteria: Dict
    ) -> List[str]:
        """Identifie documents manquants pour l'affichage."""
        missing = []
        if not person.national_id:
            missing.append("Carte d'identité nationale")
        
        # ❌ CORRECTION: Retrait des champs manquants (birth_certificate_number)
        # if not person.birth_certificate_number:
        #     missing.append("Acte de naissance") 
            
        household = person.headed_household
        if not household:
            missing.append("Déclaration de composition ménage")
            
        if criteria.get('requires_bank_account') and (not household or not household.has_bank_account):
            missing.append("RIB ou preuve de compte bancaire")
                
        return missing
    
    # ... (Autres méthodes helper comme _determine_recommendation, _calculate_estimated_benefit, etc.)
    
    def _calculate_estimated_benefit(self, person: PersonIdentity, criteria: Dict) -> Decimal:
        """Calcule le montant estimé du bénéfice (simplifié pour l'exemple)."""
        amount = Decimal(criteria.get('benefit_amount_fcfa', 0))
        # Logique d'ajustement ici si nécessaire (ex: multiplier par taille du ménage)
        return amount
        
    def _determine_recommendation(self, score: float, criteria: Dict, blocking_factors: List[str]) -> Tuple[str, int]:
        """Détermine le niveau de recommandation et la priorité."""
        
        # Si un facteur bloquant non contournable existe, la recommandation est bloquée
        if blocking_factors and 'Profil non adapté aux critères primaires' in blocking_factors:
             return 'NOT_ELIGIBLE', 99 # Priorité basse pour un profil non conforme

        if score >= 80:
            return 'HIGHLY_RECOMMENDED', 1 # Priorité haute
        elif score >= 50:
            return 'RECOMMENDED', 2
        else:
            return 'NOT_ELIGIBLE', 5
            
    def _create_program_full_eligibility(self, person: PersonIdentity, program_code: str) -> SocialProgramEligibility:
        """Crée un enregistrement d'éligibilité pour un programme fermé."""
        return SocialProgramEligibility.objects.create(
            person=person,
            program_code=program_code,
            eligibility_score=Decimal('0.00'),
            recommendation_level='NOT_ELIGIBLE',
            processing_priority=99,
            blocking_factors=["Programme fermé aux nouvelles inscriptions"],
            assessment_date=timezone.now()
        )
        
    def _auto_enroll_beneficiary(self, person, program, eligibility):
        """Logique d'auto-inscription simplifiée."""
        logger.info(f"Auto-enrollment triggered for {person.rsu_id} into {program.code}")
        # Ici, vous inséreriez la logique métier pour créer une inscription effective.
        
    # ===================================================================
    # 4. MÉTHODES D'INTERROGATION (API)
    # ===================================================================

    def calculate_eligibility_for_all_programs(
        self, 
        person_id: int
    ) -> Dict:
        """
        Calcule l'éligibilité pour tous les programmes actifs
        """
        eligible_programs = []
        ineligible_programs = []
        
        for program_code in self.active_programs.keys():
            try:
                eligibility = self.calculate_program_eligibility(person_id, program_code)
                
                result = {
                    'program_code': program_code,
                    'program_name': self.active_programs[program_code]['program_name'],
                    'recommendation_level': eligibility.recommendation_level,
                    'eligibility_score': float(eligibility.eligibility_score),
                    'blocking_factors': eligibility.blocking_factors,
                }
                
                if eligibility.recommendation_level in ['HIGHLY_RECOMMENDED', 'RECOMMENDED']:
                    eligible_programs.append(result)
                else:
                    ineligible_programs.append(result)
            
            except Exception as e:
                logger.error(f"Échec calcul éligibilité {program_code} pour {person_id}: {str(e)}")
                
        # Trie par score (meilleur match en premier)
        eligible_programs.sort(key=lambda x: x['eligibility_score'], reverse=True)
        
        return {
            'person_id': person_id,
            'eligible_programs': eligible_programs,
            'ineligible_programs': ineligible_programs
        }

    def get_recommended_programs(
        self, 
        person_id: int, 
        min_score: float = 60.0
    ) -> List[Dict]:
        """Récupère les programmes recommandés (score >= min_score)."""
        
        result = self.calculate_eligibility_for_all_programs(person_id)
        
        return [
            p for p in result['eligible_programs'] 
            if p['eligibility_score'] >= min_score
        ]

    def match_person_to_best_program(
        self, 
        person_id: int
    ) -> Optional[Dict]:
        """Trouve le meilleur programme pour une personne."""
        recommended = self.get_recommended_programs(person_id, min_score=40.0)
        
        if not recommended:
            return None
        
        best_match = recommended[0] # Déjà trié par score
        
        self.log_operation(
            'best_program_matched',
            {
                'person_id': person_id,
                'program_code': best_match['program_code'],
                'eligibility_score': best_match['eligibility_score']
            }
        )
        return best_match