# ===================================================================
# RSU GABON - INTÉGRATION SERVICES APP DANS ARCHITECTURE EXISTANTE
# Standards Top 1% - Continuité avec Core + Identity Apps
# ===================================================================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import VulnerabilityAssessment, SocialProgramEligibility
from .serializers import VulnerabilityAssessmentSerializer, SocialProgramEligibilitySerializer
from .services.vulnerability_scoring import GabonVulnerabilityScoringEngine
from rest_framework.permissions import AllowAny


class VulnerabilityAssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gestion évaluations vulnérabilité
    
    Endpoints disponibles:
    - GET /api/v1/services/vulnerability-assessments/ : Liste évaluations
    - POST /api/v1/services/vulnerability-assessments/calculate_assessment/ : Nouveau calcul
    - GET /api/v1/services/vulnerability-assessments/statistics/ : Statistiques globales
    """
    permission_classes = [AllowAny]
    queryset = VulnerabilityAssessment.objects.select_related('person')
    serializer_class = VulnerabilityAssessmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vulnerability_level', 'person__province', 'geographic_priority_zone']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calculator = GabonVulnerabilityScoringEngine()

    @action(detail=False, methods=['post'])
    def calculate_assessment(self, request):
        """
        Calcul nouvelle évaluation vulnérabilité IA
        
        POST /api/v1/services/vulnerability-assessments/calculate_assessment/
        Body: {"person_id": 123}
        
        Response: Assessment complet avec scores, niveau, recommandations
        """
        person_id = request.data.get('person_id')
        if not person_id:
            return Response(
                {'error': 'person_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.identity_app.models import PersonIdentity
            person = PersonIdentity.objects.get(id=person_id)
            
            # Extraction données pour scoring IA
            person_data = self._extract_person_data(person)
            
            # Calcul scoring IA 5 dimensions
            assessment_data = self.calculator.calculate_vulnerability_assessment(person_data)

            # Sauvegarde assessment - CORRIGER L'ACCÈS AUX ATTRIBUTS
            # Sauvegarde assessment - ACCÈS CORRECT AUX ATTRIBUTS
            assessment = VulnerabilityAssessment.objects.create(
                person=person,
                global_score=assessment_data.global_score,
                vulnerability_level=assessment_data.vulnerability_level.value,
                dimension_scores=self._convert_dimension_scores(assessment_data.dimension_scores),
                priority_interventions=assessment_data.priority_interventions,
                social_programs_eligibility=assessment_data.social_programs_eligibility,
                geographic_priority_zone=assessment_data.geographic_priority_zone,
                confidence_score=assessment_data.confidence_score,
                assessed_by=request.user if hasattr(request, 'user') else None
            )

            # Mise à jour PersonIdentity avec nouveau score
            person.vulnerability_score = assessment_data.global_score
            person.save(update_fields=['vulnerability_score'])
            
            serializer = self.get_serializer(assessment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except PersonIdentity.DoesNotExist:
            return Response(
                {'error': f'PersonIdentity {person_id} non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur calcul assessment: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _extract_person_data(self, person):
        """Extraction données PersonIdentity pour moteur IA - adaptée aux champs réels"""
        household = getattr(person, 'household', None)
        
        # Calcul age depuis birth_date si age pas disponible
        age = person.age
        if not age and person.birth_date:
            from datetime import date
            today = date.today()
            age = today.year - person.birth_date.year
        
        return {
            # Données de base disponibles dans PersonIdentity
            'age': age or 30,
            'gender': person.gender or 'M',
            'province': person.province or 'ESTUAIRE',
            'is_household_head': person.is_household_head or False,
            'marital_status': person.marital_status or 'SINGLE',
            
            # Données économiques - utiliser les champs existants
            'monthly_income': person.monthly_income or 100000,  # Valeur par défaut FCFA
            'occupation': person.occupation or 'INFORMAL',
            'housing_type': 'RENTAL',  # Valeur par défaut
            'has_bank_account': False,  # Valeur par défaut (champ manquant)
            
            # Données sociales - utiliser champs existants
            'education_level': person.education_level or 'PRIMARY',
            'has_health_insurance': False,  # Valeur par défaut (champ manquant)
            'distance_health_center_km': 25,  # Valeur par défaut
            'social_support_network': 'MEDIUM',  # Valeur par défaut
            'has_disability': person.has_disability or False,
            
            # Données ménage - valeur par défaut
            'household_size': household.total_members if household else 4,
            
            # Données géographiques - valeurs par défaut
            'zone_type': 'RURAL',
            'road_access_type': 'DIRT',
            
            # Données résilience - valeurs par défaut
            'climate_shock_exposure': 'MEDIUM',
            'has_savings': False,
            'diversified_income_sources': False,
            'recovery_time_months': 12,
            
            # Données spéciales - valeurs par défaut
            'is_pregnant': False,
            'is_breastfeeding': False,
        }
    def _serialize_dimension_scores(self, dimension_scores):
        """Sérialisation scores dimensions pour JSON"""
        return {
            dim_name: {
                'score': dim_score.score,
                'weight': dim_score.weight,
                'contributing_factors': dim_score.contributing_factors,
                'risk_indicators': dim_score.risk_indicators,
                'recommendations': dim_score.recommendations
            }
            for dim_name, dim_score in dimension_scores.items()
        }
    
    def _convert_dimension_scores(self, dimension_scores):
        """Conversion des DimensionScore en dictionnaire pour JSON"""
        result = {}
        for dim_name, dim_score in dimension_scores.items():
            result[dim_name] = {
                'score': dim_score.score,
                'weight': dim_score.weight,
                'contributing_factors': dim_score.contributing_factors,
                'risk_indicators': dim_score.risk_indicators,
                'recommendations': dim_score.recommendations
            }
        return result
        
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Statistiques vulnérabilité globales
        
        GET /api/v1/services/vulnerability-assessments/statistics/
        """
        stats = {
            'total_assessments': self.queryset.count(),
            'by_level': list(self.queryset.values('vulnerability_level').annotate(
                count=models.Count('id')
            )),
            'by_province': list(self.queryset.values('person__province').annotate(
                count=models.Count('id'),
                avg_score=models.Avg('global_score')
            )),
            'avg_global_score': self.queryset.aggregate(
                avg=models.Avg('global_score')
            )['avg'] or 0,
            'critical_count': self.queryset.filter(vulnerability_level='CRITICAL').count(),
            'high_count': self.queryset.filter(vulnerability_level='HIGH').count(),
        }
        return Response(stats)

class SocialProgramEligibilityViewSet(viewsets.ReadOnlyModelViewSet):
    """APIs lecture seule éligibilités programmes sociaux"""
    queryset = SocialProgramEligibility.objects.select_related('person')
    serializer_class = SocialProgramEligibilitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['program_code', 'recommendation_level', 'person__province']