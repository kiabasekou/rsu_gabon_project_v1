# ===================================================================
# CONFIGURATION ADMIN DJANGO - SERVICES APP
# Correction: Import et enregistrement des bons modèles
# ===================================================================

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    SocialProgram, 
    SocialProgramEligibility, 
    VulnerabilityAssessment,
    ProgramBudgetChange,
    GeographicInterventionCost  # ✅ Ajouter
)
from .models import GeographicInterventionCost



@admin.register(SocialProgramEligibility)
class SocialProgramEligibilityAdmin(admin.ModelAdmin):
    """Administration des éligibilités aux programmes"""
    
    list_display = [
        'person', 'program_code', 'recommendation_level',
        'eligibility_score', 'assessment_date', 'is_active'
    ]
    list_filter = [
        'recommendation_level', 'program_code', 'intervention_urgency',
        'estimated_impact', 'assessment_date'
    ]
    search_fields = ['person__full_name', 'person__rsu_id', 'program_code']
    readonly_fields = [
        'eligibility_score', 'processing_priority',
        'eligibility_factors', 'blocking_factors', 'assessment_date'
    ]
    
    fieldsets = (
        ('Personne et Programme', {
            'fields': ('person', 'program_code')
        }),
        ('Évaluation Automatique', {
            'fields': ('eligibility_score', 'recommendation_level', 'processing_priority'),
            'classes': ('collapse',)
        }),
        ('Analyse Détaillée', {
            'fields': ('eligibility_factors', 'blocking_factors', 'intervention_urgency'),
            'classes': ('collapse',)
        }),
        ('Impact Estimé', {
            'fields': ('estimated_monthly_benefit', 'estimated_impact', 'assessment_notes')
        })
    )

@admin.register(VulnerabilityAssessment)
class VulnerabilityAssessmentAdmin(admin.ModelAdmin):
    """Administration des évaluations de vulnérabilité"""
    
    list_display = [
        'person', 'vulnerability_score', 'risk_level',
        'assessment_date', 'is_active'
    ]
    list_filter = ['risk_level', 'assessment_date', 'is_active']
    search_fields = ['person__full_name', 'person__rsu_id']
    readonly_fields = [
        'vulnerability_score', 'risk_level', 'vulnerability_factors',
        'household_composition_score', 'economic_vulnerability_score',
        'social_vulnerability_score', 'assessment_date'
    ]
    
    fieldsets = (
        ('Personne Évaluée', {
            'fields': ('person',)
        }),
        ('Scores Calculés', {
            'fields': (
                'vulnerability_score', 'risk_level',
                'household_composition_score', 'economic_vulnerability_score',
                'social_vulnerability_score'
            ),
            'classes': ('collapse',)
        }),
        ('Facteurs Identifiés', {
            'fields': ('vulnerability_factors', 'risk_factors', 'protective_factors'),
            'classes': ('collapse',)
        }),
        ('Recommandations', {
            'fields': ('recommendations', 'priority_interventions', 'assessment_notes')
        })
    )

@admin.register(ProgramBudgetChange)
class ProgramBudgetChangeAdmin(admin.ModelAdmin):
    """Administration des modifications budgétaires"""
    
    list_display = [
        'program', 'change_type', 'amount_change_fcfa',
        'approved_by', 'created_at'
    ]
    list_filter = ['change_type', 'created_at', 'approved_by']
    search_fields = ['program__name', 'justification', 'approved_by__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Programme et Modification', {
            'fields': ('program', 'change_type', 'amount_change_fcfa')
        }),
        ('Justification', {
            'fields': ('justification', 'budget_source')
        }),
        ('Approbation', {
            'fields': ('approved_by', 'approval_date')
        }),
        ('Suivi Budgétaire', {
            'fields': ('previous_budget_total', 'new_budget_total'),
            'classes': ('collapse',)
        })
    )


@admin.register(GeographicInterventionCost)
class GeographicInterventionCostAdmin(admin.ModelAdmin):
    """
    Interface admin pour configuration coûts intervention
    """
    list_display = [
        'zone_key',
        'cost_per_person_formatted',
        'last_updated_by',
        'last_updated_at'
    ]
    list_filter = ['zone_key', 'last_updated_at']
    search_fields = ['zone_key', 'description']
    readonly_fields = ['last_updated_by', 'last_updated_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Configuration Zone', {
            'fields': ('zone_key', 'cost_per_person')
        }),
        ('Détails', {
            'fields': ('description',)
        }),
        ('Audit Trail', {
            'fields': ('last_updated_by', 'last_updated_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def cost_per_person_formatted(self, obj):
        """Affiche coût formaté avec séparateurs"""
        return f"{obj.cost_per_person:,.0f} FCFA".replace(',', ' ')
    cost_per_person_formatted.short_description = "Coût par personne"
    
    def save_model(self, request, obj, form, change):
        """Enregistrer utilisateur qui modifie"""
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        """Empêcher suppression (seulement modification)"""
        return False  # Les zones ne peuvent pas être supprimées
    
    
# Configuration globale de l'admin
admin.site.site_header = "🇬🇦 Administration RSU Gabon"
admin.site.site_title = "RSU Admin"
admin.site.index_title = "Gestion des Services Sociaux"