
# =============================================================================
# FICHIER: apps/identity_app/admin.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Admin Identity App
Interface d'administration pour les identités et ménages
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import PersonIdentity, Household, HouseholdMember, GeographicData, RBPPSync

@admin.register(PersonIdentity)
class PersonIdentityAdmin(admin.ModelAdmin):
    """Administration des identités personnelles"""
    
    list_display = [
        'rsu_id', 'full_name', 'birth_date', 'age_display', 'gender',
        'province', 'verification_status', 'rbpp_sync_status', 'created_at'
    ]
    list_filter = [
        'verification_status', 'gender', 'province', 'marital_status',
        'education_level', 'rbpp_synchronized', 'has_disability'
    ]
    search_fields = [
        'rsu_id', 'nip', 'first_name', 'last_name', 'national_id',
        'phone_number', 'email'
    ]
    readonly_fields = [
        'rsu_id', 'created_at', 'updated_at', 'data_completeness_score',
        'rbpp_last_sync', 'age_display'
    ]
    
    fieldsets = (
        ('Identifiants', {
            'fields': ('rsu_id', 'nip', 'national_id'),
        }),
        ('Informations Personnelles', {
            'fields': (
                ('first_name', 'last_name', 'maiden_name'),
                ('birth_date', 'birth_place'),
                ('gender', 'marital_status', 'nationality'),
            ),
        }),
        ('Éducation & Profession', {
            'fields': (
                ('education_level', 'occupation'),
                ('employer', 'monthly_income'),
            ),
        }),
        ('Contact', {
            'fields': (
                ('phone_number', 'phone_number_alt'),
                'email',
            ),
        }),
        ('Localisation', {
            'fields': (
                ('latitude', 'longitude', 'gps_accuracy'),
                ('province', 'department'),
                ('commune', 'district'),
                'address',
            ),
        }),
        ('Santé & Social', {
            'fields': (
                'has_disability', 'disability_details',
                'chronic_diseases', 'is_household_head',
            ),
            'classes': ('collapse',),
        }),
        ('Validation', {
            'fields': (
                'verification_status', 'verified_at', 'verified_by',
            ),
        }),
        ('RBPP', {
            'fields': (
                'rbpp_synchronized', 'rbpp_last_sync', 'rbpp_sync_errors',
            ),
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': (
                'data_completeness_score', 'last_survey_date', 'notes',
                'created_at', 'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def age_display(self, obj):
        return f"{obj.age} ans"
    age_display.short_description = 'Âge'
    
    def rbpp_sync_status(self, obj):
        if obj.rbpp_synchronized:
            return format_html(
                '<span style="color: green;">✓ Synchronisé</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ Non synchronisé</span>'
            )
    rbpp_sync_status.short_description = 'RBPP'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Création
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.calculate_completeness_score()
        super().save_model(request, obj, form, change)


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    """Administration des ménages"""
    
    list_display = [
        'household_id', 'head_of_household', 'household_type', 
        'household_size', 'get_members_count', 'province', 'created_at'
    ]
    list_filter = [
        'household_type', 'housing_type', 'water_access', 
        'electricity_access', 'province'
    ]
    search_fields = [
        'household_id', 'head_of_household__first_name', 
        'head_of_household__last_name'
    ]
    readonly_fields = ['household_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('household_id', 'head_of_household'),
        }),
        ('Caractéristiques', {
            'fields': (
                ('household_type', 'household_size'),
                ('housing_type', 'number_of_rooms'),
            ),
        }),
        ('Services de Base', {
            'fields': (
                ('water_access', 'electricity_access'),
                'has_toilet',
            ),
        }),
        ('Économie', {
            'fields': (
                'total_monthly_income', 'has_bank_account', 'assets',
            ),
        }),
        ('Agriculture', {
            'fields': (
                'has_agricultural_land', 'agricultural_land_size', 'livestock',
            ),
            'classes': ('collapse',),
        }),
        ('Vulnérabilités', {
            'fields': (
                'has_disabled_members', 'has_elderly_members',
                'has_pregnant_women', 'has_children_under_5',
            ),
        }),
        ('Métadonnées', {
            'fields': (
                'last_visit_date', 'vulnerability_score',
                'created_at', 'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_members_count(self, obj):
        return obj.get_members_count()
    get_members_count.short_description = 'Membres Réels'


class HouseholdMemberInline(admin.TabularInline):
    """Inline pour les membres du ménage"""
    model = HouseholdMember
    extra = 1
    fields = [
        'person', 'relationship_to_head', 'is_current_member',
        'contributes_to_income', 'monthly_contribution'
    ]


# Ajouter l'inline au HouseholdAdmin
HouseholdAdmin.inlines = [HouseholdMemberInline]


@admin.register(GeographicData)
class GeographicDataAdmin(admin.ModelAdmin):
    """Administration des données géographiques"""
    
    list_display = [
        'location_name', 'province', 'zone_type', 'population_estimate',
        'accessibility_score', 'service_availability_score'
    ]
    list_filter = [
        'province', 'zone_type', 'road_condition', 
        'mobile_network_coverage', 'internet_available'
    ]
    search_fields = ['location_name', 'province', 'department', 'commune']
    
    fieldsets = (
        ('Identification', {
            'fields': (
                ('location_name', 'province'),
                ('department', 'commune'),
            ),
        }),
        ('Coordonnées', {
            'fields': ('center_latitude', 'center_longitude'),
        }),
        ('Caractéristiques', {
            'fields': (
                ('zone_type', 'population_estimate', 'area_km2'),
                ('road_condition', 'distance_to_main_road_km'),
                'public_transport_available',
            ),
        }),
        ('Distances Services (km)', {
            'fields': (
                ('distance_to_health_center_km', 'distance_to_hospital_km'),
                ('distance_to_school_km', 'distance_to_secondary_school_km'),
                ('distance_to_market_km', 'distance_to_bank_km'),
                'distance_to_admin_center_km',
            ),
        }),
        ('Connectivité', {
            'fields': (
                'mobile_network_coverage', 'internet_available',
            ),
        }),
        ('Risques', {
            'fields': (
                'flood_risk', 'difficult_access_rainy_season', 
                'security_concerns',
            ),
            'classes': ('collapse',),
        }),
        ('Scores Calculés', {
            'fields': ('accessibility_score', 'service_availability_score'),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        obj.calculate_accessibility_score()
        super().save_model(request, obj, form, change)


@admin.register(RBPPSync)
class RBPPSyncAdmin(admin.ModelAdmin):
    """Administration des synchronisations RBPP"""
    
    list_display = [
        'created_at', 'person', 'sync_type', 'sync_status',
        'nip_requested', 'retry_count', 'duration_display'
    ]
    list_filter = [
        'sync_type', 'sync_status', 'created_at'
    ]
    search_fields = [
        'person__rsu_id', 'person__first_name', 'person__last_name',
        'nip_requested', 'nip_returned'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'started_at', 'completed_at',
        'duration_seconds', 'rbpp_request_id'
    ]
    
    def duration_display(self, obj):
        if obj.duration_seconds:
            return f"{obj.duration_seconds}s"
        return '-'
    duration_display.short_description = 'Durée'
    
    def has_add_permission(self, request):
        return False  # Syncs créées automatiquement


# =============================================================================
# CUSTOMISATION DE L'ADMIN PRINCIPAL
# =============================================================================

# Personnalisation du site admin
admin.site.site_header = "🇬🇦 RSU Gabon - Administration"
admin.site.site_title = "RSU Admin"
admin.site.index_title = "Registre Social Unifié - Tableau de Bord"