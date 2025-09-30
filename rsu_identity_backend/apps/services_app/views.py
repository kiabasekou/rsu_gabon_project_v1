# ===================================================================
# RSU GABON - VIEWSETS SERVICES APP - IMPORTS CORRIGÉS
# Correction: ProgramBudgetHistory → ProgramBudgetChange
# ===================================================================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models, transaction
from django.utils import timezone
from .services import VulnerabilityService, EligibilityService, GeotargetingService


# ✅ CORRECTION: Import des bons modèles et serializers
from .models import (
    SocialProgram, 
    ProgramBudgetChange, 
    SocialProgramEligibility, 
    VulnerabilityAssessment
)
from .serializers import (
    SocialProgramSerializer, 
    ProgramBudgetChangeSerializer,
    SocialProgramEligibilitySerializer,
    VulnerabilityAssessmentSerializer
)
from rest_framework.permissions import IsAdminUser

# ✅ CORRECTION: Import des bons modèles et serializers
from .models import (
    SocialProgram, 
    ProgramBudgetChange, 
    SocialProgramEligibility, 
    VulnerabilityAssessment
)
from .serializers import (
    SocialProgramSerializer, 
    ProgramBudgetChangeSerializer,
    SocialProgramEligibilitySerializer,
    VulnerabilityAssessmentSerializer
)

class SocialProgramViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gestion administrative programmes sociaux
    
    Fonctionnalités:
    - CRUD complet programmes (Admin seulement)
    - Modification budgets avec historique
    - Surveillance statut programmes
    - Statistiques budgétaires temps réel
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = SocialProgram.objects.all()
    serializer_class = SocialProgramSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'is_active', 'program_type', 'automated_enrollment'
    ]

    @action(detail=True, methods=['post'])
    def modify_budget(self, request, pk=None):
        """
        Modification budget programme avec historique
        
        Body: {
            "new_budget_total": decimal,
            "new_benefit_amount": decimal,
            "change_reason": string,
            "change_type": string
        }
        """
        program = self.get_object()
        
        new_budget_total = request.data.get('new_budget_total')
        new_benefit_amount = request.data.get('new_benefit_amount')
        change_reason = request.data.get('change_reason', '')
        change_type = request.data.get('change_type', 'ADJUSTMENT')
        
        # Validations
        if not new_budget_total or not new_benefit_amount:
            return Response(
                {'error': 'new_budget_total et new_benefit_amount requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not change_reason:
            return Response(
                {'error': 'change_reason requis pour traçabilité'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # ✅ CORRECTION: Utilisation de ProgramBudgetChange
                ProgramBudgetChange.objects.create(
                    program=program,
                    previous_budget_total=program.annual_budget,
                    new_budget_total=new_budget_total,
                    amount_change_fcfa=new_budget_total - program.annual_budget,
                    change_type=change_type,
                    justification=change_reason,
                    budget_source='Ajustement administrateur',
                    approved_by=request.user,
                    created_by=request.user
                )
                
                # Appliquer modifications
                old_budget = program.annual_budget
                old_benefit = program.benefit_amount_fcfa
                
                program.annual_budget = new_budget_total
                program.benefit_amount_fcfa = new_benefit_amount
                program.save(update_fields=['annual_budget', 'benefit_amount_fcfa'])
                
                return Response({
                    'success': True,
                    'message': f'Budget programme {program.name} modifié avec succès',
                    'changes': {
                        'budget_change': float(new_budget_total - old_budget),
                        'benefit_change': float(new_benefit_amount - old_benefit),
                        'new_budget_total': float(new_budget_total),
                        'new_benefit_amount': float(new_benefit_amount)
                    },
                    'updated_program': self.get_serializer(program).data
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': f'Erreur modification budget: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def budget_history(self, request, pk=None):
        """Historique des modifications budgétaires"""
        program = self.get_object()
        
        # ✅ CORRECTION: Utilisation de ProgramBudgetChange
        history = ProgramBudgetChange.objects.filter(
            program=program
        ).order_by('-created_at')
        
        serializer = ProgramBudgetChangeSerializer(history, many=True)
        
        return Response({
            'success': True,
            'program': program.name,
            'budget_history': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def budget_dashboard(self, request):
        """
        Dashboard global budgets tous programmes
        Vue d'ensemble pour administrateurs
        """
        try:
            active_programs = self.queryset.filter(is_active=True)
            
            # Statistiques globales
            total_programs = active_programs.count()
            total_budget = active_programs.aggregate(
                total=models.Sum('annual_budget')
            )['total'] or 0
            
            total_used = active_programs.aggregate(
                total=models.Sum('budget_used_fcfa')
            )['total'] or 0
            
            total_beneficiaries = active_programs.aggregate(
                total=models.Sum('current_beneficiaries')
            )['total'] or 0
            
            # Programmes à risque (>90% budget utilisé)
            critical_programs = active_programs.filter(
                budget_used_fcfa__gte=models.F('annual_budget') * 0.9
            ).values('name', 'code')
            
            # Programmes avec capacité
            available_programs = active_programs.filter(
                budget_used_fcfa__lt=models.F('annual_budget') * 0.7
            ).count()
            
            # ✅ CORRECTION: Utilisation de ProgramBudgetChange
            recent_changes = ProgramBudgetChange.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count()
            
            return Response({
                'success': True,
                'dashboard_data': {
                    'overview': {
                        'total_programs': total_programs,
                        'total_budget_fcfa': float(total_budget),
                        'total_used_fcfa': float(total_used),
                        'total_remaining_fcfa': float(total_budget - total_used),
                        'global_utilization_percentage': (
                            (total_used / total_budget * 100) if total_budget > 0 else 0
                        ),
                        'total_beneficiaries': total_beneficiaries
                    },
                    'risk_analysis': {
                        'critical_programs_count': len(critical_programs),
                        'critical_programs': list(critical_programs),
                        'available_programs_count': available_programs,
                        'recent_budget_changes': recent_changes
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur dashboard: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProgramBudgetChangeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ✅ CORRECTION: ViewSet pour ProgramBudgetChange (pas History)
    Audit trail complet pour gouvernance
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = ProgramBudgetChange.objects.select_related(
        'program', 'approved_by', 'created_by'
    )
    serializer_class = ProgramBudgetChangeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'program', 'change_type', 'approved_by'
    ]

    @action(detail=False, methods=['get'])
    def recent_changes(self, request):
        """Changements budgétaires récents (30 derniers jours)"""
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_changes = self.queryset.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')
        
        serializer = self.get_serializer(recent_changes, many=True)
        
        # Statistiques changements
        total_changes = recent_changes.count()
        changes_by_type = recent_changes.values('change_type').annotate(
            count=models.Count('id')
        ).order_by('-count')
        
        # Impact budgétaire total
        budget_impact = sum([
            float(change.amount_change_fcfa)
            for change in recent_changes
        ])
        
        return Response({
            'success': True,
            'period': '30 derniers jours',
            'statistics': {
                'total_changes': total_changes,
                'changes_by_type': list(changes_by_type),
                'total_budget_impact_fcfa': budget_impact,
                'average_changes_per_day': round(total_changes / 30, 1)
            },
            'recent_changes': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def audit_report(self, request):
        """
        Rapport d'audit complet modifications budgétaires
        Pour contrôles gouvernementaux
        """
        # Filtres optionnels
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        program_id = request.query_params.get('program_id')
        
        queryset = self.queryset
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        if program_id:
            queryset = queryset.filter(program_id=program_id)
        
        # Statistiques audit
        total_modifications = queryset.count()
        total_budget_changes = sum([
            float(change.amount_change_fcfa)
            for change in queryset
        ])
        
        # Modifications par administrateur
        by_admin = queryset.values(
            'approved_by__username', 'approved_by__full_name'
        ).annotate(
            changes_count=models.Count('id'),
            total_budget_impact=models.Sum('amount_change_fcfa')
        ).order_by('-changes_count')
        
        # Modifications par programme
        by_program = queryset.values(
            'program__name', 'program__code'
        ).annotate(
            changes_count=models.Count('id')
        ).order_by('-changes_count')
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'audit_period': {
                'start_date': start_date or 'Début',
                'end_date': end_date or 'Fin',
                'program_filter': program_id
            },
            'audit_summary': {
                'total_modifications': total_modifications,
                'total_budget_changes_fcfa': total_budget_changes,
                'modifications_by_admin': list(by_admin),
                'modifications_by_program': list(by_program)
            },
            'detailed_history': serializer.data,
            'generated_at': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

# ===================================================================
# VIEWSETS ADDITIONNELS
# ===================================================================

class SocialProgramEligibilityViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gestion éligibilités programmes
    """
    permission_classes = [IsAuthenticated]
    queryset = SocialProgramEligibility.objects.select_related('person')
    serializer_class = SocialProgramEligibilitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'program_code', 'recommendation_level', 'processing_priority',
        'intervention_urgency', 'person'
    ]

    def get_queryset(self):
        """Queryset optimisé"""
        return super().get_queryset().select_related(
            'person', 'created_by', 'updated_by'
        ).order_by('-assessment_date')
    
        
    @action(detail=False, methods=['post'])
    def calculate_eligibility(self, request):
        """Calcule éligibilité personne/programme"""
        person_id = request.data.get('person_id')
        program_code = request.data.get('program_code')
        
        service = EligibilityService()
        eligibility = service.calculate_program_eligibility(
            person_id=person_id,
            program_code=program_code
        )
        
        serializer = self.get_serializer(eligibility)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recommended_programs(self, request):
        """Programmes recommandés pour une personne"""
        person_id = request.query_params.get('person_id')
        min_score = float(request.query_params.get('min_score', 60.0))
        
        service = EligibilityService()
        recommended = service.get_recommended_programs(
            person_id=int(person_id),
            min_score=min_score
        )
        return Response(recommended)


class VulnerabilityAssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour évaluations vulnérabilité
    """
    permission_classes = [IsAuthenticated]
    queryset = VulnerabilityAssessment.objects.select_related('person')
    serializer_class = VulnerabilityAssessmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'risk_level', 'person', 'assessment_date'
    ]

    def get_queryset(self):
        """Queryset optimisé"""
        return super().get_queryset().select_related(
            'person', 'created_by', 'updated_by'
        ).order_by('-assessment_date')


    @action(detail=False, methods=['get'])
    def risk_statistics(self, request):
        """Statistiques niveaux de risque"""
        try:
            risk_stats = self.queryset.values('risk_level').annotate(
                count=models.Count('id')
            ).order_by('-count')
            
            return Response({
                'success': True,
                'risk_distribution': list(risk_stats),
                'total_assessments': self.queryset.count()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Erreur modification budget: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def budget_history(self, request, pk=None):
        """Historique des modifications budgétaires"""
        program = self.get_object()
        
        # ✅ CORRECTION: Utilisation de ProgramBudgetChange
        history = ProgramBudgetChange.objects.filter(
            program=program
        ).order_by('-created_at')
        
        serializer = ProgramBudgetChangeSerializer(history, many=True)
        
        return Response({
            'success': True,
            'program': program.name,
            'budget_history': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def budget_dashboard(self, request):
        """
        Dashboard global budgets tous programmes
        Vue d'ensemble pour administrateurs
        """
        try:
            active_programs = self.queryset.filter(is_active=True)
            
            # Statistiques globales
            total_programs = active_programs.count()
            total_budget = active_programs.aggregate(
                total=models.Sum('annual_budget')
            )['total'] or 0
            
            total_used = active_programs.aggregate(
                total=models.Sum('budget_used_fcfa')
            )['total'] or 0
            
            total_beneficiaries = active_programs.aggregate(
                total=models.Sum('current_beneficiaries')
            )['total'] or 0
            
            # Programmes à risque (>90% budget utilisé)
            critical_programs = active_programs.filter(
                budget_used_fcfa__gte=models.F('annual_budget') * 0.9
            ).values('name', 'code')
            
            # Programmes avec capacité
            available_programs = active_programs.filter(
                budget_used_fcfa__lt=models.F('annual_budget') * 0.7
            ).count()
            
            # ✅ CORRECTION: Utilisation de ProgramBudgetChange
            recent_changes = ProgramBudgetChange.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count()
            
            return Response({
                'success': True,
                'dashboard_data': {
                    'overview': {
                        'total_programs': total_programs,
                        'total_budget_fcfa': float(total_budget),
                        'total_used_fcfa': float(total_used),
                        'total_remaining_fcfa': float(total_budget - total_used),
                        'global_utilization_percentage': (
                            (total_used / total_budget * 100) if total_budget > 0 else 0
                        ),
                        'total_beneficiaries': total_beneficiaries
                    },
                    'risk_analysis': {
                        'critical_programs_count': len(critical_programs),
                        'critical_programs': list(critical_programs),
                        'available_programs_count': available_programs,
                        'recent_budget_changes': recent_changes
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur dashboard: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=False, methods=['post'])
    def bulk_calculate(self, request):
        """Calcul en masse des évaluations"""
        person_ids = request.data.get('person_ids', [])
        service = VulnerabilityService()
        results = service.bulk_calculate_assessments(person_ids)
        return Response(results)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques vulnérabilité"""
        province = request.query_params.get('province')
        service = VulnerabilityService()
        stats = service.get_vulnerability_statistics(province=province)
        return Response(stats)

class ProgramBudgetChangeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ✅ CORRECTION: ViewSet pour ProgramBudgetChange (pas History)
    Audit trail complet pour gouvernance
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = ProgramBudgetChange.objects.select_related(
        'program', 'approved_by', 'created_by'
    )
    serializer_class = ProgramBudgetChangeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'program', 'change_type', 'approved_by'
    ]

    @action(detail=False, methods=['get'])
    def recent_changes(self, request):
        """Changements budgétaires récents (30 derniers jours)"""
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_changes = self.queryset.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')
        
        serializer = self.get_serializer(recent_changes, many=True)
        
        # Statistiques changements
        total_changes = recent_changes.count()
        changes_by_type = recent_changes.values('change_type').annotate(
            count=models.Count('id')
        ).order_by('-count')
        
        # Impact budgétaire total
        budget_impact = sum([
            float(change.amount_change_fcfa)
            for change in recent_changes
        ])
        
        return Response({
            'success': True,
            'period': '30 derniers jours',
            'statistics': {
                'total_changes': total_changes,
                'changes_by_type': list(changes_by_type),
                'total_budget_impact_fcfa': budget_impact,
                'average_changes_per_day': round(total_changes / 30, 1)
            },
            'recent_changes': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def audit_report(self, request):
        """
        Rapport d'audit complet modifications budgétaires
        Pour contrôles gouvernementaux
        """
        # Filtres optionnels
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        program_id = request.query_params.get('program_id')
        
        queryset = self.queryset
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        if program_id:
            queryset = queryset.filter(program_id=program_id)
        
        # Statistiques audit
        total_modifications = queryset.count()
        total_budget_changes = sum([
            float(change.amount_change_fcfa)
            for change in queryset
        ])
        
        # Modifications par administrateur
        by_admin = queryset.values(
            'approved_by__username', 'approved_by__full_name'
        ).annotate(
            changes_count=models.Count('id'),
            total_budget_impact=models.Sum('amount_change_fcfa')
        ).order_by('-changes_count')
        
        # Modifications par programme
        by_program = queryset.values(
            'program__name', 'program__code'
        ).annotate(
            changes_count=models.Count('id')
        ).order_by('-changes_count')
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'audit_period': {
                'start_date': start_date or 'Début',
                'end_date': end_date or 'Fin',
                'program_filter': program_id
            },
            'audit_summary': {
                'total_modifications': total_modifications,
                'total_budget_changes_fcfa': total_budget_changes,
                'modifications_by_admin': list(by_admin),
                'modifications_by_program': list(by_program)
            },
            'detailed_history': serializer.data,
            'generated_at': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)