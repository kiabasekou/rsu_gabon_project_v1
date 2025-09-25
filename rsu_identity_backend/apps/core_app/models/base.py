"""
🇬🇦 RSU Gabon - Modèle de Base
Modèle abstrait pour tous les autres modèles
"""
from django.db import models
from django.utils import timezone
import uuid

class BaseModel(models.Model):
    """
    Modèle de base abstrait avec champs communs
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Métadonnées pour audit
    created_by = models.ForeignKey(
        'core_app.RSUUser', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='created_%(class)s_set',
        verbose_name="Créé par"
    )
    updated_by = models.ForeignKey(
        'core_app.RSUUser', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='updated_%(class)s_set',
        verbose_name="Modifié par"
    )
    
    class Meta:
        abstract = True
        
    def soft_delete(self):
        """Suppression logique"""
        self.is_active = False
        self.save()
        
    def restore(self):
        """Restauration après suppression logique"""
        self.is_active = True
        self.save()