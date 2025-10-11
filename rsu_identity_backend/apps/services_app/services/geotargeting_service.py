# ===================================================================
# RSU GABON - SERVICE GEOTARGETING COMPLET
# Identification zones prioritaires et optimisation distribution
# ===================================================================

import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from django.db import transaction
from django.db.models import Count, Avg, Q, F, Sum
from django.utils import timezone

from apps.identity_app.models import PersonIdentity, GeographicData
from ..models import VulnerabilityAssessment
from apps.programs_app.models import SocialProgram  
from .base_service import BaseService

logger = logging.getLogger(__name__)


class GeotargetingService(BaseService):
    """
    Service de géotargeting et optimisation déploiement programmes
    Analyse zones prioritaires pour interventions ciblées
    """
    
    # Classification zones prioritaires Gabon
    ZONE_PRIORITY_MAPPING = {
        'ZONE_1': {
            'name': 'CRITIQUE',
            'provinces': ['NYANGA', 'OGOOUE_LOLO', 'OGOOUE_IVINDO'],
            'characteristics': 'Zones isolées, accès difficile, services limités',
            'intervention_multiplier': 1.5
        },
        'ZONE_2': {
            'name': 'ÉLEVÉE',
            'provinces': ['HAUT_OGOOUE', 'NGOUNIE', 'WOLEU_NTEM'],
            'characteristics': 'Zones rurales, infrastructures limitées',
            'intervention_multiplier': 1.3
        },
        'ZONE_3': {
            'name': 'MODÉRÉE',
            'provinces': ['MOYEN_OGOOUE', 'OGOOUE_MARITIME'],
            'characteristics': 'Zones péri-urbaines, accès modéré',
            'intervention_multiplier': 1.1
        },
        'ZONE_4': {
            'name': 'STANDARD',
            'provinces': ['ESTUAIRE'],
            'characteristics': 'Zone urbaine, services accessibles',
            'intervention_multiplier': 1.0
        }
    }
    
    # Coûts moyens intervention par zone (FCFA/personne) - VALEURS PAR DÉFAUT
    # NOTE: Ces coûts DOIVENT être configurables par les administrateurs
    # via un modèle GeographicInterventionCost ou paramètres système
    DEFAULT_INTERVENTION_COSTS = {
        'ZONE_1': 150000,  # Zones critiques isolées
        'ZONE_2': 100000,  # Zones rurales
        'ZONE_3': 75000,   # Zones péri-urbaines
        'ZONE_4': 50000    # Zones urbaines
    }
    
    def __init__(self):
        super().__init__()
        # Charger coûts configurables depuis base de données
        self.intervention_costs = self._load_intervention_costs()

    def analyze_geographic_vulnerability(
        self, 
        province: str = None
    ) -> Dict:
        """
        Analyse vulnérabilité géographique par zone
        
        Args:
            province: Filtrer par province (optionnel)
            
        Returns:
            Dict: Analyse complète vulnérabilité géographique
        """
        try:
            queryset = VulnerabilityAssessment.objects.filter(is_active=True)
            
            if province:
                queryset = queryset.filter(person__province=province)
            
            # Analyse par province
            province_analysis = {}
            
            for zone_key, zone_data in self.ZONE_PRIORITY_MAPPING.items():
                for prov in zone_data['provinces']:
                    if province and prov != province:
                        continue
                    
                    # Statistiques province
                    prov_assessments = queryset.filter(person__province=prov)
                    total_persons = prov_assessments.count()
                    
                    if total_persons == 0:
                        continue
                    
                    # Distribution niveaux vulnérabilité
                    critical_count = prov_assessments.filter(risk_level='CRITICAL').count()
                    high_count = prov_assessments.filter(
                        risk_level='HIGH'
                    ).count()
                    
                    # Score moyen
                    # Score moyen
                    avg_vuln = prov_assessments.aggregate(
                        avg_score=Avg('vulnerability_score')
                    )['avg_score'] or 0

                    
                    # Score accessibilité (si données géographiques disponibles)
                    accessibility_score = self._calculate_province_accessibility(prov)
                    
                    province_analysis[prov] = {
                        'priority_zone': zone_key,
                        'zone_name': zone_data['name'],
                        'total_population': total_persons,
                        'critical_vulnerable': critical_count,
                        'high_vulnerable': high_count,
                        'vulnerability_rate': round(
                            (critical_count + high_count) / total_persons * 100, 2
                        ) if total_persons > 0 else 0,
                        'avg_vulnerability_score': round(float(avg_vuln), 2),
                        'accessibility_score': accessibility_score,
                        'intervention_cost_per_person': self.intervention_costs.get(
                            zone_key,
                            self.DEFAULT_INTERVENTION_COSTS[zone_key]
                        ),
                        'characteristics': zone_data['characteristics']
                    }
            
            # Classement provinces par priorité
            sorted_provinces = sorted(
                province_analysis.items(),
                key=lambda x: (
                    -x[1]['vulnerability_rate'],
                    -x[1]['critical_vulnerable']
                )
            )
            
            # Recommandations stratégiques
            recommendations = self._generate_geographic_recommendations(
                province_analysis
            )
            
            result = {
                'analysis_date': timezone.now().isoformat(),
                'provinces_analyzed': len(province_analysis),
                'province_details': dict(sorted_provinces),
                'strategic_recommendations': recommendations,
                'filters_applied': {'province': province}
            }
            
            self.log_operation(
                'geographic_vulnerability_analyzed',
                {
                    'provinces_count': len(province_analysis),
                    'province_filter': province
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur analyse géographique: {str(e)}")
            raise

    def calculate_zone_accessibility_score(
        self, 
        province: str,
        location_name: str = None
    ) -> float:
        """
        Calcule score accessibilité zone (0-100)
        
        Args:
            province: Province
            location_name: Localité spécifique (optionnel)
            
        Returns:
            float: Score accessibilité 0-100 (100 = très accessible)
        """
        try:
            # Récupérer données géographiques
            geo_queryset = GeographicData.objects.filter(province=province)
            
            if location_name:
                geo_queryset = geo_queryset.filter(location_name=location_name)
            
            if not geo_queryset.exists():
                # Pas de données = score estimé selon zone
                return self._estimate_accessibility_from_zone(province)
            
            # Score moyen accessibilité
            avg_accessibility = geo_queryset.aggregate(
                avg_score=Avg('accessibility_score')
            )['avg_score']
            
            return round(float(avg_accessibility or 50.0), 2)
            
        except Exception as e:
            logger.error(f"Erreur calcul accessibilité: {str(e)}")
            return 50.0

    def identify_priority_zones(
        self,
        min_vulnerable_population: int = 100,
        min_vulnerability_rate: float = 40.0
    ) -> List[Dict]:
        """
        Identifie zones prioritaires pour interventions
        
        Args:
            min_vulnerable_population: Population vulnérable minimum
            min_vulnerability_rate: Taux vulnérabilité minimum (%)
            
        Returns:
            List[Dict]: Zones prioritaires classées
        """
        try:
            priority_zones = []
            
            # Analyse par province
            for province_code in self._get_all_provinces():
                assessments = VulnerabilityAssessment.objects.filter(
                    person__province=province_code,
                    is_active=True
                )
                
                total_pop = assessments.count()
                if total_pop < min_vulnerable_population:
                    continue
                
                # Comptage vulnérables
                vulnerable_count = assessments.filter(
                    risk_level__in=['CRITICAL', 'HIGH']
                ).count()
                
                vulnerability_rate = (vulnerable_count / total_pop * 100) if total_pop > 0 else 0
                
                if vulnerability_rate < min_vulnerability_rate:
                    continue
                
                # Zone prioritaire identifiée
                zone_key = self._get_zone_from_province(province_code)
                zone_data = self.ZONE_PRIORITY_MAPPING[zone_key]
                
                # Score accessibilité
                accessibility = self.calculate_zone_accessibility_score(province_code)
                
                # Score priorité composite
                priority_score = self._calculate_composite_priority_score(
                    vulnerability_rate,
                    vulnerable_count,
                    accessibility,
                    zone_key
                )
                
                # Coût intervention pour cette zone
                intervention_cost = self.intervention_costs.get(
                    zone_key,
                    self.DEFAULT_INTERVENTION_COSTS[zone_key]
                )
                
                priority_zones.append({
                    'province': province_code,
                    'priority_zone': zone_key,
                    'zone_classification': zone_data['name'],
                    'total_population': total_pop,
                    'vulnerable_population': vulnerable_count,
                    'vulnerability_rate': round(vulnerability_rate, 2),
                    'accessibility_score': accessibility,
                    'priority_score': priority_score,
                    'estimated_intervention_cost': vulnerable_count * intervention_cost,
                    'cost_per_person': intervention_cost,
                    'recommended_programs': self._recommend_programs_for_zone(
                        province_code,
                        vulnerability_rate
                    )
                })
            
            # Trier par score priorité décroissant
            priority_zones.sort(key=lambda x: x['priority_score'], reverse=True)
            
            self.log_operation(
                'priority_zones_identified',
                {
                    'zones_count': len(priority_zones),
                    'min_vulnerable_pop': min_vulnerable_population,
                    'min_vulnerability_rate': min_vulnerability_rate
                }
            )
            
            return priority_zones
            
        except Exception as e:
            logger.error(f"Erreur identification zones prioritaires: {str(e)}")
            raise

    def optimize_program_deployment(
        self,
        program_code: str,
        available_budget: Decimal,
        target_provinces: List[str] = None
    ) -> Dict:
        """
        Optimise déploiement programme selon budget et zones
        
        Args:
            program_code: Code du programme
            available_budget: Budget disponible (FCFA)
            target_provinces: Provinces ciblées (optionnel)
            
        Returns:
            Dict: Plan déploiement optimisé
        """
        try:
            # Récupérer programme
            program = SocialProgram.objects.get(code=program_code)
            
            # Identifier bénéficiaires potentiels par province
            potential_beneficiaries = {}
            
            provinces_to_analyze = target_provinces or self._get_all_provinces()
            
            for province in provinces_to_analyze:
                # Bénéficiaires éligibles dans la province
                eligible_count = self._count_eligible_beneficiaries(
                    program_code,
                    province
                )
                
                if eligible_count == 0:
                    continue
                
                zone_key = self._get_zone_from_province(province)
                cost_per_person = self.intervention_costs.get(
                    zone_key,
                    self.DEFAULT_INTERVENTION_COSTS[zone_key]
                )
                
                # Coût bénéfice mensuel
                monthly_benefit = float(program.benefit_amount_fcfa)
                total_cost_per_beneficiary = cost_per_person + (
                    monthly_benefit * program.duration_months
                )
                
                potential_beneficiaries[province] = {
                    'eligible_count': eligible_count,
                    'cost_per_beneficiary': total_cost_per_beneficiary,
                    'total_cost': eligible_count * total_cost_per_beneficiary,
                    'priority_zone': zone_key,
                    'intervention_multiplier': self.ZONE_PRIORITY_MAPPING[zone_key]['intervention_multiplier']
                }
            
            # Optimisation allocation budget
            deployment_plan = self._optimize_budget_allocation(
                potential_beneficiaries,
                float(available_budget)
            )
            
            self.log_operation(
                'program_deployment_optimized',
                {
                    'program_code': program_code,
                    'budget': float(available_budget),
                    'provinces_analyzed': len(potential_beneficiaries)
                }
            )
            
            return {
                'program_code': program_code,
                'program_name': program.name,
                'available_budget': float(available_budget),
                'deployment_plan': deployment_plan,
                'optimization_date': timezone.now().isoformat()
            }
            
        except SocialProgram.DoesNotExist:
            logger.error(f"Programme {program_code} introuvable")
            raise ValueError(f"Programme {program_code} introuvable")
        except Exception as e:
            logger.error(f"Erreur optimisation déploiement: {str(e)}")
            raise
            
            # Classement provinces par priorité
            sorted_provinces = sorted(
                province_analysis.items(),
                key=lambda x: (
                    -x[1]['vulnerability_rate'],
                    -x[1]['critical_vulnerable']
                )
            )
            
            # Recommandations stratégiques
            recommendations = self._generate_geographic_recommendations(
                province_analysis
            )
            
            result = {
                'analysis_date': timezone.now().isoformat(),
                'provinces_analyzed': len(province_analysis),
                'province_details': dict(sorted_provinces),
                'strategic_recommendations': recommendations,
                'filters_applied': {'province': province}
            }
            
            self.log_operation(
                'geographic_vulnerability_analyzed',
                {
                    'provinces_count': len(province_analysis),
                    'province_filter': province
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur analyse géographique: {str(e)}")
            raise

    def calculate_zone_accessibility_score(
        self, 
        province: str,
        location_name: str = None
    ) -> float:
        """
        Calcule score accessibilité zone (0-100)
        
        Args:
            province: Province
            location_name: Localité spécifique (optionnel)
            
        Returns:
            float: Score accessibilité 0-100 (100 = très accessible)
        """
        try:
            # Récupérer données géographiques
            geo_queryset = GeographicData.objects.filter(province=province)
            
            if location_name:
                geo_queryset = geo_queryset.filter(location_name=location_name)
            
            if not geo_queryset.exists():
                # Pas de données = score estimé selon zone
                return self._estimate_accessibility_from_zone(province)
            
            # Score moyen accessibilité
            avg_accessibility = geo_queryset.aggregate(
                avg_score=Avg('accessibility_score')
            )['avg_score']
            
            return round(float(avg_accessibility or 50.0), 2)
            
        except Exception as e:
            logger.error(f"Erreur calcul accessibilité: {str(e)}")
            return 50.0

    def identify_priority_zones(
        self,
        min_vulnerable_population: int = 100,
        min_vulnerability_rate: float = 40.0
    ) -> List[Dict]:
        """
        Identifie zones prioritaires pour interventions
        
        Args:
            min_vulnerable_population: Population vulnérable minimum
            min_vulnerability_rate: Taux vulnérabilité minimum (%)
            
        Returns:
            List[Dict]: Zones prioritaires classées
        """
        try:
            priority_zones = []
            
            # Analyse par province
            for province_code in self._get_all_provinces():
                assessments = VulnerabilityAssessment.objects.filter(
                    person__province=province_code,
                    is_active=True
                )
                
                total_pop = assessments.count()
                if total_pop < min_vulnerable_population:
                    continue
                
                # Comptage vulnérables
                vulnerable_count = assessments.filter(
                    risk_level__in=['CRITICAL', 'HIGH']
                ).count()
                
                vulnerability_rate = (vulnerable_count / total_pop * 100) if total_pop > 0 else 0
                
                if vulnerability_rate < min_vulnerability_rate:
                    continue
                
                # Zone prioritaire identifiée
                zone_key = self._get_zone_from_province(province_code)
                zone_data = self.ZONE_PRIORITY_MAPPING[zone_key]
                
                # Score accessibilité
                accessibility = self.calculate_zone_accessibility_score(province_code)
                
                # Score priorité composite
                priority_score = self._calculate_composite_priority_score(
                    vulnerability_rate,
                    vulnerable_count,
                    accessibility,
                    zone_key
                )
                
                priority_zones.append({
                    'province': province_code,
                    'priority_zone': zone_key,
                    'zone_classification': zone_data['name'],
                    'total_population': total_pop,
                    'vulnerable_population': vulnerable_count,
                    'vulnerability_rate': round(vulnerability_rate, 2),
                    'accessibility_score': accessibility,
                    'priority_score': priority_score,
                    'estimated_intervention_cost': vulnerable_count * self.INTERVENTION_COSTS[zone_key],
                    'recommended_programs': self._recommend_programs_for_zone(
                        province_code,
                        vulnerability_rate
                    )
                })
            
            # Trier par score priorité décroissant
            priority_zones.sort(key=lambda x: x['priority_score'], reverse=True)
            
            self.log_operation(
                'priority_zones_identified',
                {
                    'zones_count': len(priority_zones),
                    'min_vulnerable_pop': min_vulnerable_population,
                    'min_vulnerability_rate': min_vulnerability_rate
                }
            )
            
            return priority_zones
            
        except Exception as e:
            logger.error(f"Erreur identification zones prioritaires: {str(e)}")
            raise

    def optimize_program_deployment(
        self,
        program_code: str,
        available_budget: Decimal,
        target_provinces: List[str] = None
    ) -> Dict:
        """
        Optimise déploiement programme selon budget et zones
        
        Args:
            program_code: Code du programme
            available_budget: Budget disponible (FCFA)
            target_provinces: Provinces ciblées (optionnel)
            
        Returns:
            Dict: Plan déploiement optimisé
        """
        try:
            # Récupérer programme
            program = SocialProgram.objects.get(code=program_code)
            
            # Identifier bénéficiaires potentiels par province
            potential_beneficiaries = {}
            
            provinces_to_analyze = target_provinces or self._get_all_provinces()
            
            for province in provinces_to_analyze:
                # Bénéficiaires éligibles dans la province
                eligible_count = self._count_eligible_beneficiaries(
                    program_code,
                    province
                )
                
                if eligible_count == 0:
                    continue
                
                zone_key = self._get_zone_from_province(province)
                cost_per_person = self.INTERVENTION_COSTS[zone_key]
                
                # Coût bénéfice mensuel
                monthly_benefit = float(program.benefit_amount_fcfa)
                total_cost_per_beneficiary = cost_per_person + (
                    monthly_benefit * program.duration_months
                )
                
                potential_beneficiaries[province] = {
                    'eligible_count': eligible_count,
                    'cost_per_beneficiary': total_cost_per_beneficiary,
                    'total_cost': eligible_count * total_cost_per_beneficiary,
                    'priority_zone': zone_key,
                    'intervention_multiplier': self.ZONE_PRIORITY_MAPPING[zone_key]['intervention_multiplier']
                }
            
            # Optimisation allocation budget
            deployment_plan = self._optimize_budget_allocation(
                potential_beneficiaries,
                float(available_budget)
            )
            
            self.log_operation(
                'program_deployment_optimized',
                {
                    'program_code': program_code,
                    'budget': float(available_budget),
                    'provinces_analyzed': len(potential_beneficiaries)
                }
            )
            
            return {
                'program_code': program_code,
                'program_name': program.name,
                'available_budget': float(available_budget),
                'deployment_plan': deployment_plan,
                'optimization_date': timezone.now().isoformat()
            }
            
        except SocialProgram.DoesNotExist:
            logger.error(f"Programme {program_code} introuvable")
            raise ValueError(f"Programme {program_code} introuvable")
        except Exception as e:
            logger.error(f"Erreur optimisation déploiement: {str(e)}")
            raise

    def _load_intervention_costs(self) -> Dict[str, float]:
        """
        Charge coûts intervention depuis base de données
        """
        try:
            from django.core.cache import cache
            from ..models import GeographicInterventionCost  # ✅ Import modèle
            
            # Vérifier cache
            cached_costs = cache.get('intervention_costs')
            if cached_costs:
                return cached_costs
            
            # Charger depuis DB
            costs = {}
            cost_objects = GeographicInterventionCost.objects.filter(is_active=True)
            
            for cost_obj in cost_objects:
                costs[cost_obj.zone_key] = float(cost_obj.cost_per_person)
            
            # Si aucune config en DB, utiliser défauts
            if not costs:
                self.logger.warning("Aucun coût en DB, utilisation valeurs par défaut")
                costs = self.DEFAULT_INTERVENTION_COSTS.copy()
            
            # Mettre en cache 1 heure
            cache.set('intervention_costs', costs, 3600)
            
            self.logger.info(f"Coûts intervention chargés: {costs}")
            
            return costs
            
        except Exception as e:
            self.logger.warning(f"Erreur chargement coûts: {str(e)}")
            return self.DEFAULT_INTERVENTION_COSTS.copy()
        
    def update_intervention_cost(
        self, 
        zone_key: str, 
        new_cost: float,
        updated_by=None
    ) -> bool:
        """
        Met à jour coût intervention pour une zone (fonction admin)
        
        Args:
            zone_key: Clé de la zone (ZONE_1, ZONE_2, etc.)
            new_cost: Nouveau coût en FCFA
            updated_by: Utilisateur effectuant la modification
            
        Returns:
            bool: True si succès
        """
        try:
            if zone_key not in self.ZONE_PRIORITY_MAPPING:
                raise ValueError(f"Zone {zone_key} invalide")
            
            if new_cost < 0:
                raise ValueError("Coût doit être positif")
            
            # TODO: Sauvegarder dans modèle GeographicInterventionCost
            # Pour l'instant, mettre à jour en mémoire et cache
            
            self.intervention_costs[zone_key] = new_cost
            
            from django.core.cache import cache
            cache.set('intervention_costs', self.intervention_costs, 3600)
            
            self.log_operation(
                'intervention_cost_updated',
                {
                    'zone_key': zone_key,
                    'new_cost': new_cost,
                    'updated_by': updated_by.username if updated_by else None
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour coût intervention: {str(e)}")
            return False

    def calculate_intervention_cost(
        self,
        province: str,
        beneficiary_count: int,
        program_duration_months: int,
        monthly_benefit: float,
        custom_operational_cost: float = None
    ) -> Dict:

        """
        Calcule coût total intervention dans une zone
        
        Args:
            province: Province cible
            beneficiary_count: Nombre de bénéficiaires
            program_duration_months: Durée programme (mois)
            monthly_benefit: Montant mensuel par bénéficiaire (FCFA)
            custom_operational_cost: Coût opérationnel personnalisé (optionnel)
            
        Returns:
            Dict: Détail coûts intervention
        """
        try:
            zone_key = self._get_zone_from_province(province)
            
            # Coût opérationnel (logistique, déploiement, suivi)
            # Utilise coût personnalisé si fourni, sinon coût configuré/défaut
            operational_cost_per_person = (
                custom_operational_cost if custom_operational_cost is not None
                else self.intervention_costs.get(zone_key, self.DEFAULT_INTERVENTION_COSTS[zone_key])
            )
            
            # Coût total bénéfices (transferts directs)
            total_benefits = beneficiary_count * monthly_benefit * program_duration_months
            
            # Coût total opérationnel
            total_operational = beneficiary_count * operational_cost_per_person
            
            # Coût total programme
            total_cost = total_benefits + total_operational
            
            # Coût par bénéficiaire
            cost_per_beneficiary = total_cost / beneficiary_count if beneficiary_count > 0 else 0
            
            # Ratio efficacité (% du budget qui va directement aux bénéficiaires)
            efficiency_ratio = (total_benefits / total_cost * 100) if total_cost > 0 else 0
            
            result = {
                'province': province,
                'priority_zone': zone_key,
                'beneficiary_count': beneficiary_count,
                'program_duration_months': program_duration_months,
                'monthly_benefit_fcfa': monthly_benefit,
                'costs': {
                    'operational_cost_per_person': operational_cost_per_person,
                    'total_operational': total_operational,
                    'total_benefits': total_benefits,
                    'total_program_cost': total_cost,
                    'cost_per_beneficiary': cost_per_beneficiary
                },
                'efficiency_ratio': round(efficiency_ratio, 2),
                'cost_customized': custom_operational_cost is not None
            }
            
            self.log_operation(
                'intervention_cost_calculated',
                {
                    'province': province,
                    'beneficiary_count': beneficiary_count,
                    'total_cost': total_cost
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul coût intervention: {str(e)}")
            raise

    def generate_deployment_recommendations(
        self,
        program_code: str,
        available_budget: float,
        max_provinces: int = 5
    ) -> List[Dict]:
        """
        Génère recommandations déploiement optimisées
        
        Args:
            program_code: Code du programme
            available_budget: Budget disponible (FCFA)
            max_provinces: Nombre maximum de provinces à cibler
            
        Returns:
            List[Dict]: Recommandations par province classées
        """
        try:
            # Récupérer programme
            program = SocialProgram.objects.get(code=program_code)
            
            recommendations = []
            
            # Analyser toutes les provinces
            for province in self._get_all_provinces():
                # Nombre bénéficiaires éligibles
                eligible_count = self._count_eligible_beneficiaries(
                    program_code,
                    province
                )
                
                if eligible_count == 0:
                    continue
                
                # Calcul coûts
                cost_analysis = self.calculate_intervention_cost(
                    province=province,
                    beneficiary_count=eligible_count,
                    program_duration_months=program.duration_months,
                    monthly_benefit=float(program.benefit_amount_fcfa)
                )
                
                # Score impact (vulnérabilité × population)
                vulnerability_rate = self._get_province_vulnerability_rate(province)
                impact_score = vulnerability_rate * eligible_count / 100
                
                # ROI social (impact par FCFA dépensé)
                social_roi = impact_score / cost_analysis['costs']['total_program_cost'] * 1000000
                
                recommendations.append({
                    'province': province,
                    'priority_zone': cost_analysis['priority_zone'],
                    'eligible_beneficiaries': eligible_count,
                    'total_cost': cost_analysis['costs']['total_program_cost'],
                    'cost_per_beneficiary': cost_analysis['costs']['cost_per_beneficiary'],
                    'vulnerability_rate': vulnerability_rate,
                    'impact_score': round(impact_score, 2),
                    'social_roi': round(social_roi, 4),
                    'efficiency_ratio': cost_analysis['efficiency_ratio'],
                    'recommendation': self._generate_province_recommendation(
                        province,
                        cost_analysis,
                        vulnerability_rate,
                        available_budget
                    )
                })
            
            # Trier par ROI social décroissant
            recommendations.sort(key=lambda x: x['social_roi'], reverse=True)
            
            # Limiter au nombre demandé
            top_recommendations = recommendations[:max_provinces]
            
            # Calculer couverture budgétaire
            total_cost = sum(r['total_cost'] for r in top_recommendations)
            budget_coverage = (total_cost / available_budget * 100) if available_budget > 0 else 0
            
            self.log_operation(
                'deployment_recommendations_generated',
                {
                    'program_code': program_code,
                    'provinces_recommended': len(top_recommendations),
                    'budget_coverage': budget_coverage
                }
            )
            
            return {
                'program_code': program_code,
                'program_name': program.name,
                'available_budget': available_budget,
                'recommendations': top_recommendations,
                'summary': {
                    'total_provinces_recommended': len(top_recommendations),
                    'total_beneficiaries': sum(r['eligible_beneficiaries'] for r in top_recommendations),
                    'total_estimated_cost': total_cost,
                    'budget_coverage_percent': round(budget_coverage, 2),
                    'budget_remaining': available_budget - total_cost if total_cost <= available_budget else 0
                }
            }
            
        except SocialProgram.DoesNotExist:
            logger.error(f"Programme {program_code} introuvable")
            raise ValueError(f"Programme {program_code} introuvable")
        except Exception as e:
            logger.error(f"Erreur génération recommandations: {str(e)}")
            raise

    # ===================================================================
    # MÉTHODES PRIVÉES - UTILITAIRES
    # ===================================================================

    def _calculate_province_accessibility(self, province: str) -> float:
        """Calcule score accessibilité moyen d'une province"""
        try:
            geo_data = GeographicData.objects.filter(province=province)
            
            if geo_data.exists():
                avg_score = geo_data.aggregate(
                    avg=Avg('accessibility_score')
                )['avg']
                return round(float(avg_score or 50.0), 2)
            
            return self._estimate_accessibility_from_zone(province)
            
        except Exception as e:
            logger.error(f"Erreur calcul accessibilité province: {str(e)}")
            return 50.0

    def _estimate_accessibility_from_zone(self, province: str) -> float:
        """Estime accessibilité selon zone prioritaire"""
        zone_key = self._get_zone_from_province(province)
        
        # Estimation selon priorité zone
        accessibility_estimates = {
            'ZONE_1': 25.0,  # Critique = faible accessibilité
            'ZONE_2': 45.0,  # Élevée = accessibilité limitée
            'ZONE_3': 65.0,  # Modérée = accessibilité moyenne
            'ZONE_4': 85.0   # Standard = bonne accessibilité
        }
        
        return accessibility_estimates.get(zone_key, 50.0)

    def _get_zone_from_province(self, province: str) -> str:
        """Retourne clé zone depuis province"""
        for zone_key, zone_data in self.ZONE_PRIORITY_MAPPING.items():
            if province in zone_data['provinces']:
                return zone_key
        return 'ZONE_4'  # Défaut

    def _get_all_provinces(self) -> List[str]:
        """Retourne liste toutes les provinces"""
        all_provinces = []
        for zone_data in self.ZONE_PRIORITY_MAPPING.values():
            all_provinces.extend(zone_data['provinces'])
        return all_provinces

    def _calculate_composite_priority_score(
        self,
        vulnerability_rate: float,
        vulnerable_count: int,
        accessibility: float,
        zone_key: str
    ) -> float:
        """
        Calcule score priorité composite
        
        Pondération:
        - 40% Taux vulnérabilité
        - 30% Nombre vulnérables
        - 20% Difficulté accès (inverse accessibilité)
        - 10% Multiplicateur zone
        """
        # Normaliser nombre vulnérables (échelle 0-100)
        normalized_count = min(vulnerable_count / 10, 100)
        
        # Difficulté accès (inverse accessibilité)
        access_difficulty = 100 - accessibility
        
        # Multiplicateur zone
        zone_multiplier = self.ZONE_PRIORITY_MAPPING[zone_key]['intervention_multiplier']
        
        # Score composite
        composite_score = (
            vulnerability_rate * 0.40 +
            normalized_count * 0.30 +
            access_difficulty * 0.20 +
            (zone_multiplier - 1) * 100 * 0.10
        )
        
        return round(composite_score, 2)

    def _recommend_programs_for_zone(
        self,
        province: str,
        vulnerability_rate: float
    ) -> List[str]:
        """Recommande programmes adaptés à une zone"""
        recommended = []
        
        zone_key = self._get_zone_from_province(province)
        
        # Programmes selon niveau vulnérabilité
        if vulnerability_rate >= 70:
            recommended.extend([
                'Transferts monétaires d\'urgence',
                'Aide alimentaire',
                'Soins santé gratuits'
            ])
        elif vulnerability_rate >= 50:
            recommended.extend([
                'Transferts monétaires ciblés',
                'Bourses scolaires',
                'Formation professionnelle'
            ])
        else:
            recommended.extend([
                'Microcrédits',
                'Appui activités génératrices de revenus'
            ])
        
        # Programmes selon accessibilité zone
        if zone_key in ['ZONE_1', 'ZONE_2']:
            recommended.append('Services mobiles de santé')
            recommended.append('Programmes agriculture/élevage')
        
        return recommended[:3]  # Top 3

    def _count_eligible_beneficiaries(
        self,
        program_code: str,
        province: str
    ) -> int:
        """Compte bénéficiaires éligibles dans une province"""
        try:
            from ..models import SocialProgramEligibility
            
            count = SocialProgramEligibility.objects.filter(
                program_code=program_code,
                person__province=province,
                recommendation_level__in=['HIGHLY_RECOMMENDED', 'RECOMMENDED']
            ).count()
            
            return count
            
        except Exception as e:
            logger.error(f"Erreur comptage bénéficiaires: {str(e)}")
            return 0

    def _get_province_vulnerability_rate(self, province: str) -> float:
        """Retourne taux vulnérabilité d'une province"""
        try:
            assessments = VulnerabilityAssessment.objects.filter(
                person__province=province,
                is_active=True
            )
            
            total = assessments.count()
            if total == 0:
                return 0.0
            
            vulnerable = assessments.filter(
                risk_level__in=['CRITICAL', 'HIGH']
            ).count()
            
            return round(vulnerable / total * 100, 2)
            
        except Exception as e:
            logger.error(f"Erreur calcul taux vulnérabilité: {str(e)}")
            return 0.0

    def _optimize_budget_allocation(
        self,
        beneficiaries_by_province: Dict,
        available_budget: float
    ) -> Dict:
        """
        Optimise allocation budget entre provinces
        Algorithme glouton basé sur ROI social
        """
        allocated = {}
        remaining_budget = available_budget
        
        # Trier provinces par ROI (coût/impact)
        sorted_provinces = sorted(
            beneficiaries_by_province.items(),
            key=lambda x: x[1]['cost_per_beneficiary'] / x[1]['intervention_multiplier']
        )
        
        for province, data in sorted_provinces:
            if remaining_budget <= 0:
                break
            
            # Calculer combien de bénéficiaires peuvent être couverts
            affordable_count = int(remaining_budget / data['cost_per_beneficiary'])
            actual_count = min(affordable_count, data['eligible_count'])
            
            if actual_count > 0:
                allocated_cost = actual_count * data['cost_per_beneficiary']
                
                allocated[province] = {
                    'beneficiaries_covered': actual_count,
                    'total_eligible': data['eligible_count'],
                    'coverage_rate': round(actual_count / data['eligible_count'] * 100, 2),
                    'allocated_budget': allocated_cost,
                    'priority_zone': data['priority_zone']
                }
                
                remaining_budget -= allocated_cost
        
        return {
            'provinces': allocated,
            'total_beneficiaries_covered': sum(p['beneficiaries_covered'] for p in allocated.values()),
            'total_budget_allocated': available_budget - remaining_budget,
            'budget_remaining': remaining_budget,
            'provinces_covered': len(allocated)
        }

    def _generate_geographic_recommendations(
        self,
        province_analysis: Dict
    ) -> List[str]:
        """Génère recommandations stratégiques géographiques"""
        recommendations = []
        
        # Identifier provinces prioritaires
        critical_provinces = [
            prov for prov, data in province_analysis.items()
            if data['vulnerability_rate'] >= 60
        ]
        
        if critical_provinces:
            recommendations.append(
                f"Intervention urgente requise dans {len(critical_provinces)} province(s) : "
                f"{', '.join(critical_provinces)}"
            )
        
        # Identifier zones sous-desservies
        low_access_provinces = [
            prov for prov, data in province_analysis.items()
            if data['accessibility_score'] < 40
        ]
        
        if low_access_provinces:
            recommendations.append(
                f"Déployer services mobiles dans zones isolées : {', '.join(low_access_provinces)}"
            )
        
        # Recommandations par zone prioritaire
        zone_1_provinces = [
            prov for prov, data in province_analysis.items()
            if data['priority_zone'] == 'ZONE_1'
        ]
        
        if zone_1_provinces:
            recommendations.append(
                f"Allouer ressources supplémentaires (+50%) pour zones critiques : {', '.join(zone_1_provinces)}"
            )
        
        return recommendations

    def _generate_province_recommendation(
        self,
        province: str,
        cost_analysis: Dict,
        vulnerability_rate: float,
        available_budget: float
    ) -> str:
        """Génère recommandation spécifique pour une province"""
        total_cost = cost_analysis['costs']['total_program_cost']
        
        if total_cost > available_budget:
            return "Budget insuffisant - Prioriser phases pilotes"
        elif vulnerability_rate >= 70:
            return "HAUTE PRIORITÉ - Déploiement immédiat recommandé"
        elif vulnerability_rate >= 50:
            return "Priorité élevée - Déploiement dans 3 mois"
        elif cost_analysis['efficiency_ratio'] >= 85:
            return "Excellent ROI - Déploiement recommandé"
        else:
            return "Évaluation terrain supplémentaire conseillée"

    def get_deployment_statistics(
        self,
        program_code: str = None
    ) -> Dict:
        """
        Génère statistiques déploiement géographique
        
        Args:
            program_code: Filtrer par programme (optionnel)
            
        Returns:
            Dict: Statistiques déploiement
        """
        try:
            from ..models import SocialProgramEligibility
            
            queryset = SocialProgramEligibility.objects.filter(
                recommendation_level__in=['HIGHLY_RECOMMENDED', 'RECOMMENDED']
            )
            
            if program_code:
                queryset = queryset.filter(program_code=program_code)
            
            # Statistiques par province
            province_stats = {}
            
            for province in self._get_all_provinces():
                count = queryset.filter(person__province=province).count()
                
                if count == 0:
                    continue
                
                zone_key = self._get_zone_from_province(province)
                
                province_stats[province] = {
                    'eligible_count': count,
                    'priority_zone': zone_key,
                    'zone_name': self.ZONE_PRIORITY_MAPPING[zone_key]['name'],
                    'intervention_cost_per_person': self.intervention_costs.get(
                        zone_key,
                        self.DEFAULT_INTERVENTION_COSTS[zone_key]
                    )
                }
            
            # Statistiques par zone
            zone_stats = {}
            for zone_key in self.ZONE_PRIORITY_MAPPING.keys():
                provinces_in_zone = [
                    p for p in province_stats.keys()
                    if province_stats[p]['priority_zone'] == zone_key
                ]
                
                if provinces_in_zone:
                    total_eligible = sum(
                        province_stats[p]['eligible_count']
                        for p in provinces_in_zone
                    )
                    
                    zone_stats[zone_key] = {
                        'zone_name': self.ZONE_PRIORITY_MAPPING[zone_key]['name'],
                        'provinces': provinces_in_zone,
                        'total_eligible': total_eligible,
                        'avg_cost_per_person': self.intervention_costs.get(
                            zone_key,
                            self.DEFAULT_INTERVENTION_COSTS[zone_key]
                        )
                    }
            
            result = {
                'program_code': program_code,
                'total_eligible': sum(p['eligible_count'] for p in province_stats.values()),
                'provinces_covered': len(province_stats),
                'province_statistics': province_stats,
                'zone_statistics': zone_stats,
                'generated_at': timezone.now().isoformat()
            }
            
            self.log_operation(
                'deployment_statistics_generated',
                {
                    'program_code': program_code,
                    'total_eligible': result['total_eligible']
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur génération statistiques déploiement: {str(e)}")
            raise

    def compare_deployment_scenarios(
        self,
        program_code: str,
        scenarios: List[Dict]
    ) -> Dict:
        """
        Compare différents scénarios de déploiement
        
        Args:
            program_code: Code du programme
            scenarios: Liste scénarios avec budget et provinces
                      Exemple: [
                          {'name': 'Scenario A', 'budget': 100000000, 'provinces': ['NYANGA']},
                          {'name': 'Scenario B', 'budget': 150000000, 'provinces': ['NYANGA', 'OGOOUE_LOLO']}
                      ]
            
        Returns:
            Dict: Comparaison détaillée scénarios
        """
        try:
            program = SocialProgram.objects.get(code=program_code)
            
            scenario_results = []
            
            for scenario in scenarios:
                # Optimiser déploiement pour ce scénario
                deployment = self.optimize_program_deployment(
                    program_code=program_code,
                    available_budget=Decimal(str(scenario['budget'])),
                    target_provinces=scenario.get('provinces')
                )
                
                # Calculer métriques clés
                plan = deployment['deployment_plan']
                
                scenario_results.append({
                    'scenario_name': scenario['name'],
                    'budget': scenario['budget'],
                    'target_provinces': scenario.get('provinces', 'Toutes'),
                    'beneficiaries_covered': plan['total_beneficiaries_covered'],
                    'budget_allocated': plan['total_budget_allocated'],
                    'budget_remaining': plan['budget_remaining'],
                    'provinces_covered': plan['provinces_covered'],
                    'coverage_rate': round(
                        plan['total_beneficiaries_covered'] / 
                        sum(self._count_eligible_beneficiaries(program_code, p) 
                            for p in self._get_all_provinces()) * 100, 2
                    ) if sum(self._count_eligible_beneficiaries(program_code, p) 
                            for p in self._get_all_provinces()) > 0 else 0,
                    'cost_per_beneficiary': round(
                        plan['total_budget_allocated'] / plan['total_beneficiaries_covered'], 2
                    ) if plan['total_beneficiaries_covered'] > 0 else 0
                })
            
            # Identifier meilleur scénario (ROI)
            best_scenario = max(
                scenario_results,
                key=lambda x: x['beneficiaries_covered'] / x['budget'] if x['budget'] > 0 else 0
            )
            
            result = {
                'program_code': program_code,
                'program_name': program.name,
                'scenarios': scenario_results,
                'best_scenario': best_scenario['scenario_name'],
                'comparison_date': timezone.now().isoformat()
            }
            
            self.log_operation(
                'deployment_scenarios_compared',
                {
                    'program_code': program_code,
                    'scenarios_count': len(scenarios)
                }
            )
            
            return result
            
        except SocialProgram.DoesNotExist:
            logger.error(f"Programme {program_code} introuvable")
            raise ValueError(f"Programme {program_code} introuvable")
        except Exception as e:
            logger.error(f"Erreur comparaison scénarios: {str(e)}")
            raise

    def get_intervention_costs_by_zone(self) -> Dict:
        """
        Retourne coûts d'intervention actuels par zone
        Utile pour dashboards admin
        
        Returns:
            Dict: Coûts par zone avec métadonnées
        """
        try:
            costs = {}
            
            for zone_key, zone_data in self.ZONE_PRIORITY_MAPPING.items():
                current_cost = self.intervention_costs.get(
                    zone_key,
                    self.DEFAULT_INTERVENTION_COSTS[zone_key]
                )
                
                costs[zone_key] = {
                    'zone_name': zone_data['name'],
                    'provinces': zone_data['provinces'],
                    'cost_per_person_fcfa': current_cost,
                    'cost_per_person_euro': round(current_cost / 655.957, 2),
                    'is_default': zone_key not in self.intervention_costs or 
                                  self.intervention_costs[zone_key] == self.DEFAULT_INTERVENTION_COSTS[zone_key],
                    'characteristics': zone_data['characteristics'],
                    'intervention_multiplier': zone_data['intervention_multiplier']
                }
            
            return {
                'costs_by_zone': costs,
                'last_updated': timezone.now().isoformat(),
                'currency': 'FCFA',
                'configurable': True
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération coûts: {str(e)}")
            raise