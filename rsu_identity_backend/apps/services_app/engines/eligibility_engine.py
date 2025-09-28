# ===================================================================
# 🇬🇦 RSU GABON - MOTEUR ÉLIGIBILITÉ PROGRAMMES SOCIAUX
# Standards Top 1% - Optimisation IA Allocation Ressources
# ===================================================================

import logging
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# ===================================================================
# CONFIGURATION ET CONSTANTES
# ===================================================================

class RecommendationStatus(Enum):
    HIGHLY_RECOMMENDED = "HIGHLY_RECOMMENDED"
    RECOMMENDED = "RECOMMENDED"
    CONDITIONAL = "CONDITIONAL"
    NOT_RECOMMENDED = "NOT_RECOMMENDED"
    INELIGIBLE = "INELIGIBLE"

class InterventionUrgency(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class ProgramCriteria:
    """Critères d'éligibilité pour un programme social"""
    code: str
    name: str
    economic_score_min: Optional[float] = None
    social_score_min: Optional[float] = None
    demographic_score_min: Optional[float] = None
    geographic_score_min: Optional[float] = None
    vulnerability_levels: List[str] = None
    age_range: Tuple[int, int] = None
    geographic_zones: List[str] = None
    special_conditions: Dict = None
    annual_budget: Decimal = Decimal('0')
    max_beneficiaries: int = 0
    cost_per_beneficiary: Decimal = Decimal('0')

@dataclass
class EligibilityResult:
    """Résultat évaluation éligibilité pour un programme"""
    program_code: str
    program_name: str
    eligibility_score: float
    compatibility_score: float
    recommendation_status: RecommendationStatus
    intervention_urgency: InterventionUrgency
    estimated_monthly_benefit: Decimal
    processing_priority: int
    eligibility_factors: List[str]
    blocking_factors: List[str]
    required_documents: List[str]
    estimated_impact: str

# ===================================================================
# MOTEUR PRINCIPAL ÉLIGIBILITÉ
# ===================================================================

class GabonSocialProgramEligibilityEngine:
    """
    Moteur IA d'éligibilité aux programmes sociaux du Gabon
    Utilise les scores de vulnérabilité pour optimiser l'allocation
    """
    
    # Configuration programmes sociaux Gabon
    PROGRAMS_CATALOG = {
        'TM_001': ProgramCriteria(
            code='TM_001',
            name='Transferts Monétaires',
            economic_score_min=35.0,
            vulnerability_levels=['CRITICAL', 'HIGH'],
            annual_budget=Decimal('45000000'),
            max_beneficiaries=15000,
            cost_per_beneficiary=Decimal('75000'),
            special_conditions={
                'household_income_max': 150000,
                'employment_status': ['unemployed', 'informal'],
                'required_documents': ['identity_card', 'poverty_certificate']
            }
        ),
        'NM_002': ProgramCriteria(
            code='NM_002',
            name='Nutrition Maternelle',
            social_score_min=25.0,
            age_range=(15, 45),
            annual_budget=Decimal('25000000'),
            max_beneficiaries=8000,
            cost_per_beneficiary=Decimal('50000'),
            special_conditions={
                'gender': 'female',
                'pregnancy_status': True,
                'children_under_5': True,
                'health_access_limited': True
            }
        ),
        'DR_003': ProgramCriteria(
            code='DR_003',
            name='Développement Rural',
            geographic_score_min=30.0,
            geographic_zones=['RURAL_REMOTE', 'RURAL_ISOLATED'],
            annual_budget=Decimal('60000000'),
            max_beneficiaries=20000,
            cost_per_beneficiary=Decimal('100000'),
            special_conditions={
                'economic_activity': 'agriculture',
                'land_ownership': True
            }
        ),
        'FP_004': ProgramCriteria(
            code='FP_004',
            name='Formation Professionnelle',
            age_range=(18, 35),
            economic_score_min=25.0,
            annual_budget=Decimal('30000000'),
            max_beneficiaries=5000,
            cost_per_beneficiary=Decimal('200000'),
            special_conditions={
                'education_level': ['primary', 'secondary'],
                'employment_status': ['unemployed']
            }
        ),
        'SS_005': ProgramCriteria(
            code='SS_005',
            name='Soins Santé Gratuits',
            social_score_min=30.0,
            annual_budget=Decimal('80000000'),
            max_beneficiaries=40000,
            cost_per_beneficiary=Decimal('60000'),
            special_conditions={
                'has_health_insurance': False,
                'chronic_illness': True
            }
        ),
        'BE_006': ProgramCriteria(
            code='BE_006',
            name='Bourses Éducation',
            age_range=(6, 25),
            economic_score_min=40.0,
            annual_budget=Decimal('40000000'),
            max_beneficiaries=10000,
            cost_per_beneficiary=Decimal('120000'),
            special_conditions={
                'school_enrollment': True,
                'academic_performance': 'acceptable'
            }
        ),
        'AH_007': ProgramCriteria(
            code='AH_007',
            name='Appui Personnes Handicapées',
            annual_budget=Decimal('20000000'),
            max_beneficiaries=3000,
            cost_per_beneficiary=Decimal('150000'),
            special_conditions={
                'disability_status': True,
                'disability_certificate': True
            }
        ),
        'AU_008': ProgramCriteria(
            code='AU_008',
            name='Aide d\'Urgence',
            vulnerability_levels=['CRITICAL'],
            annual_budget=Decimal('35000000'),
            max_beneficiaries=7000,
            cost_per_beneficiary=Decimal('100000'),
            special_conditions={
                'emergency_situation': True,
                'immediate_need': True
            }
        )
    }
    
    def __init__(self):
        """Initialisation du moteur d'éligibilité"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("🇬🇦 Initialisation Moteur Éligibilité Programmes Sociaux")
    
    def calculate_eligibility_assessment(self, person_data: Dict, 
                                       vulnerability_assessment: Dict) -> Dict[str, EligibilityResult]:
        """
        Calcul complet éligibilité pour tous les programmes
        
        Args:
            person_data: Données complètes de la personne
            vulnerability_assessment: Résultats scoring vulnérabilité
            
        Returns:
            Dict[program_code, EligibilityResult]: Résultats par programme
        """
        try:
            eligibility_results = {}
            
            for program_code, criteria in self.PROGRAMS_CATALOG.items():
                result = self._evaluate_program_eligibility(
                    person_data, vulnerability_assessment, criteria
                )
                eligibility_results[program_code] = result
            
            # Optimisation priorités globales
            self._optimize_program_priorities(eligibility_results)
            
            self.logger.info(f"✅ Éligibilité calculée pour {len(eligibility_results)} programmes")
            return eligibility_results
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul éligibilité: {e}")
            raise
    
    def _evaluate_program_eligibility(self, person_data: Dict, 
                                    vulnerability_assessment: Dict,
                                    criteria: ProgramCriteria) -> EligibilityResult:
        """Évaluation éligibilité pour un programme spécifique"""
        
        # 1. Scores de vulnérabilité
        dimension_scores = vulnerability_assessment.get('dimension_scores', {})
        global_score = vulnerability_assessment.get('global_score', 0)
        vulnerability_level = vulnerability_assessment.get('vulnerability_level', 'LOW')
        
        # 2. Vérification critères de base
        eligibility_score = 0.0
        eligibility_factors = []
        blocking_factors = []
        
        # Critères scores de vulnérabilité
        if criteria.economic_score_min and dimension_scores.get('economic', {}).get('score', 0) >= criteria.economic_score_min:
            eligibility_score += 25
            eligibility_factors.append(f"Score économique: {dimension_scores.get('economic', {}).get('score', 0):.1f}")
        elif criteria.economic_score_min:
            blocking_factors.append(f"Score économique insuffisant (<{criteria.economic_score_min})")
        
        if criteria.social_score_min and dimension_scores.get('social', {}).get('score', 0) >= criteria.social_score_min:
            eligibility_score += 25
            eligibility_factors.append(f"Score social: {dimension_scores.get('social', {}).get('score', 0):.1f}")
        elif criteria.social_score_min:
            blocking_factors.append(f"Score social insuffisant (<{criteria.social_score_min})")
        
        if criteria.geographic_score_min and dimension_scores.get('geographic', {}).get('score', 0) >= criteria.geographic_score_min:
            eligibility_score += 20
            eligibility_factors.append(f"Score géographique: {dimension_scores.get('geographic', {}).get('score', 0):.1f}")
        elif criteria.geographic_score_min:
            blocking_factors.append(f"Score géographique insuffisant (<{criteria.geographic_score_min})")
        
        # Niveau de vulnérabilité
        if criteria.vulnerability_levels and vulnerability_level in criteria.vulnerability_levels:
            eligibility_score += 30
            eligibility_factors.append(f"Niveau vulnérabilité: {vulnerability_level}")
        elif criteria.vulnerability_levels:
            blocking_factors.append(f"Niveau vulnérabilité non éligible: {vulnerability_level}")
        
        # 3. Critères démographiques
        person_age = person_data.get('age', 0)
        if criteria.age_range:
            min_age, max_age = criteria.age_range
            if min_age <= person_age <= max_age:
                eligibility_score += 15
                eligibility_factors.append(f"Âge éligible: {person_age} ans")
            else:
                blocking_factors.append(f"Âge non éligible: {person_age} ans")
        
        # 4. Critères spéciaux
        if criteria.special_conditions:
            special_score = self._evaluate_special_conditions(
                person_data, criteria.special_conditions
            )
            eligibility_score += special_score
        
        # 5. Calcul score compatibilité
        compatibility_score = self._calculate_compatibility_score(
            person_data, vulnerability_assessment, criteria
        )
        
        # 6. Détermination statut recommandation
        recommendation_status = self._determine_recommendation_status(
            eligibility_score, compatibility_score, blocking_factors
        )
        
        # 7. Urgence intervention
        intervention_urgency = self._calculate_intervention_urgency(
            vulnerability_assessment, criteria
        )
        
        # 8. Estimation bénéfice
        estimated_benefit = self._estimate_monthly_benefit(criteria, person_data)
        
        # 9. Impact estimé
        estimated_impact = self._estimate_program_impact(
            vulnerability_assessment, criteria
        )
        
        # 10. Documents requis
        required_documents = self._get_required_documents(criteria)
        
        return EligibilityResult(
            program_code=criteria.code,
            program_name=criteria.name,
            eligibility_score=round(eligibility_score, 2),
            compatibility_score=round(compatibility_score, 2),
            recommendation_status=recommendation_status,
            intervention_urgency=intervention_urgency,
            estimated_monthly_benefit=estimated_benefit,
            processing_priority=0,  # Sera calculé dans optimize_priorities
            eligibility_factors=eligibility_factors,
            blocking_factors=blocking_factors,
            required_documents=required_documents,
            estimated_impact=estimated_impact
        )
    
    def _evaluate_special_conditions(self, person_data: Dict, 
                                   special_conditions: Dict) -> float:
        """Évaluation critères spéciaux du programme"""
        score = 0.0
        
        # Revenu maximum
        if 'household_income_max' in special_conditions:
            monthly_income = person_data.get('monthly_income', 0)
            if monthly_income <= special_conditions['household_income_max']:
                score += 10
        
        # Statut emploi
        if 'employment_status' in special_conditions:
            employment_status = person_data.get('employment_status', '')
            if employment_status in special_conditions['employment_status']:
                score += 10
        
        # Genre
        if 'gender' in special_conditions:
            if person_data.get('gender') == special_conditions['gender']:
                score += 5
        
        # Statut grossesse
        if 'pregnancy_status' in special_conditions:
            if person_data.get('is_pregnant') == special_conditions['pregnancy_status']:
                score += 15
        
        # Enfants de moins de 5 ans
        if 'children_under_5' in special_conditions:
            if person_data.get('has_children_under_5') == special_conditions['children_under_5']:
                score += 10
        
        # Handicap
        if 'disability_status' in special_conditions:
            if person_data.get('has_disability') == special_conditions['disability_status']:
                score += 20
        
        # Situation d'urgence
        if 'emergency_situation' in special_conditions:
            if person_data.get('emergency_status') == special_conditions['emergency_situation']:
                score += 25
        
        return score
    
    def _calculate_compatibility_score(self, person_data: Dict,
                                     vulnerability_assessment: Dict,
                                     criteria: ProgramCriteria) -> float:
        """
        Score de compatibilité personne-programme
        Combine éligibilité + urgence + impact potentiel
        """
        
        # Facteur urgence basé sur vulnérabilité
        global_score = vulnerability_assessment.get('global_score', 0)
        urgency_factor = min(global_score / 100, 1.0)
        
        # Facteur impact basé sur ciblage programme
        impact_factor = self._calculate_impact_factor(person_data, criteria)
        
        # Facteur ressources disponibles
        resource_factor = self._calculate_resource_availability_factor(criteria)
        
        # Score composite
        compatibility_score = (
            urgency_factor * 40 +
            impact_factor * 35 +
            resource_factor * 25
        ) * 100
        
        return min(compatibility_score, 100.0)
    
    def _calculate_impact_factor(self, person_data: Dict, 
                               criteria: ProgramCriteria) -> float:
        """Calcul facteur d'impact potentiel du programme"""
        impact_score = 0.5  # Base
        
        # Multiplicateur selon type de programme
        if 'transferts' in criteria.name.lower():
            # Impact élevé pour transferts monétaires
            if person_data.get('monthly_income', 0) < 100000:
                impact_score = 0.9
        elif 'nutrition' in criteria.name.lower():
            # Impact critique pour nutrition maternelle
            if person_data.get('is_pregnant') or person_data.get('has_children_under_5'):
                impact_score = 0.95
        elif 'formation' in criteria.name.lower():
            # Impact moyen-élevé formation selon âge
            age = person_data.get('age', 0)
            if 18 <= age <= 35:
                impact_score = 0.8
        elif 'santé' in criteria.name.lower():
            # Impact élevé soins santé selon besoins
            if not person_data.get('has_health_insurance', True):
                impact_score = 0.85
        
        return impact_score
    
    def _calculate_resource_availability_factor(self, criteria: ProgramCriteria) -> float:
        """Facteur disponibilité ressources du programme"""
        # Simulé - en production, connecté aux budgets réels
        if criteria.annual_budget > Decimal('50000000'):
            return 0.9  # Budget élevé
        elif criteria.annual_budget > Decimal('30000000'):
            return 0.7  # Budget moyen
        else:
            return 0.5  # Budget limité
    
    def _determine_recommendation_status(self, eligibility_score: float,
                                       compatibility_score: float,
                                       blocking_factors: List[str]) -> RecommendationStatus:
        """Détermine le statut de recommandation"""
        
        if blocking_factors:
            return RecommendationStatus.INELIGIBLE
        
        combined_score = (eligibility_score + compatibility_score) / 2
        
        if combined_score >= 80:
            return RecommendationStatus.HIGHLY_RECOMMENDED
        elif combined_score >= 60:
            return RecommendationStatus.RECOMMENDED
        elif combined_score >= 40:
            return RecommendationStatus.CONDITIONAL
        else:
            return RecommendationStatus.NOT_RECOMMENDED
    
    def _calculate_intervention_urgency(self, vulnerability_assessment: Dict,
                                      criteria: ProgramCriteria) -> InterventionUrgency:
        """Calcul urgence d'intervention"""
        
        vulnerability_level = vulnerability_assessment.get('vulnerability_level', 'LOW')
        global_score = vulnerability_assessment.get('global_score', 0)
        
        # Programmes d'urgence
        if criteria.code == 'AU_008':  # Aide d'urgence
            return InterventionUrgency.CRITICAL
        
        # Basé sur niveau vulnérabilité
        if vulnerability_level == 'CRITICAL':
            return InterventionUrgency.CRITICAL
        elif vulnerability_level == 'HIGH':
            return InterventionUrgency.HIGH
        elif vulnerability_level == 'MODERATE':
            return InterventionUrgency.MEDIUM
        else:
            return InterventionUrgency.LOW
    
    def _estimate_monthly_benefit(self, criteria: ProgramCriteria, 
                                person_data: Dict) -> Decimal:
        """Estimation bénéfice mensuel du programme"""
        
        if criteria.code == 'TM_001':  # Transferts monétaires
            # Calculé selon taille ménage et revenus
            household_size = person_data.get('household_size', 1)
            base_amount = Decimal('50000')  # Base 50k FCFA
            return base_amount + (Decimal('15000') * (household_size - 1))
        
        elif criteria.code == 'NM_002':  # Nutrition maternelle
            return Decimal('40000')  # Forfait nutrition
        
        elif criteria.code == 'DR_003':  # Développement rural
            return Decimal('75000')  # Appui agricole
        
        elif criteria.code == 'FP_004':  # Formation professionnelle
            return Decimal('0')  # Formation gratuite, pas de transfert
        
        elif criteria.code == 'SS_005':  # Soins santé gratuits
            return Decimal('30000')  # Équivalent couverture santé
        
        elif criteria.code == 'BE_006':  # Bourses éducation
            education_level = person_data.get('education_level', 'primary')
            if education_level == 'university':
                return Decimal('100000')
            elif education_level == 'secondary':
                return Decimal('60000')
            else:
                return Decimal('30000')
        
        elif criteria.code == 'AH_007':  # Appui handicapés
            return Decimal('80000')  # Allocation handicap
        
        elif criteria.code == 'AU_008':  # Aide d'urgence
            return Decimal('100000')  # Aide ponctuelle
        
        return Decimal('0')
    
    def _estimate_program_impact(self, vulnerability_assessment: Dict,
                               criteria: ProgramCriteria) -> str:
        """Estimation impact du programme"""
        
        global_score = vulnerability_assessment.get('global_score', 0)
        
        if global_score >= 75:
            if criteria.code in ['TM_001', 'AU_008', 'NM_002']:
                return "TRANSFORMATIONAL"
            else:
                return "SIGNIFICANT"
        elif global_score >= 50:
            return "SIGNIFICANT"
        elif global_score >= 25:
            return "MODERATE"
        else:
            return "LIMITED"
    
    def _get_required_documents(self, criteria: ProgramCriteria) -> List[str]:
        """Liste documents requis pour le programme"""
        
        base_documents = ['identity_card', 'residency_certificate']
        
        if criteria.special_conditions:
            conditions = criteria.special_conditions
            
            if 'poverty_certificate' in conditions.get('required_documents', []):
                base_documents.append('poverty_certificate')
            
            if conditions.get('pregnancy_status'):
                base_documents.append('medical_certificate_pregnancy')
            
            if conditions.get('disability_status'):
                base_documents.append('disability_certificate')
            
            if conditions.get('emergency_situation'):
                base_documents.append('emergency_declaration')
            
            if conditions.get('school_enrollment'):
                base_documents.append('school_enrollment_certificate')
        
        return base_documents
    
    def _optimize_program_priorities(self, eligibility_results: Dict[str, EligibilityResult]):
        """Optimisation priorités globales des programmes"""
        
        # Tri par score de compatibilité et urgence
        results_list = list(eligibility_results.values())
        results_list.sort(
            key=lambda x: (
                x.intervention_urgency.value == 'CRITICAL',
                x.intervention_urgency.value == 'HIGH',
                x.compatibility_score,
                x.eligibility_score
            ),
            reverse=True
        )
        
        # Attribution priorités
        for i, result in enumerate(results_list, 1):
            result.processing_priority = i

# ===================================================================
# OPTIMISEUR D'ALLOCATION RESSOURCES
# ===================================================================

class ResourceAllocationOptimizer:
    """
    Optimiseur allocation ressources avec contraintes budgétaires
    Implémente algorithme Weighted Maximum Coverage Problem
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def optimize_batch_allocation(self, persons_assessments: List[Dict],
                                budget_constraints: Dict,
                                optimization_objective: str = "maximize_coverage") -> Dict:
        """
        Optimisation allocation pour un groupe de personnes
        
        Args:
            persons_assessments: Liste évaluations éligibilité
            budget_constraints: Contraintes budgétaires par programme
            optimization_objective: Objectif d'optimisation
            
        Returns:
            Dict: Matrice allocation optimisée
        """
        
        try:
            allocation_matrix = {}
            total_budget_used = {}
            total_beneficiaries = {}
            
            # Initialisation budgets
            for program_code in GabonSocialProgramEligibilityEngine.PROGRAMS_CATALOG:
                total_budget_used[program_code] = Decimal('0')
                total_beneficiaries[program_code] = 0
            
            # Tri global par priorité
            all_candidates = []
            for person_assessment in persons_assessments:
                person_id = person_assessment['person_id']
                eligibility_results = person_assessment['eligibility_results']
                
                for program_code, result in eligibility_results.items():
                    if result.recommendation_status in [
                        RecommendationStatus.HIGHLY_RECOMMENDED,
                        RecommendationStatus.RECOMMENDED
                    ]:
                        all_candidates.append({
                            'person_id': person_id,
                            'program_code': program_code,
                            'result': result,
                            'priority_score': self._calculate_global_priority_score(result)
                        })
            
            # Tri par score priorité global
            all_candidates.sort(key=lambda x: x['priority_score'], reverse=True)
            
            # Allocation selon contraintes budgétaires
            for candidate in all_candidates:
                person_id = candidate['person_id']
                program_code = candidate['program_code']
                result = candidate['result']
                
                # Vérification contraintes budgétaires
                program_criteria = GabonSocialProgramEligibilityEngine.PROGRAMS_CATALOG[program_code]
                
                if (total_budget_used[program_code] + result.estimated_monthly_benefit * 12 
                    <= program_criteria.annual_budget and
                    total_beneficiaries[program_code] < program_criteria.max_beneficiaries):
                    
                    # Allocation approuvée
                    if person_id not in allocation_matrix:
                        allocation_matrix[person_id] = {}
                    
                    allocation_matrix[person_id][program_code] = {
                        'status': 'APPROVED',
                        'monthly_benefit': result.estimated_monthly_benefit,
                        'annual_cost': result.estimated_monthly_benefit * 12,
                        'priority_rank': result.processing_priority,
                        'approval_date': datetime.now().isoformat()
                    }
                    
                    total_budget_used[program_code] += result.estimated_monthly_benefit * 12
                    total_beneficiaries[program_code] += 1
            
            # Statistiques allocation
            allocation_stats = {
                'total_persons_evaluated': len(persons_assessments),
                'total_persons_allocated': len(allocation_matrix),
                'budget_utilization': {
                    program: {
                        'budget_used': float(total_budget_used[program]),
                        'budget_available': float(
                            GabonSocialProgramEligibilityEngine.PROGRAMS_CATALOG[program].annual_budget
                        ),
                        'utilization_rate': float(
                            total_budget_used[program] / 
                            GabonSocialProgramEligibilityEngine.PROGRAMS_CATALOG[program].annual_budget * 100
                        ),
                        'beneficiaries_count': total_beneficiaries[program]
                    }
                    for program in total_budget_used
                },
                'optimization_objective': optimization_objective,
                'allocation_date': datetime.now().isoformat()
            }
            
            return {
                'allocation_matrix': allocation_matrix,
                'allocation_statistics': allocation_stats,
                'total_allocated_budget': sum(float(b) for b in total_budget_used.values()),
                'coverage_rate': len(allocation_matrix) / len(persons_assessments) * 100
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur optimisation allocation: {e}")
            raise
    
    def _calculate_global_priority_score(self, result: EligibilityResult) -> float:
        """Calcul score priorité global pour optimisation"""
        
        urgency_weight = {
            InterventionUrgency.CRITICAL: 1.0,
            InterventionUrgency.HIGH: 0.8,
            InterventionUrgency.MEDIUM: 0.6,
            InterventionUrgency.LOW: 0.4
        }
        
        recommendation_weight = {
            RecommendationStatus.HIGHLY_RECOMMENDED: 1.0,
            RecommendationStatus.RECOMMENDED: 0.8,
            RecommendationStatus.CONDITIONAL: 0.5,
            RecommendationStatus.NOT_RECOMMENDED: 0.2,
            RecommendationStatus.INELIGIBLE: 0.0
        }
        
        impact_weight = {
            "TRANSFORMATIONAL": 1.0,
            "SIGNIFICANT": 0.8,
            "MODERATE": 0.6,
            "LIMITED": 0.4
        }
        
        priority_score = (
            result.compatibility_score * 0.3 +
            result.eligibility_score * 0.2 +
            urgency_weight[result.intervention_urgency] * 100 * 0.3 +
            recommendation_weight[result.recommendation_status] * 100 * 0.1 +
            impact_weight[result.estimated_impact] * 100 * 0.1
        )
        
        return priority_score

# ===================================================================
# GÉNÉRATEUR DE RECOMMANDATIONS INTELLIGENTES
# ===================================================================

class SocialInterventionRecommendationEngine:
    """
    Générateur recommandations d'intervention sociale intelligentes
    Analyse globale et suggestions d'actions prioritaires
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_global_recommendations(self, eligibility_results: Dict[str, EligibilityResult],
                                      person_data: Dict,
                                      vulnerability_assessment: Dict) -> Dict:
        """
        Génération recommandations globales d'intervention
        """
        
        # Analyse priorités
        high_priority_programs = [
            result for result in eligibility_results.values()
            if result.recommendation_status in [
                RecommendationStatus.HIGHLY_RECOMMENDED,
                RecommendationStatus.RECOMMENDED
            ]
        ]
        
        # Tri par urgence et impact
        high_priority_programs.sort(
            key=lambda x: (x.intervention_urgency.value == 'CRITICAL', x.compatibility_score),
            reverse=True
        )
        
        # Recommandations principales
        primary_recommendations = []
        if high_priority_programs:
            top_program = high_priority_programs[0]
            primary_recommendations.append(
                f"PRIORITÉ 1: {top_program.program_name} - Intervention {top_program.intervention_urgency.value.lower()}"
            )
        
        # Recommandations complémentaires
        complementary_recommendations = []
        
        # Analyse vulnérabilité multidimensionnelle
        dimension_scores = vulnerability_assessment.get('dimension_scores', {})
        
        if dimension_scores.get('economic', {}).get('score', 0) >= 40:
            complementary_recommendations.append("Suivi économique renforcé recommandé")
        
        if dimension_scores.get('social', {}).get('score', 0) >= 35:
            complementary_recommendations.append("Accompagnement social nécessaire")
        
        if dimension_scores.get('geographic', {}).get('score', 0) >= 35:
            complementary_recommendations.append("Programmes développement territorial prioritaires")
        
        # Recommandations préventives
        preventive_recommendations = []
        global_score = vulnerability_assessment.get('global_score', 0)
        
        if global_score >= 50:
            preventive_recommendations.append("Révision situation dans 3 mois")
            preventive_recommendations.append("Activation réseau de soutien communautaire")
        
        return {
            'primary_interventions': primary_recommendations,
            'complementary_actions': complementary_recommendations,
            'preventive_measures': preventive_recommendations,
            'total_recommended_programs': len(high_priority_programs),
            'estimated_total_monthly_benefit': sum(
                float(p.estimated_monthly_benefit) for p in high_priority_programs[:3]
            ),
            'next_evaluation_date': (datetime.now() + timedelta(days=90)).isoformat(),
            'case_complexity': self._assess_case_complexity(eligibility_results, vulnerability_assessment)
        }
    
    def _assess_case_complexity(self, eligibility_results: Dict[str, EligibilityResult],
                              vulnerability_assessment: Dict) -> str:
        """Évaluation complexité du cas social"""
        
        eligible_programs_count = len([
            r for r in eligibility_results.values()
            if r.recommendation_status != RecommendationStatus.INELIGIBLE
        ])
        
        global_score = vulnerability_assessment.get('global_score', 0)
        
        if global_score >= 75 and eligible_programs_count >= 4:
            return "TRÈS_COMPLEXE"
        elif global_score >= 50 and eligible_programs_count >= 3:
            return "COMPLEXE"
        elif global_score >= 25 and eligible_programs_count >= 2:
            return "MODÉRÉ"
        else:
            return "SIMPLE"

# ===================================================================
# TESTS ET VALIDATION
# ===================================================================

def test_eligibility_engine():
    """Test du moteur d'éligibilité avec cas réel"""
    
    # Données test - Femme enceinte en situation précaire
    test_person_data = {
        'age': 28,
        'gender': 'female',
        'monthly_income': 80000,  # Sous seuil pauvreté
        'employment_status': 'informal',
        'is_pregnant': True,
        'has_children_under_5': True,
        'household_size': 4,
        'education_level': 'primary',
        'has_health_insurance': False,
        'province': 'OGOOUE_IVINDO',
        'zone_type': 'RURAL_REMOTE',
        'has_disability': False,
        'emergency_status': False
    }
    
    # Assessment vulnérabilité simulé
    test_vulnerability_assessment = {
        'global_score': 68.5,
        'vulnerability_level': 'HIGH',
        'dimension_scores': {
            'economic': {'score': 55.0},
            'social': {'score': 40.0},
            'demographic': {'score': 45.0},
            'geographic': {'score': 50.0},
            'resilience': {'score': 30.0}
        }
    }
    
    # Test moteur
    engine = GabonSocialProgramEligibilityEngine()
    eligibility_results = engine.calculate_eligibility_assessment(
        test_person_data, test_vulnerability_assessment
    )
    
    # Affichage résultats
    print("🇬🇦 TEST MOTEUR ÉLIGIBILITÉ - PROGRAMMES SOCIAUX GABON")
    print("=" * 60)
    print(f"Profil: Femme {test_person_data['age']} ans, enceinte, {test_person_data['province']}")
    print(f"Score vulnérabilité: {test_vulnerability_assessment['global_score']}/100 ({test_vulnerability_assessment['vulnerability_level']})")
    print()
    
    print("📋 RÉSULTATS ÉLIGIBILITÉ PAR PROGRAMME:")
    for program_code, result in eligibility_results.items():
        if result.recommendation_status != RecommendationStatus.INELIGIBLE:
            print(f"\n✅ {result.program_name} ({program_code})")
            print(f"   Score éligibilité: {result.eligibility_score:.1f}/100")
            print(f"   Score compatibilité: {result.compatibility_score:.1f}/100")
            print(f"   Statut: {result.recommendation_status.value}")
            print(f"   Urgence: {result.intervention_urgency.value}")
            print(f"   Bénéfice mensuel estimé: {result.estimated_monthly_benefit:,} FCFA")
            print(f"   Impact: {result.estimated_impact}")
            print(f"   Priorité: {result.processing_priority}")
    
    # Test recommandations
    recommendation_engine = SocialInterventionRecommendationEngine()
    recommendations = recommendation_engine.generate_global_recommendations(
        eligibility_results, test_person_data, test_vulnerability_assessment
    )
    
    print(f"\n🎯 RECOMMANDATIONS GLOBALES:")
    print(f"Complexité cas: {recommendations['case_complexity']}")
    print(f"Programmes recommandés: {recommendations['total_recommended_programs']}")
    print(f"Bénéfice total estimé: {recommendations['estimated_total_monthly_benefit']:,.0f} FCFA/mois")
    
    print(f"\n💡 INTERVENTIONS PRIORITAIRES:")
    for rec in recommendations['primary_interventions']:
        print(f"   • {rec}")
    
    print(f"\n🔄 ACTIONS COMPLÉMENTAIRES:")
    for rec in recommendations['complementary_actions']:
        print(f"   • {rec}")
    
    print(f"\n⚡ MESURES PRÉVENTIVES:")
    for rec in recommendations['preventive_measures']:
        print(f"   • {rec}")
    
    print(f"\n📅 Prochaine évaluation: {recommendations['next_evaluation_date'][:10]}")
    print("\n✅ Test moteur éligibilité terminé avec succès")

if __name__ == "__main__":
    test_eligibility_engine()