# ===================================================================
# RSU GABON - VIEWSETS PROGRAMMES PARAMÉTRABLES
# APIs pour gestion administrative programmes sociaux
# ===================================================================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models, transaction
from django.utils import timezone

from .models import SocialProgram, ProgramBudgetHistory
from .serializers import SocialProgramSerializer, ProgramBudgetHistorySerializer
from apps.core_app.permissions import IsAdminOrManagerPermission


class SocialProgramViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gestion administrative programmes sociaux
    
    Fonctionnalités:
    - CRUD complet programmes (Admin seulement)
    - Modification budgets avec historique
    - Surveillance statut programmes
    - Statistiques budgétaires temps réel
    """
    permission_classes = [IsAuthenticated, IsAdminOrManagerPermission]
    queryset = SocialProgram.objects.all()
    serializer_class = SocialProgramSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'is_active', 'program_type', 'priority_level', 
        'responsible_ministry'
    ]

    @action(detail=True, methods=['post'])
    def modify_budget(self, request, pk=None):
        """
        Modification budget programme avec historique
        
        Body: {
            "new_budget_total": decimal,
            "new_benefit_amount": decimal,
            "change_reason": string,
            "change_type": string,
            "effective_date": date (optionnel)
        }
        """
        program = self.get_object()
        
        new_budget_total = request.data.get('new_budget_total')
        new_benefit_amount = request.data.get('new_benefit_amount')
        change_reason = request.data.get('change_reason', '')
        change_type = request.data.get('change_type', 'ADJUSTMENT')
        effective_date = request.data.get('effective_date', timezone.now().date())
        
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
                # Sauvegarder historique AVANT modification
                ProgramBudgetHistory.objects.create(
                    program=program,
                    previous_budget_total=program.budget_total_fcfa,
                    previous_benefit_amount=program.benefit_amount_fcfa,
                    new_budget_total=new_budget_total,
                    new_benefit_amount=new_benefit_amount,
                    change_reason=change_reason,
                    change_type=change_type,
                    approved_by=request.user,
                    effective_date=effective_date,
                    created_by=request.user
                )
                
                # Appliquer modifications
                old_budget = program.budget_total_fcfa
                old_benefit = program.benefit_amount_fcfa
                
                program.budget_total_fcfa = new_budget_total
                program.benefit_amount_fcfa = new_benefit_amount
                program.save(update_fields=['budget_total_fcfa', 'benefit_amount_fcfa'])
                
                return Response({
                    'success': True,
                    'message': f'Budget programme {program.name} modifié avec succès',
                    'changes': {
                        'budget_change': float(new_budget_total - old_budget),
                        'benefit_change': float(new_benefit_amount - old_benefit),
                        'new_budget_total': float(new_budget_total),
                        'new_benefit_amount': float(new_benefit_amount),
                        'effective_date': str(effective_date)
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
        
        history = ProgramBudgetHistory.objects.filter(
            program=program
        ).order_by('-created_at')
        
        serializer = ProgramBudgetHistorySerializer(history, many=True)
        
        return Response({
            'success': True,
            'program': {
                'id': program.id,
                'name': program.name,
                'code': program.code
            },
            'history_count': history.count(),
            'history': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def add_beneficiary(self, request, pk=None):
        """
        Ajouter bénéficiaire avec mise à jour budget
        
        Body: {
            "person_id": integer,
            "enrollment_notes": string (optionnel)
        }
        """
        program = self.get_object()
        person_id = request.data.get('person_id')
        
        if not person_id:
            return Response(
                {'error': 'person_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Vérifier si programme peut accepter nouveau bénéficiaire
            if not program.can_accept_new_beneficiaries:
                return Response({
                    'success': False,
                    'error': 'Programme ne peut pas accepter nouveaux bénéficiaires',
                    'reason': {
                        'budget_available': program.is_budget_available,
                        'capacity_available': (
                            program.max_beneficiaries is None or 
                            program.current_beneficiaries < program.max_beneficiaries
                        ),
                        'program_active': program.is_active,
                        'current_beneficiaries': program.current_beneficiaries,
                        'max_beneficiaries': program.max_beneficiaries,
                        'budget_remaining': float(program.budget_remaining_fcfa)
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Ajouter bénéficiaire
            success = program.add_beneficiary()
            
            if success:
                return Response({
                    'success': True,
                    'message': f'Bénéficiaire ajouté au programme {program.name}',
                    'program_status': {
                        'current_beneficiaries': program.current_beneficiaries,
                        'budget_used': float(program.budget_used_fcfa),
                        'budget_remaining': float(program.budget_remaining_fcfa),
                        'utilization_percentage': program.budget_utilization_percentage
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Impossible d\'ajouter bénéficiaire'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': f'Erreur ajout bénéficiaire: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def remove_beneficiary(self, request, pk=None):
        """
        Retirer bénéficiaire avec ajustement budget
        
        Body: {
            "person_id": integer,
            "refund_budget": boolean (défaut: true),
            "removal_reason": string
        }
        """
        program = self.get_object()
        refund_budget = request.data.get('refund_budget', True)
        removal_reason = request.data.get('removal_reason', '')
        
        try:
            # Retirer bénéficiaire
            program.remove_beneficiary(refund_budget=refund_budget)
            
            return Response({
                'success': True,
                'message': f'Bénéficiaire retiré du programme {program.name}',
                'budget_refunded': refund_budget,
                'removal_reason': removal_reason,
                'program_status': {
                    'current_beneficiaries': program.current_beneficiaries,
                    'budget_used': float(program.budget_used_fcfa),
                    'budget_remaining': float(program.budget_remaining_fcfa),
                    'utilization_percentage': program.budget_utilization_percentage
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur retrait bénéficiaire: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
                total=models.Sum('budget_total_fcfa')
            )['total'] or 0
            
            total_used = active_programs.aggregate(
                total=models.Sum('budget_used_fcfa')
            )['total'] or 0
            
            total_beneficiaries = active_programs.aggregate(
                total=models.Sum('current_beneficiaries')
            )['total'] or 0
            
            # Programmes à risque (>90% budget utilisé)
            critical_programs = active_programs.filter(
                budget_used_fcfa__gte=models.F('budget_total_fcfa') * 0.9
            ).values('name', 'code', 'budget_utilization_percentage')
            
            # Programmes avec plus de capacité
            available_programs = active_programs.filter(
                budget_used_fcfa__lt=models.F('budget_total_fcfa') * 0.7
            ).count()
            
            # Distribution par type
            programs_by_type = list(
                active_programs.values('program_type')
                .annotate(
                    count=models.Count('id'),
                    total_budget=models.Sum('budget_total_fcfa'),
                    total_beneficiaries=models.Sum('current_beneficiaries')
                )
                .order_by('-total_budget')
            )
            
            # Évolution récente (derniers changements budget)
            recent_changes = ProgramBudgetHistory.objects.filter(
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
                        'programs_at_risk_percentage': (
                            len(critical_programs) / total_programs * 100 
                            if total_programs > 0 else 0
                        )
                    },
                    'distribution_by_type': programs_by_type,
                    'recent_activity': {
                        'budget_changes_last_30_days': recent_changes,
                        'dashboard_generated_at': timezone.now().isoformat()
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur génération dashboard: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def activate_program(self, request, pk=None):
        """Activer programme social"""
        program = self.get_object()
        
        if program.is_active:
            return Response({
                'success': False,
                'message': f'Programme {program.name} déjà actif'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        program.is_active = True
        program.save(update_fields=['is_active'])
        
        return Response({
            'success': True,
            'message': f'Programme {program.name} activé avec succès',
            'program': self.get_serializer(program).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def deactivate_program(self, request, pk=None):
        """
        Désactiver programme social
        
        Body: {
            "deactivation_reason": string,
            "stop_new_enrollments_only": boolean (défaut: false)
        }
        """
        program = self.get_object()
        deactivation_reason = request.data.get('deactivation_reason', '')
        stop_enrollments_only = request.data.get('stop_new_enrollments_only', False)
        
        if not program.is_active:
            return Response({
                'success': False,
                'message': f'Programme {program.name} déjà inactif'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if stop_enrollments_only:
            # Arrêter seulement nouvelles inscriptions (budget à 0)
            program.budget_total_fcfa = program.budget_used_fcfa
        else:
            # Désactivation complète
            program.is_active = False
        
        program.save()
        
        return Response({
            'success': True,
            'message': f'Programme {program.name} {"suspendu" if stop_enrollments_only else "désactivé"}',
            'deactivation_reason': deactivation_reason,
            'program': self.get_serializer(program).data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def export_programs_report(self, request):
        """
        Export rapport complet programmes (format structuré)
        Prêt pour Excel/PDF
        """
        try:
            programs = self.queryset.filter(is_active=True)
            
            programs_data = []
            for program in programs:
                programs_data.append({
                    'Code': program.code,
                    'Nom': program.name,
                    'Type': program.get_program_type_display(),
                    'Ministère Responsable': program.responsible_ministry,
                    'Budget Total (FCFA)': float(program.budget_total_fcfa),
                    'Budget Utilisé (FCFA)': float(program.budget_used_fcfa),
                    'Budget Restant (FCFA)': float(program.budget_remaining_fcfa),
                    'Utilisation (%)': round(program.budget_utilization_percentage, 1),
                    'Bénéficiaires Actuels': program.current_beneficiaries,
                    'Bénéficiaires Max': program.max_beneficiaries or 'Illimité',
                    'Montant Bénéfice (FCFA)': float(program.benefit_amount_fcfa),
                    'Durée (mois)': program.duration_months,
                    'Provinces Cibles': ', '.join(program.target_provinces) if program.target_provinces else 'Toutes',
                    'Inscription Auto': 'Oui' if program.automated_enrollment else 'Non',
                    'Niveau Priorité': program.get_priority_level_display(),
                    'Date Début': program.start_date.strftime('%d/%m/%Y'),
                    'Date Fin': program.end_date.strftime('%d/%m/%Y') if program.end_date else 'Permanent',
                    'Contact': program.contact_person or '',
                    'Téléphone': program.contact_phone or '',
                    'Email': program.contact_email or '',
                    'Peut Accepter Nouveaux': 'Oui' if program.can_accept_new_beneficiaries else 'Non',
                    'Bénéficiaires Possibles Restants': program.estimated_beneficiaries_possible
                })
            
            return Response({
                'success': True,
                'export_data': {
                    'generated_at': timezone.now().isoformat(),
                    'total_programs': len(programs_data),
                    'programs': programs_data
                },
                'message': 'Rapport programmes exporté avec succès'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur export rapport: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_queryset(self):
        """Queryset optimisé avec annotations"""
        return super().get_queryset().select_related(
            'created_by', 'updated_by'
        ).annotate(
            budget_utilization_percentage=models.Case(
                models.When(
                    budget_total_fcfa__gt=0,
                    then=models.F('budget_used_fcfa') / models.F('budget_total_fcfa') * 100
                ),
                default=0,
                output_field=models.FloatField()
            )
        )


class ProgramBudgetHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet lecture seule pour historique budgets
    Audit trail complet pour gouvernance
    """
    permission_classes = [IsAuthenticated, IsAdminOrManagerPermission]
    queryset = ProgramBudgetHistory.objects.select_related(
        'program', 'approved_by', 'created_by'
    )
    serializer_class = ProgramBudgetHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'program', 'change_type', 'approved_by', 'effective_date'
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
            float(change.new_budget_total - change.previous_budget_total)
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
            float(change.new_budget_total - change.previous_budget_total)
            for change in queryset
        ])
        
        # Modifications par administrateur
        by_admin = queryset.values(
            'approved_by__username', 'approved_by__full_name'
        ).annotate(
            changes_count=models.Count('id'),
            total_budget_impact=models.Sum(
                models.F('new_budget_total') - models.F('previous_budget_total')
            )
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