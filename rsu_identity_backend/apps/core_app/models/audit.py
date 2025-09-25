"""
🇬🇦 RSU Gabon - Modèles Audit
Système de traçabilité gouvernementale
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .base import BaseModel

class AuditLog(BaseModel):
    """
    Journal d'audit pour toutes les actions système
    Conformité gouvernementale et traçabilité complète
    """
    ACTIONS = [
        # Actions CRUD
        ('CREATE', 'Création'),
        ('READ', 'Consultation'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        
        # Actions authentification
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('LOGIN_FAILED', 'Échec Connexion'),
        ('PASSWORD_CHANGE', 'Changement Mot de Passe'),
        
        # Actions métier
        ('ENROLLMENT', 'Enrôlement Bénéficiaire'),
        ('VALIDATION', 'Validation Données'),
        ('SYNC', 'Synchronisation RBPP'),
        ('EXPORT', 'Export Données'),
        ('IMPORT', 'Import Données'),
        
        # Actions sensibles
        ('DATA_ACCESS', 'Accès Données Sensibles'),
        ('ADMIN_ACTION', 'Action Administrative'),
        ('SYSTEM_CONFIG', 'Configuration Système'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Élevée'),
        ('CRITICAL', 'Critique'),
    ]
    
    # Action et utilisateur
    user = models.ForeignKey(
        'core_app.RSUUser', 
        on_delete=models.PROTECT,
        verbose_name="Utilisateur"
    )
    action = models.CharField(
        max_length=30, 
        choices=ACTIONS,
        verbose_name="Action"
    )
    severity = models.CharField(
        max_length=10, 
        choices=SEVERITY_LEVELS, 
        default='LOW',
        verbose_name="Gravité"
    )
    
    # Objet concerné (relation générique)
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    object_id = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Détails de l'action
    description = models.TextField(verbose_name="Description")
    changes = models.JSONField(
        null=True, 
        blank=True,
        help_text="Détails des modifications (avant/après)",
        verbose_name="Modifications"
    )
    
    # Contexte technique
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name="Adresse IP"
    )
    user_agent = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Navigateur"
    )
    session_key = models.CharField(
        max_length=40, 
        null=True, 
        blank=True,
        verbose_name="Session"
    )
    
    # Contexte géographique
    location_lat = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name="Latitude"
    )
    location_lng = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name="Longitude"
    )
    
    class Meta:
        verbose_name = "Log d'Audit"
        verbose_name_plural = "Logs d'Audit"
        db_table = 'rsu_audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['created_at']),
            models.Index(fields=['severity']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.created_at}"
        
    @classmethod
    def log_action(cls, user, action, description, obj=None, changes=None, 
                   ip_address=None, user_agent=None, severity='LOW'):
        """
        Méthode utilitaire pour créer un log d'audit
        """
        return cls.objects.create(
            user=user,
            action=action,
            description=description,
            content_object=obj,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity
        )