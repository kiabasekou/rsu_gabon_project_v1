# =============================================================================
# FICHIER: apps/identity_app/admin.py
# CORRECTION MINIMALE: Seulement les champs existants
# =============================================================================

"""
🇬🇦 RSU Gabon - Admin Identity App
Interface d'administration pour les identités et ménages
"""
from django.contrib import admin
from django.utils.html import format_html
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
        'rbpp_sync_date', 'age_display'
    ]
    
    fieldsets = (
        ('Identifiants', {
            'fields': ('rsu_id', 'nip', 'national_id'),
        }),
        ('Informations Personnelles', {
            'fields': (
                ('first_name', 'last_name', 'maiden_name'),
                ('birth_date', 'birth_place'),
                ('gender', 'marital_status'),
            ),
        }),
        ('Éducation & Profession', {
            'fields': (
                ('education_level', 'occupation'),
                'monthly_income',
            ),
        }),
        ('Contact', {
            'fields': (
                'phone_number',
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
                'is_household_head',
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
                'rbpp_synchronized', 'rbpp_sync_date',
            ),
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': (
                'data_completeness_score', 'notes',
                'created_at', 'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def age_display(self, obj):
        if obj.age:
            return f"{obj.age} ans"
        return "Non calculé"
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
    """Administration des ménages - Version minimale"""
    
    list_display = [
        'household_id', 'household_size', 'province', 'created_at'
    ]
    list_filter = ['province']
    search_fields = ['household_id']
    readonly_fields = ['household_id', 'created_at', 'updated_at']
    
    # Fieldsets minimaux avec seulement les champs existants
    fieldsets = (
        ('Identification', {
            'fields': ('household_id',),
        }),
        ('Localisation', {
            'fields': ('province', 'latitude', 'longitude'),
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(HouseholdMember)
class HouseholdMemberAdmin(admin.ModelAdmin):
    """Administration des membres de ménage - Version minimale"""
    
    list_display = [
        'person', 'household', 'relationship_to_head', 'created_at'
    ]
    list_filter = ['relationship_to_head']
    search_fields = [
        'person__rsu_id', 'person__first_name', 'person__last_name',
        'household__household_id'
    ]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GeographicData)
class GeographicDataAdmin(admin.ModelAdmin):
    """Administration des données géographiques - Version minimale"""
    
    list_display = [
        'location_name', 'province', 'zone_type', 'accessibility_score'
    ]
    list_filter = ['province', 'zone_type']
    search_fields = ['location_name', 'province']
    readonly_fields = ['created_at', 'updated_at', 'accessibility_score']
    
    fieldsets = (
        ('Localisation', {
            'fields': (
                ('location_name', 'province'),
                ('center_latitude', 'center_longitude'),
                'zone_type',
            ),
        }),
        ('Scores Calculés', {
            'fields': ('accessibility_score',),
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'calculate_accessibility_score'):
            obj.calculate_accessibility_score()
        super().save_model(request, obj, form, change)


@admin.register(RBPPSync)
class RBPPSyncAdmin(admin.ModelAdmin):
    """Administration des synchronisations RBPP"""
    
    list_display = [
        'created_at', 'person', 'sync_type', 'sync_status',
        'nip_requested', 'retry_count'
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
    
    def has_add_permission(self, request):
        return False  # Syncs créées automatiquement


# =============================================================================
# CUSTOMISATION DE L'ADMIN PRINCIPAL
# =============================================================================

# Personnalisation du site admin
admin.site.site_header = "🇬🇦 RSU Gabon - Administration"
admin.site.site_title = "RSU Admin"
admin.site.index_title = "Registre Social Unifié - Tableau de Bord"