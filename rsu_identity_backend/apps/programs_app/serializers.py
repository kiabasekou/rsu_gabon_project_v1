"""
🇬🇦 RSU Gabon - Programs App Serializers
Standards Top 1% - Validation et Sérialisation
Fichier: rsu_identity_backend/apps/programs_app/serializers.py
"""

from rest_framework import serializers
from .models import ProgramCategory, SocialProgram, ProgramEnrollment, Payment
from apps.identity_app.models import PersonIdentity


class ProgramCategorySerializer(serializers.ModelSerializer):
    """Serializer pour catégories de programmes"""
    
    programs_count = serializers.IntegerField(
        source='programs.count',
        read_only=True
    )
    
    class Meta:
        model = ProgramCategory
        fields = [
            'id', 'name', 'description', 'icon',
            'programs_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SocialProgramListSerializer(serializers.ModelSerializer):
    """Serializer pour liste programmes (léger)"""
    
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    managed_by_name = serializers.CharField(
        source='managed_by.get_full_name',
        read_only=True
    )
    
    # Propriétés calculées
    is_active = serializers.BooleanField(read_only=True)
    budget_remaining = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    capacity_remaining = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SocialProgram
        fields = [
            'id', 'code', 'name', 'category', 'category_name',
            'status', 'start_date', 'end_date',
            'total_budget', 'budget_spent', 'budget_remaining',
            'benefit_amount', 'frequency',
            'max_beneficiaries', 'current_beneficiaries', 'capacity_remaining',
            'is_active', 'is_full',
            'managed_by', 'managed_by_name',
            'created_at'
        ]
        read_only_fields = [
            'budget_spent', 'current_beneficiaries',
            'is_active', 'budget_remaining', 'capacity_remaining', 'is_full'
        ]


class SocialProgramDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour programmes"""
    
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    managed_by_name = serializers.CharField(
        source='managed_by.get_full_name',
        read_only=True
    )
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    
    # Propriétés calculées
    is_active = serializers.BooleanField(read_only=True)
    budget_remaining = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    capacity_remaining = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    
    # Statistiques
    enrollments_count = serializers.IntegerField(
        source='enrollments.count',
        read_only=True
    )
    active_enrollments_count = serializers.SerializerMethodField()
    total_payments = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialProgram
        fields = '__all__'
        read_only_fields = [
            'budget_spent', 'current_beneficiaries',
            'is_active', 'budget_remaining', 'capacity_remaining', 'is_full',
            'created_at', 'updated_at'
        ]
    
    def get_active_enrollments_count(self, obj):
        return obj.enrollments.filter(status='ACTIVE').count()
    
    def get_total_payments(self, obj):
        return obj.payments.filter(status='COMPLETED').aggregate(
            total=serializers.models.Sum('amount')
        )['total'] or 0
    
    def validate(self, data):
        """Validation programme"""
        # Vérifier dates
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({
                    'end_date': "La date de fin doit être après la date de début"
                })
        
        # Vérifier budget
        if data.get('benefit_amount') and data.get('total_budget'):
            if data['benefit_amount'] > data['total_budget']:
                raise serializers.ValidationError({
                    'benefit_amount': "Le montant unitaire ne peut dépasser le budget total"
                })
        
        return data


class ProgramEnrollmentListSerializer(serializers.ModelSerializer):
    """Serializer pour liste enrollments"""
    
    program_name = serializers.CharField(
        source='program.name',
        read_only=True
    )
    program_code = serializers.CharField(
        source='program.code',
        read_only=True
    )
    beneficiary_name = serializers.CharField(
        source='beneficiary.full_name',
        read_only=True
    )
    beneficiary_rsu_id = serializers.CharField(
        source='beneficiary.rsu_id',
        read_only=True
    )
    
    class Meta:
        model = ProgramEnrollment
        fields = [
            'id', 'program', 'program_name', 'program_code',
            'beneficiary', 'beneficiary_name', 'beneficiary_rsu_id',
            'status', 'enrollment_date', 'approval_date',
            'eligibility_score', 'total_received', 'payments_count',
            'created_at'
        ]
        read_only_fields = [
            'total_received', 'payments_count', 'created_at'
        ]


class ProgramEnrollmentDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour enrollments"""
    
    program_name = serializers.CharField(
        source='program.name',
        read_only=True
    )
    beneficiary_name = serializers.CharField(
        source='beneficiary.full_name',
        read_only=True
    )
    household_name = serializers.CharField(
        source='household.name',
        read_only=True
    )
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name',
        read_only=True
    )
    
    # Paiements récents
    recent_payments = serializers.SerializerMethodField()
    
    class Meta:
        model = ProgramEnrollment
        fields = '__all__'
        read_only_fields = [
            'total_received', 'payments_count',
            'created_at', 'updated_at'
        ]
    
    def get_recent_payments(self, obj):
        """5 derniers paiements"""
        payments = obj.payments.order_by('-scheduled_date')[:5]
        return PaymentSerializer(payments, many=True).data
    
    def validate(self, data):
        """Validation enrollment"""
        program = data.get('program')
        beneficiary = data.get('beneficiary')
        
        # Vérifier si programme est actif
        if program and not program.is_active:
            raise serializers.ValidationError({
                'program': "Ce programme n'est pas actif"
            })
        
        # Vérifier si programme est plein
        if program and program.is_full:
            raise serializers.ValidationError({
                'program': "Ce programme a atteint sa capacité maximale"
            })
        
        # Vérifier doublon (si création)
        if not self.instance and program and beneficiary:
            if ProgramEnrollment.objects.filter(
                program=program,
                beneficiary=beneficiary
            ).exists():
                raise serializers.ValidationError(
                    "Ce bénéficiaire est déjà inscrit à ce programme"
                )
        
        return data


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer pour paiements"""
    
    beneficiary_name = serializers.CharField(
        source='beneficiary.full_name',
        read_only=True
    )
    program_name = serializers.CharField(
        source='program.name',
        read_only=True
    )
    processed_by_name = serializers.CharField(
        source='processed_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = [
            'processed_date', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Validation paiement"""
        enrollment = data.get('enrollment')
        
        # Vérifier que l'enrollment est actif
        if enrollment and enrollment.status != 'ACTIVE':
            raise serializers.ValidationError({
                'enrollment': "L'inscription n'est pas active"
            })
        
        # Vérifier montant
        if data.get('amount'):
            program = data.get('program') or enrollment.program
            if data['amount'] > program.benefit_amount:
                raise serializers.ValidationError({
                    'amount': f"Le montant ne peut dépasser {program.benefit_amount} FCFA"
                })
        
        return data


class EligibilityCheckSerializer(serializers.Serializer):
    """Serializer pour vérification éligibilité"""
    
    beneficiary_id = serializers.IntegerField()
    program_id = serializers.IntegerField()
    
    def validate_beneficiary_id(self, value):
        if not PersonIdentity.objects.filter(id=value).exists():
            raise serializers.ValidationError("Bénéficiaire introuvable")
        return value
    
    def validate_program_id(self, value):
        if not SocialProgram.objects.filter(id=value).exists():
            raise serializers.ValidationError("Programme introuvable")
        return value