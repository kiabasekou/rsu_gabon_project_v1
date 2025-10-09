"""
🇬🇦 RSU Gabon - Programs App Admin
Fichier: apps/programs_app/admin.py
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ProgramCategory, SocialProgram, ProgramEnrollment, Payment


@admin.register(ProgramCategory)
class ProgramCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'programs_count', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def programs_count(self, obj):
        return obj.programs.count()
    programs_count.short_description = 'Nombre de programmes'


@admin.register(SocialProgram)
class SocialProgramAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'status_badge', 'category',
        'budget_progress', 'beneficiaries_progress',
        'start_date', 'is_active'
    ]
    list_filter = ['status', 'category', 'start_date']
    search_fields = ['code', 'name', 'description']
    readonly_fields = [
        'budget_spent', 'current_beneficiaries',
        'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Informations de base', {
            'fields': ('code', 'name', 'category', 'description', 'objectives')
        }),
        ('Statut et dates', {
            'fields': ('status', 'start_date', 'end_date')
        }),
        ('Budget', {
            'fields': (
                'total_budget', 'budget_spent', 'benefit_amount', 'frequency'
            )
        }),
        ('Capacité', {
            'fields': ('max_beneficiaries', 'current_beneficiaries')
        }),
        ('Critères d\'éligibilité', {
            'fields': ('eligibility_criteria', 'target_provinces'),
            'classes': ('collapse',)
        }),
        ('Gestion', {
            'fields': ('managed_by', 'created_by'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'DRAFT': 'gray',
            'ACTIVE': 'green',
            'PAUSED': 'orange',
            'CLOSED': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 10px; border-radius:3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def budget_progress(self, obj):
        if obj.total_budget == 0:
            return "N/A"
        percent = (obj.budget_spent / obj.total_budget * 100)
        color = 'green' if percent < 80 else 'orange' if percent < 100 else 'red'
        return format_html(
            '<div style="width:100px; background:#eee; border-radius:3px;">'
            '<div style="width:{}%; background:{}; color:white; text-align:center; border-radius:3px;">{:.0f}%</div>'
            '</div>',
            min(percent, 100), color, percent
        )
    budget_progress.short_description = 'Budget utilisé'
    
    def beneficiaries_progress(self, obj):
        if not obj.max_beneficiaries:
            return f"{obj.current_beneficiaries} (illimité)"
        percent = (obj.current_beneficiaries / obj.max_beneficiaries * 100)
        return f"{obj.current_beneficiaries} / {obj.max_beneficiaries} ({percent:.0f}%)"
    beneficiaries_progress.short_description = 'Bénéficiaires'


@admin.register(ProgramEnrollment)
class ProgramEnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'beneficiary_link', 'program_link', 'status_badge',
        'eligibility_score', 'enrollment_date', 'total_received'
    ]
    list_filter = ['status', 'program', 'enrollment_date']
    search_fields = [
        'beneficiary__first_name', 'beneficiary__last_name',
        'beneficiary__rsu_id', 'program__code', 'program__name'
    ]
    readonly_fields = [
        'total_received', 'payments_count', 'created_at', 'updated_at'
    ]
    
    def beneficiary_link(self, obj):
        return format_html(
            '<a href="/admin/identity_app/personidentity/{}/change/">{}</a>',
            obj.beneficiary.id, obj.beneficiary.full_name
        )
    beneficiary_link.short_description = 'Bénéficiaire'
    
    def program_link(self, obj):
        return format_html(
            '<a href="/admin/programs_app/socialprogram/{}/change/">{}</a>',
            obj.program.id, obj.program.name
        )
    program_link.short_description = 'Programme'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'APPROVED': 'blue',
            'REJECTED': 'red',
            'ACTIVE': 'green',
            'SUSPENDED': 'gray',
            'COMPLETED': 'purple',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 10px; border-radius:3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_reference', 'beneficiary_link', 'amount_display',
        'status_badge', 'payment_method', 'scheduled_date', 'processed_date'
    ]
    list_filter = ['status', 'payment_method', 'scheduled_date']
    search_fields = [
        'payment_reference', 'transaction_id',
        'beneficiary__first_name', 'beneficiary__last_name'
    ]
    readonly_fields = ['processed_date', 'created_at', 'updated_at']
    
    def beneficiary_link(self, obj):
        return format_html(
            '<a href="/admin/identity_app/personidentity/{}/change/">{}</a>',
            obj.beneficiary.id, obj.beneficiary.full_name
        )
    beneficiary_link.short_description = 'Bénéficiaire'
    
    def amount_display(self, obj):
        return f"{obj.amount:,.0f} FCFA"
    amount_display.short_description = 'Montant'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'PROCESSING': 'blue',
            'COMPLETED': 'green',
            'FAILED': 'red',
            'CANCELLED': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 10px; border-radius:3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'