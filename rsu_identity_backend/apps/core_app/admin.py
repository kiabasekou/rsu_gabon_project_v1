# 🇬🇦 RSU GABON - CONFIGURATION ADMIN DJANGO
# Standards Gouvernementaux - Interface d'Administration

# =============================================================================
# FICHIER: apps/core_app/admin.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Admin Core App
Interface d'administration pour les utilisateurs et audit
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import RSUUser, AuditLog

@admin.register(RSUUser)
class RSUUserAdmin(UserAdmin):
    """Administration des utilisateurs RSU"""
    
    list_display = [
        'username', 'employee_id', 'user_type', 'get_full_name', 
        'email', 'phone_number', 'is_active', 'last_login'
    ]
    list_filter = [
        'user_type', 'is_active', 'is_staff', 'date_joined',
        'assigned_provinces'
    ]
    search_fields = [
        'username', 'employee_id', 'first_name', 'last_name', 
        'email', 'phone_number'
    ]
    readonly_fields = [
        'date_joined', 'last_login', 'created_at', 'updated_at',
        'last_activity', 'failed_login_attempts'
    ]
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations RSU', {
            'fields': (
                'user_type', 'employee_id', 'department', 'phone_number',
                'assigned_provinces'
            ),
        }),
        ('Localisation', {
            'fields': ('current_location_lat', 'current_location_lng'),
            'classes': ('collapse',),
        }),
        ('Sécurité', {
            'fields': (
                'last_login_ip', 'failed_login_attempts', 'account_locked_until',
                'force_password_change'
            ),
            'classes': ('collapse',),
        }),
        ('Dates Importantes', {
            'fields': ('created_at', 'updated_at', 'last_activity'),
            'classes': ('collapse',),
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    get_full_name.short_description = 'Nom Complet'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Administration des logs d'audit"""
    
    list_display = [
        'created_at', 'user', 'action', 'severity', 'description',
        'ip_address', 'get_object_display'
    ]
    list_filter = [
        'action', 'severity', 'created_at', 'user__user_type'
    ]
    search_fields = [
        'user__username', 'description', 'ip_address', 'object_id'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'user', 'action', 'description',
        'content_type', 'object_id', 'changes', 'ip_address', 
        'user_agent', 'session_key'
    ]
    date_hierarchy = 'created_at'
    
    def get_object_display(self, obj):
        if obj.content_object:
            return str(obj.content_object)[:50]
        return '-'
    get_object_display.short_description = 'Objet Concerné'
    
    def has_add_permission(self, request):
        return False  # Pas de création manuelle de logs
    
    def has_delete_permission(self, request, obj=None):
        return False  # Pas de suppression de logs

