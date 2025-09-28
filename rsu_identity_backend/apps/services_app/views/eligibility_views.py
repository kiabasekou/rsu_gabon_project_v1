

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
import time

class SocialProgramViewSet(viewsets.ModelViewSet):
    """
    ViewSet gestion programmes sociaux
    CRUD + statistiques utilisation budgétaire
    """
    queryset = SocialProgram.objects.all()
    serializer_class = SocialProgramSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'target_provinces', 'urban_rural_preference']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['code', 'name', 'annual_budget', 'launch_date']
    
    @action(detail=True, methods=['get'])
    def budget_utilization(self, request, pk=None):
        """Détail utilisation budgétaire d'un programme"""
        program = self.get_object()
        
        utilization_data = {
            'program_code': program.code,
            'program_name': program.name,
            'annual_budget': program.annual_budget,
            'remaining_budget': program.remaining_budget,
            'utilization_rate': program.current_budget_utilization,
            'max_beneficiaries': program.max_beneficiaries,
            'current_beneficiaries': program.eligibility_assessments.filter(
                allocation_decision='APPROVED'
            ).count(),
            'pending_assessments': program.eligibility_assessments.filter(
                allocation_decision='PENDING'
            ).count(),
            'monthly_breakdown': self._get_monthly_utilization(program)
        }
        
        return Response(utilization_data)
    
    def _get_monthly_utilization(self, program):
        """Calcul utilisation budgétaire mensuelle"""
        # Implémentation simplifiée - en production, requête optimisée
        return {
            'current_month': float(program.remaining_budget),
            'projected_utilization': 75.0  # Exemple
        }

class ProgramEligibilityViewSet(viewsets.ModelViewSet):
    """
    ViewSet évaluations éligibilité programmes
    Calcul IA + gestion décisions allocation
    """
    queryset = ProgramEligibilityAssessment.objects.all()
    serializer_class = ProgramEligibilityAssessmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = [
        'recommendation_status', 'intervention_urgency', 
        'allocation_decision', 'program__code'
    ]
    ordering_fields = [
        'processing_priority', 'compatibility_score', 
        'assessment_date', 'estimated_monthly_benefit'
    ]
    
    @action(detail=False, methods=['post'])
    def calculate_eligibility(self, request):
        """
        Calcul éligibilité pour une personne
        Utilise le moteur IA d'éligibilité
        """
        start_time = time.time()
        
        serializer = EligibilityCalculationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        person_id = serializer.validated_data['person_id']
        target_programs = serializer.validated_data.get('programs', [])
        force_recalc = serializer.validated_data.get('force_recalculation', False)
        
        try:
            # Récupération personne et évaluation vulnérabilité
            person = get_object_or_404(PersonIdentity, id=person_id)
            vulnerability_assessment = person.vulnerability_assessments.first()
            
            if not vulnerability_assessment:
                return Response(
                    {'error': 'Aucune évaluation vulnérabilité trouvée. Calculer d\'abord le scoring.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Données personne pour moteur IA
            person_data = self._prepare_person_data(person)
            vulnerability_data = self._prepare_vulnerability_data(vulnerability_assessment)
            
            # Calcul éligibilité avec moteur IA
            from ..services.eligibility_engine import GabonSocialProgramEligibilityEngine
            from ..services.recommendation_engine import SocialInterventionRecommendationEngine
            
            eligibility_engine = GabonSocialProgramEligibilityEngine()
            recommendation_engine = SocialInterventionRecommendationEngine()
            
            # Calcul éligibilité tous programmes ou programmes spécifiques
            eligibility_results = eligibility_engine.calculate_eligibility_assessment(
                person_data, vulnerability_data
            )
            
            # Filtrage programmes si spécifiés
            if target_programs:
                eligibility_results = {
                    k: v for k, v in eligibility_results.items() 
                    if k in target_programs
                }
            
            # Génération recommandations globales
            global_recommendations = recommendation_engine.generate_global_recommendations(
                eligibility_results, person_data, vulnerability_data
            )
            
            # Sauvegarde résultats en base
            saved_assessments = self._save_eligibility_results(
                person, vulnerability_assessment, eligibility_results, request.user
            )
            
            # Préparation réponse
            processing_duration = int((time.time() - start_time) * 1000)
            
            response_data = {
                'person_id': person.id,
                'person_name': person.full_name,
                'vulnerability_score': vulnerability_assessment.global_score,
                'vulnerability_level': vulnerability_assessment.vulnerability_level,
                'eligibility_results': [
                    self._format_eligibility_result(result)
                    for result in eligibility_results.values()
                ],
                'global_recommendations': global_recommendations,
                'calculation_timestamp': timezone.now(),
                'processing_duration_ms': processing_duration,
                'saved_assessments_count': len(saved_assessments)
            }
            
            response_serializer = EligibilityCalculationResponseSerializer(response_data)
            return Response(response_serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur calcul éligibilité: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def person_programs(self, request):
        """Programmes éligibles pour une personne"""
        person_id = request.query_params.get('person_id')
        if not person_id:
            return Response(
                {'error': 'Paramètre person_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assessments = self.queryset.filter(
            person_id=person_id,
            recommendation_status__in=['HIGHLY_RECOMMENDED', 'RECOMMENDED']
        ).order_by('processing_priority')
        
        serializer = self.get_serializer(assessments, many=True)
        return Response({
            'person_id': person_id,
            'eligible_programs_count': assessments.count(),
            'programs': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def approve_allocation(self, request, pk=None):
        """Approbation allocation par agent"""
        assessment = self.get_object()
        
        if assessment.allocation_decision != 'PENDING':
            return Response(
                {'error': 'Allocation déjà traitée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assessment.allocation_decision = 'APPROVED'
        assessment.allocation_date = timezone.now()
        assessment.approved_by = request.user
        assessment.save()
        
        return Response({
            'message': 'Allocation approuvée',
            'assessment_id': assessment.id,
            'monthly_benefit': assessment.estimated_monthly_benefit
        })
    
    def _prepare_person_data(self, person):
        """Préparation données personne pour moteur IA"""
        return {
            'age': person.age,
            'gender': person.gender,
            'monthly_income': person.monthly_income or 0,
            'employment_status': person.employment_status,
            'is_pregnant': person.is_pregnant,
            'has_children_under_5': person.has_children_under_5,
            'household_size': person.household_size or 1,
            'education_level': person.education_level,
            'has_health_insurance': person.has_health_insurance,
            'province': person.province,
            'zone_type': person.zone_type,
            'has_disability': person.has_disability,
            'emergency_status': getattr(person, 'emergency_status', False)
        }
    
    def _prepare_vulnerability_data(self, vulnerability_assessment):
        """Préparation données vulnérabilité"""
        return {
            'global_score': float(vulnerability_assessment.global_score),
            'vulnerability_level': vulnerability_assessment.vulnerability_level,
            'dimension_scores': vulnerability_assessment.dimension_scores
        }
    
    def _save_eligibility_results(self, person, vulnerability_assessment, 
                                 eligibility_results, user):
        """Sauvegarde résultats éligibilité en base"""
        saved_assessments = []
        
        for program_code, result in eligibility_results.items():
            try:
                program = SocialProgram.objects.get(code=program_code)
                
                # Mise à jour ou création
                assessment, created = ProgramEligibilityAssessment.objects.update_or_create(
                    person=person,
                    program=program,
                    vulnerability_assessment=vulnerability_assessment,
                    defaults={
                        'eligibility_score': result.eligibility_score,
                        'compatibility_score': result.compatibility_score,
                        'recommendation_status': result.recommendation_status.value,
                        'intervention_urgency': result.intervention_urgency.value,
                        'estimated_monthly_benefit': result.estimated_monthly_benefit,
                        'estimated_annual_cost': result.estimated_monthly_benefit * 12,
                        'processing_priority': result.processing_priority,
                        'estimated_impact': result.estimated_impact,
                        'eligibility_factors': result.eligibility_factors,
                        'blocking_factors': result.blocking_factors,
                        'required_documents': result.required_documents,
                        'assessed_by': user,
                        'criteria_snapshot': program.eligibility_criteria
                    }
                )
                saved_assessments.append(assessment)
                
            except SocialProgram.DoesNotExist:
                continue
        
        return saved_assessments
    
    def _format_eligibility_result(self, result):
        """Formatage résultat pour API"""
        return {
            'program_code': result.program_code,
            'program_name': result.program_name,
            'eligibility_score': result.eligibility_score,
            'compatibility_score': result.compatibility_score,
            'recommendation_status': result.recommendation_status.value,
            'intervention_urgency': result.intervention_urgency.value,
            'estimated_monthly_benefit': float(result.estimated_monthly_benefit),
            'processing_priority': result.processing_priority,
            'estimated_impact': result.estimated_impact,
            'eligibility_factors': result.eligibility_factors,
            'blocking_factors': result.blocking_factors,
            'required_documents': result.required_documents
        }


