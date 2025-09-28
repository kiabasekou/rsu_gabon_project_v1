# ===================================================================
# CONFIGURATION ADMIN DJANGO
# ===================================================================

# apps/services_app/admin.py - Ajout interfaces admin

from django.contrib import admin
from .models import SocialProgram

@admin.register(SocialProgram)
class SocialProgramAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'annual_budget', 'max_beneficiaries',
        'current_budget_utilization', 'is_active'
    ]
    list_filter = ['is_active', 'urban_rural_preference', 'target_provinces']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['current_budget_utilization', 'remaining_budget']

@admin.register(ProgramEligibilityAssessment)
class ProgramEligibilityAssessmentAdmin(admin.ModelAdmin):
    list_display = [
        'person', 'program', 'recommendation_status',
        'intervention_urgency', 'estimated_monthly_benefit',
        'allocation_decision', 'assessment_date'
    ]
    list_filter = [
        'recommendation_status', 'intervention_urgency',
        'allocation_decision', 'estimated_impact'
    ]
    search_fields = ['person__full_name', 'program__name']
    readonly_fields = [
        'eligibility_score', 'compatibility_score', 'processing_priority',
        'eligibility_factors', 'blocking_factors'
    ]