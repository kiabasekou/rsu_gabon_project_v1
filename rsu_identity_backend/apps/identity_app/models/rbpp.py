

# =============================================================================
# FICHIER: apps/identity_app/models/rbpp.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Modèles Synchronisation RBPP
Intégration avec le Registre Biométrique des Personnes Physiques
"""
from datetime import timezone
from django.db import models
from apps.core_app.models.base import BaseModel

class RBPPSync(BaseModel):
    """
    Synchronisation avec le système RBPP
    Traçabilité des échanges avec le registre biométrique national
    """
    SYNC_TYPES = [
        ('VALIDATION', 'Validation NIP'),
        ('DATA_FETCH', 'Récupération Données'),
        ('UPDATE', 'Mise à Jour'),
        ('VERIFICATION', 'Vérification Biométrique'),
        ('BULK_SYNC', 'Synchronisation Massive'),
    ]
    
    SYNC_STATUS = [
        ('PENDING', 'En Attente'),
        ('IN_PROGRESS', 'En Cours'),
        ('SUCCESS', 'Réussie'),
        ('FAILED', 'Échouée'),
        ('TIMEOUT', 'Délai Dépassé'),
        ('PARTIAL', 'Partielle'),
    ]
    
    # Référence à la personne
    person = models.ForeignKey(
        'identity_app.PersonIdentity',
        on_delete=models.CASCADE,
        related_name='rbpp_syncs',
        verbose_name="Personne"
    )
    
    # Type et statut de synchronisation
    sync_type = models.CharField(
        max_length=20, 
        choices=SYNC_TYPES,
        verbose_name="Type de Sync"
    )
    sync_status = models.CharField(
        max_length=20, 
        choices=SYNC_STATUS,
        default='PENDING',
        verbose_name="Statut"
    )
    
    # Données techniques
    rbpp_request_id = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="ID Requête RBPP"
    )
    nip_requested = models.CharField(
        max_length=13, 
        null=True, 
        blank=True,
        verbose_name="NIP Demandé"
    )
    nip_returned = models.CharField(
        max_length=13, 
        null=True, 
        blank=True,
        verbose_name="NIP Retourné"
    )
    
    # Résultats de la synchronisation
    rbpp_response_data = models.JSONField(
        null=True, 
        blank=True,
        verbose_name="Données Réponse RBPP"
    )
    biometric_match_score = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Score Correspondance Biométrique"
    )
    data_discrepancies = models.JSONField(
        default=list, 
        blank=True,
        verbose_name="Incohérences Données"
    )
    
    # Gestion erreurs
    error_code = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        verbose_name="Code Erreur"
    )
    error_message = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Message Erreur"
    )
    
    # Timing
    started_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Démarré à"
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Terminé à"
    )
    duration_seconds = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name="Durée (secondes)"
    )
    
    # Retry logic
    retry_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de Tentatives"
    )
    max_retries = models.PositiveIntegerField(
        default=3,
        verbose_name="Max Tentatives"
    )
    next_retry_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Prochaine Tentative"
    )
    
    def __str__(self):
        return f"RBPP Sync {self.person.rsu_id} - {self.get_sync_type_display()}"
    
    def can_retry(self):
        """Vérifie si une nouvelle tentative est possible"""
        return self.retry_count < self.max_retries and self.sync_status == 'FAILED'
    
    def mark_success(self, response_data=None):
        """Marque la sync comme réussie"""
        self.sync_status = 'SUCCESS'
        self.completed_at = timezone.now()
        if response_data:
            self.rbpp_response_data = response_data
        self.save()
    
    def mark_failed(self, error_code=None, error_message=None):
        """Marque la sync comme échouée"""
        self.sync_status = 'FAILED'
        self.completed_at = timezone.now()
        if error_code:
            self.error_code = error_code
        if error_message:
            self.error_message = error_message
        self.save()
    
    class Meta:
        verbose_name = "Synchronisation RBPP"
        verbose_name_plural = "Synchronisations RBPP"
        db_table = 'rsu_rbpp_syncs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['person', 'sync_type']),
            models.Index(fields=['sync_status']),
            models.Index(fields=['next_retry_at']),
        ]