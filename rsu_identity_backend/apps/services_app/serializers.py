"""
🇬🇦 RSU Gabon - Services App Serializers COMPLET
Version fusionnée : Ancien + Nouveau
Standards Top 1% - Tous les serializers nécessaires
Fichier: rsu_identity_backend/apps/services_app/serializers.py
"""

from rest_framework import serializers
from apps.services_app.models import (
    SocialProgram, 
    SocialProgramEligibility, 
    VulnerabilityAssessment,
    ProgramBudgetChange
)
from apps.identity_app.serializers import PersonIdentityMinimalSerializer
from apps.core_app.serializers import RSUUserMinimalSerializer


# ============================================================================
# SOCIAL PROGRAMS SERIALIZERS (EXISTANT - CONSERVÉ)
# ============================================================================

class SocialProgramSerializer(serializers.ModelSerializer):
    """
    Serializer pour SocialProgram avec budgets ajustables
    """
    
    # Champs calculés
    remaining_budget = serializers.ReadOnlyField()
    budget_utilization_percentage = serializers.ReadOnlyField()
    current_budget_utilization = serializers.ReadOnlyField()
    can_accept_new_beneficiaries = serializers.ReadOnlyField()
    is_budget_available = serializers.ReadOnlyField()
    
    class Meta:
        model = SocialProgram
        fields = [
            'id', 'code', 'name', 'description', 'is_active',
            'annual_budget', 'budget_used_fcfa', 'benefit_amount_fcfa',
            'duration_months', 'max_beneficiaries', 'current_beneficiaries',
            'eligibility_criteria', 'target_provinces', 'urban_rural_preference',
            'program_type', 'automated_enrollment', 'requires_documents',
            # Champs calculés
            'remaining_budget', 'budget_utilization_percentage',
            'current_budget_utilization', 'can_accept_new_beneficiaries',
            'is_budget_available',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'remaining_budget', 'budget_utilization_percentage',
            'current_budget_utilization', 'can_accept_new_beneficiaries',
            'is_budget_available', 'created_at', 'updated_at'
        ]
    
    def validate_annual_budget(self, value):
        """Validation budget annuel"""
        if value <= 0:
            raise serializers.ValidationError("Le budget annuel doit être positif")
        return value
    
    def validate_benefit_amount_fcfa(self, value):
        """Validation montant par bénéficiaire"""
        if value <= 0:
            raise serializers.ValidationError("Le montant par bénéficiaire doit être positif")
        return value
    
    def validate(self, data):
        """Validation croisée des données"""
        annual_budget = data.get('annual_budget', 0)
        benefit_amount = data.get('benefit_amount_fcfa', 0)
        max_beneficiaries = data.get('max_beneficiaries', 0)
        
        # Vérifier cohérence budget/bénéficiaires
        if annual_budget > 0 and benefit_amount > 0 and max_beneficiaries > 0:
            theoretical_max_cost = benefit_amount * max_beneficiaries
            if theoretical_max_cost > annual_budget:
                raise serializers.ValidationError(
                    f"Budget insuffisant: {theoretical_max_cost} FCFA nécessaires "
                    f"pour {max_beneficiaries} bénéficiaires à {benefit_amount} FCFA chacun"
                )
        
        return data


class ProgramBudgetChangeSerializer(serializers.ModelSerializer):
    """
    Serializer pour historique modifications budgétaires
    """
    
    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = ProgramBudgetChange
        fields = [
            'id', 'program', 'program_name', 'program_code',
            'change_type', 'previous_budget_total', 'new_budget_total',
            'amount_change_fcfa', 'justification', 'budget_source',
            'approved_by', 'approved_by_name', 'approval_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'program_name', 'program_code', 'approved_by_name',
            'created_at', 'updated_at'
        ]
    
    def validate_amount_change_fcfa(self, value):
        """Validation montant changement"""
        if value == 0:
            raise serializers.ValidationError("Le montant du changement ne peut pas être zéro")
        return value


# ============================================================================
# ELIGIBILITY SERIALIZERS (FUSIONNÉ - VERSION ENRICHIE)
# ============================================================================

class SocialProgramEligibilitySerializer(serializers.ModelSerializer):
    """
    Serializer pour éligibilité programmes sociaux
    ✅ VERSION ENRICHIE avec détails person et assessed_by
    """
    
    # Relations enrichies
    person_details = PersonIdentityMinimalSerializer(source='person', read_only=True)
    assessed_by_details = RSUUserMinimalSerializer(source='assessed_by', read_only=True)
    
    # Champs calculés (ancien)
    person_name = serializers.CharField(source='person.full_name', read_only=True)
    person_rsu_id = serializers.CharField(source='person.rsu_id', read_only=True)
    
    # Champs display
    eligibility_status_display = serializers.CharField(
        source='get_eligibility_status_display', 
        read_only=True
    )
    
    class Meta:
        model = SocialProgramEligibility
        fields = [
            'id',
            # Person info
            'person', 'person_details', 'person_name', 'person_rsu_id',
            
            # Program info
            'program_name', 'program_category',
            
            # Eligibility
            'eligibility_status', 'eligibility_status_display',
            'eligibility_score', 'matching_criteria', 'missing_criteria',
            'priority_ranking', 'recommendation_notes',
            
            # Assessment
            'assessment_date', 'assessed_by', 'assessed_by_details',
            
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# VULNERABILITY SERIALIZERS (FUSIONNÉ - VERSION ENRICHIE + CRÉATION)
# ============================================================================

class VulnerabilityAssessmentSerializer(serializers.ModelSerializer):
    """
    Serializer pour VulnerabilityAssessment
    ✅ VERSION ENRICHIE avec relations et tous les champs
    """
    
    # Relations enrichies
    person_details = PersonIdentityMinimalSerializer(source='person', read_only=True)
    assessed_by_details = RSUUserMinimalSerializer(source='assessed_by', read_only=True)
    
    # Champs calculés (ancien)
    person_name = serializers.CharField(source='person.full_name', read_only=True)
    person_rsu_id = serializers.CharField(source='person.rsu_id', read_only=True)
    
    # Champs display
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    
    class Meta:
        model = VulnerabilityAssessment
        fields = [
            'id',
            # Person info
            'person', 'person_details', 'person_name', 'person_rsu_id',
            
            # Scores
            'vulnerability_score', 'risk_level', 'risk_level_display',
            'health_vulnerability_score',
            'household_composition_score',
            'economic_vulnerability_score',
            'social_vulnerability_score',
            
            # Factors
            'vulnerability_factors', 'risk_factors', 'protective_factors',
            
            # Recommendations
            'recommendations', 'priority_interventions',
            
            # Assessment info
            'assessment_date', 'assessed_by', 'assessed_by_details',
            'assessment_notes',
            
            # Status
            'is_active',
            
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_vulnerability_score(self, value):
        """Validation score vulnérabilité"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Le score de vulnérabilité doit être entre 0 et 100"
            )
        return value


class VulnerabilityAssessmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour création manuelle d'évaluation vulnérabilité
    ✅ NOUVEAU - Pour création via API
    """
    
    class Meta:
        model = VulnerabilityAssessment
        fields = [
            'person',
            'vulnerability_score',
            'risk_level',
            'health_vulnerability_score',
            'household_composition_score',
            'economic_vulnerability_score',
            'social_vulnerability_score',
            'vulnerability_factors',
            'risk_factors',
            'protective_factors',
            'recommendations',
            'priority_interventions',
            'assessment_notes'
        ]
    
    def validate_vulnerability_score(self, value):
        """Valider score entre 0 et 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Le score de vulnérabilité doit être entre 0 et 100"
            )
        return value


# ============================================================================
# STATISTICS & REPORTS SERIALIZERS (EXISTANT - CONSERVÉ)
# ============================================================================

class ProgramStatisticsSerializer(serializers.Serializer):
    """
    Serializer pour statistiques programmes
    """
    
    total_programs = serializers.IntegerField()
    active_programs = serializers.IntegerField()
    total_budget_fcfa = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_used_fcfa = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_beneficiaries = serializers.IntegerField()
    programs_by_type = serializers.ListField()
    
    class Meta:
        fields = [
            'total_programs', 'active_programs', 'total_budget_fcfa',
            'total_used_fcfa', 'total_beneficiaries', 'programs_by_type'
        ]


class BudgetDashboardSerializer(serializers.Serializer):
    """
    Serializer pour dashboard budgétaire
    """
    
    overview = serializers.DictField()
    risk_analysis = serializers.DictField()
    
    class Meta:
        fields = ['overview', 'risk_analysis']


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Programs
    'SocialProgramSerializer',
    'ProgramBudgetChangeSerializer',
    
    # Eligibility
    'SocialProgramEligibilitySerializer',
    
    # Vulnerability
    'VulnerabilityAssessmentSerializer',
    'VulnerabilityAssessmentCreateSerializer',
    
    # Statistics
    'ProgramStatisticsSerializer',
    'BudgetDashboardSerializer',
]