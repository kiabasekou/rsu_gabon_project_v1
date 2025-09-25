"""
🇬🇦 RSU Gabon - Modèles Core
Modèles de base pour le système
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class RSUUser(AbstractUser):
    """Utilisateur RSU avec extensions gabonaises"""
    USER_TYPES = [
        ('ADMIN', 'Administrateur'),
        ('SURVEYOR', 'Enquêteur'),
        ('SUPERVISOR', 'Superviseur'),
        ('OPERATOR', 'Opérateur'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='OPERATOR')
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Utilisateur RSU"
        verbose_name_plural = "Utilisateurs RSU"

class AuditLog(models.Model):
    """Audit trail pour toutes les actions système"""
    ACTIONS = [
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('SYNC', 'Synchronisation'),
        ('EXPORT', 'Export'),
    ]
    
    user = models.ForeignKey(RSUUser, on_delete=models.PROTECT)
    action = models.CharField(max_length=20, choices=ACTIONS)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log d'audit"
        verbose_name_plural = "Logs d'audit"
        ordering = ['-created_at']