"""
🇬🇦 RSU Gabon - Programs App Views
Standards Top 1% - APIs REST + Logique Métier
Fichier: rsu_identity_backend/apps/programs_app/views.py
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.utils import timezone

from .models import ProgramCategory, SocialProgram, ProgramEnrollment, Payment
from .serializers import (
    ProgramCategorySerializer,
    SocialProgramListSerializer,
    SocialProgramDetailSerializer,
    ProgramEnrollmentListSerializer,
    ProgramEnrollmentDetailSerializer,
    PaymentSerializer,
    EligibilityCheckSerializer
)
from apps.identity_app.models import PersonIdentity


class ProgramCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour catégories de programmes"""
    
    queryset = ProgramCategory.objects.all()
    serializer_class = ProgramCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class SocialProgramViewSet(viewsets.ModelViewSet):
    """ViewSet pour programmes sociaux"""
    
    queryset = SocialProgram.objects.select_related(
        'category', 'managed_by', 'created_by'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'managed_by']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['created_at', 'start_date', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SocialProgramListSerializer
        return SocialProgramDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Liste programmes actifs seulement"""
        active_programs = self.get_queryset().filter(
            status='ACTIVE',
            start_date__lte=timezone.now().date()
        )
        
        # Filtrer end_date
        active_programs = active_programs.filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.now().date())
        )
        
        serializer = self.get_serializer(active_programs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Statistiques détaillées du programme"""
        program = self.get_object()
        
        enrollments = program.enrollments.all()
        payments = program.payments.all()
        
        stats = {
            'program_info': {
                'code': program.code,
                'name': program.name,
                'status': program.status,
                'is_active': program.is_active,
            },
            'budget': {
                'total': float(program.total_budget),
                'spent': float(program.budget_spent),
                'remaining': float(program.budget_remaining),
                'percentage_used': round((program.budget_spent / program.total_budget * 100), 2) if program.total_budget > 0 else 0
            },
            'beneficiaries': {
                'current': program.current_beneficiaries,
                'max': program.max_beneficiaries,
                'remaining': program.capacity_remaining,
                'is_full': program.is_full
            },
            'enrollments': {
                'total': enrollments.count(),
                'pending': enrollments.filter(status='PENDING').count(),
                'approved': enrollments.filter(status='APPROVED').count(),
                'active': enrollments.filter(status='ACTIVE').count(),
                'rejected': enrollments.filter(status='REJECTED').count(),
                'completed': enrollments.filter(status='COMPLETED').count(),
            },
            'payments': {
                'total_count': payments.count(),
                'completed': payments.filter(status='COMPLETED').count(),
                'pending': payments.filter(status='PENDING').count(),
                'failed': payments.filter(status='FAILED').count(),
                'total_amount': float(payments.filter(status='COMPLETED').aggregate(
                    total=Sum('amount')
                )['total'] or 0),
            },
            'demographics': self._get_demographics(program),
        }
        
        return Response(stats)
    
    def _get_demographics(self, program):
        """Démographie des bénéficiaires"""
        enrollments = program.enrollments.filter(status__in=['APPROVED', 'ACTIVE'])
        beneficiaries = PersonIdentity.objects.filter(
            program_enrollments__in=enrollments
        )
        
        return {
            'by_gender': {
                'M': beneficiaries.filter(gender='M').count(),
                'F': beneficiaries.filter(gender='F').count(),
                'OTHER': beneficiaries.filter(gender='OTHER').count(),
            },
            'by_province': list(
                beneficiaries.values('province').annotate(
                    count=Count('id')
                ).order_by('-count')
            ),
            'avg_vulnerability_score': beneficiaries.aggregate(
                avg=Sum('vulnerability_score')
            )['avg'] or 0,
        }
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activer un programme"""
        program = self.get_object()
        
        if program.status == 'ACTIVE':
            return Response(
                {'detail': 'Le programme est déjà actif'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        program.status = 'ACTIVE'
        program.save()
        
        return Response({
            'detail': 'Programme activé avec succès',
            'program': self.get_serializer(program).data
        })
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Suspendre un programme"""
        program = self.get_object()
        
        program.status = 'PAUSED'
        program.save()
        
        return Response({
            'detail': 'Programme suspendu',
            'program': self.get_serializer(program).data
        })
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Clôturer un programme"""
        program = self.get_object()
        
        program.status = 'CLOSED'
        program.end_date = timezone.now().date()
        program.save()
        
        return Response({
            'detail': 'Programme clôturé',
            'program': self.get_serializer(program).data
        })


class ProgramEnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet pour inscriptions programmes"""
    
    queryset = ProgramEnrollment.objects.select_related(
        'program', 'beneficiary', 'household', 'approved_by'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'program', 'beneficiary']
    ordering_fields = ['enrollment_date', 'approval_date']
    ordering = ['-enrollment_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProgramEnrollmentListSerializer
        return ProgramEnrollmentDetailSerializer
    
    def perform_create(self, serializer):
        """Création avec calcul score éligibilité"""
        enrollment = serializer.save()
        
        # Calculer score d'éligibilité
        score = self._calculate_eligibility_score(
            enrollment.beneficiary,
            enrollment.program
        )
        enrollment.eligibility_score = score
        enrollment.save()
    
    def _calculate_eligibility_score(self, beneficiary, program):
        """Calcule score de matching avec critères du programme"""
        criteria = program.eligibility_criteria
        score = 0
        max_score = 0
        
        # Score vulnérabilité (40 points)
        max_score += 40
        vuln_min = criteria.get('vulnerability_min', 0)
        if beneficiary.vulnerability_score >= vuln_min:
            score += 40
        
        # Âge (20 points)
        max_score += 20
        age_min = criteria.get('age_min')
        age_max = criteria.get('age_max')
        if beneficiary.age:
            if age_min and age_max:
                if age_min <= beneficiary.age <= age_max:
                    score += 20
            elif age_min and beneficiary.age >= age_min:
                score += 20
            elif age_max and beneficiary.age <= age_max:
                score += 20
        
        # Province (20 points)
        max_score += 20
        target_provinces = criteria.get('provinces', [])
        if not target_provinces or beneficiary.province in target_provinces:
            score += 20
        
        # Genre (10 points)
        max_score += 10
        target_gender = criteria.get('gender')
        if not target_gender or beneficiary.gender == target_gender:
            score += 10
        
        # Taille ménage (10 points)
        max_score += 10
        household_size_min = criteria.get('household_size_min')
        if beneficiary.household:
            if not household_size_min or beneficiary.household.size >= household_size_min:
                score += 10
        
        # Calculer pourcentage
        return round((score / max_score * 100), 2) if max_score > 0 else 0
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approuver une inscription"""
        enrollment = self.get_object()
        
        if enrollment.status != 'PENDING':
            return Response(
                {'detail': 'Seules les inscriptions en attente peuvent être approuvées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier capacité programme
        if enrollment.program.is_full:
            return Response(
                {'detail': 'Le programme a atteint sa capacité maximale'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment.status = 'APPROVED'
        enrollment.approval_date = timezone.now().date()
        enrollment.approved_by = request.user
        enrollment.save()
        
        # Incrémenter compteur bénéficiaires
        program = enrollment.program
        program.current_beneficiaries += 1
        program.save()
        
        return Response({
            'detail': 'Inscription approuvée',
            'enrollment': self.get_serializer(enrollment).data
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rejeter une inscription"""
        enrollment = self.get_object()
        reason = request.data.get('reason', '')
        
        if enrollment.status != 'PENDING':
            return Response(
                {'detail': 'Seules les inscriptions en attente peuvent être rejetées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment.status = 'REJECTED'
        enrollment.rejection_reason = reason
        enrollment.approved_by = request.user
        enrollment.save()
        
        return Response({
            'detail': 'Inscription rejetée',
            'enrollment': self.get_serializer(enrollment).data
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activer une inscription approuvée"""
        enrollment = self.get_object()
        
        if enrollment.status != 'APPROVED':
            return Response(
                {'detail': 'Seules les inscriptions approuvées peuvent être activées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment.status = 'ACTIVE'
        enrollment.start_date = timezone.now().date()
        enrollment.save()
        
        return Response({
            'detail': 'Inscription activée',
            'enrollment': self.get_serializer(enrollment).data
        })
    
    @action(detail=False, methods=['post'])
    def check_eligibility(self, request):
        """Vérifier éligibilité bénéficiaire pour programme"""
        serializer = EligibilityCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        beneficiary = PersonIdentity.objects.get(id=serializer.validated_data['beneficiary_id'])
        program = SocialProgram.objects.get(id=serializer.validated_data['program_id'])
        
        # Calculer score
        score = self._calculate_eligibility_score(beneficiary, program)
        
        # Vérifications
        checks = {
            'is_program_active': program.is_active,
            'is_program_full': program.is_full,
            'is_already_enrolled': ProgramEnrollment.objects.filter(
                program=program,
                beneficiary=beneficiary
            ).exists(),
            'eligibility_score': score,
            'is_eligible': score >= 50,  # Seuil minimum 50%
        }
        
        return Response({
            'beneficiary': {
                'id': beneficiary.id,
                'name': beneficiary.full_name,
                'rsu_id': beneficiary.rsu_id,
            },
            'program': {
                'id': program.id,
                'code': program.code,
                'name': program.name,
            },
            'checks': checks,
            'recommendation': 'ELIGIBLE' if checks['is_eligible'] and checks['is_program_active'] and not checks['is_already_enrolled'] else 'NOT_ELIGIBLE'
        })


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet pour paiements"""
    
    queryset = Payment.objects.select_related(
        'enrollment', 'beneficiary', 'program', 'processed_by'
    ).all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'program', 'beneficiary']
    ordering_fields = ['scheduled_date', 'processed_date', 'amount']
    ordering = ['-scheduled_date']
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Traiter un paiement"""
        payment = self.get_object()
        
        if payment.status not in ['PENDING', 'FAILED']:
            return Response(
                {'detail': 'Ce paiement ne peut pas être traité'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'PROCESSING'
        payment.save()
        
        # Simulation traitement (à remplacer par vraie intégration)
        # En production: appel API Mobile Money, Banque, etc.
        
        payment.status = 'COMPLETED'
        payment.processed_date = timezone.now()
        payment.processed_by = request.user
        payment.save()
        
        # Mettre à jour enrollment
        enrollment = payment.enrollment
        enrollment.total_received += payment.amount
        enrollment.payments_count += 1
        enrollment.save()
        
        # Mettre à jour programme
        program = payment.program
        program.budget_spent += payment.amount
        program.save()
        
        return Response({
            'detail': 'Paiement traité avec succès',
            'payment': self.get_serializer(payment).data
        })
    
    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        """Marquer un paiement comme échoué"""
        payment = self.get_object()
        reason = request.data.get('reason', '')
        
        payment.status = 'FAILED'
        payment.failure_reason = reason
        payment.processed_by = request.user
        payment.save()
        
        return Response({
            'detail': 'Paiement marqué comme échoué',
            'payment': self.get_serializer(payment).data
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Liste paiements en attente"""
        pending_payments = self.get_queryset().filter(status='PENDING')
        
        page = self.paginate_queryset(pending_payments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(pending_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques globales paiements"""
        queryset = self.get_queryset()
        
        stats = {
            'total_count': queryset.count(),
            'by_status': {
                'pending': queryset.filter(status='PENDING').count(),
                'processing': queryset.filter(status='PROCESSING').count(),
                'completed': queryset.filter(status='COMPLETED').count(),
                'failed': queryset.filter(status='FAILED').count(),
                'cancelled': queryset.filter(status='CANCELLED').count(),
            },
            'amounts': {
                'total_processed': float(queryset.filter(
                    status='COMPLETED'
                ).aggregate(total=Sum('amount'))['total'] or 0),
                'total_pending': float(queryset.filter(
                    status='PENDING'
                ).aggregate(total=Sum('amount'))['total'] or 0),
            },
            'by_method': list(
                queryset.filter(status='COMPLETED').values('payment_method').annotate(
                    count=Count('id'),
                    total=Sum('amount')
                )
            ),
        }
        
        return Response(stats)