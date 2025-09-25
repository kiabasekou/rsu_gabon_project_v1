"""
🇬🇦 RSU Gabon - Modèles Utilisateurs
Système d'authentification RSU
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from utils.gabonese_data import PROVINCES

class RSUUser(AbstractUser):
    """
    Utilisateur RSU avec extensions gabonaises
    Compatible avec le système d'identité gouvernemental
    """
    USER_TYPES = [
        ('ADMIN', 'Administrateur Système'),
        ('SURVEYOR', 'Enquêteur Terrain'),
        ('SUPERVISOR', 'Superviseur Régional'),
        ('OPERATOR', 'Opérateur Programme'),
        ('ANALYST', 'Analyste Données'),
        ('AUDITOR', 'Auditeur'),
    ]
    
    PROVINCES_CHOICES = [(code, data['name']) for code, data in PROVINCES.items()]
    
    # Informations professionnelles
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPES, 
        default='OPERATOR',
        verbose_name="Type d'utilisateur"
    )
    employee_id = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name="ID Employé"
    )
    department = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Département"
    )
    
    # Contact et localisation
    phone_validator = RegexValidator(
        regex=r'^\+241[0-9]{8}$', 
        message="Format requis: +241XXXXXXXX"
    )
    phone_number = models.CharField(
        validators=[phone_validator], 
        max_length=13, 
        null=True, 
        blank=True,
        verbose_name="Téléphone"
    )
    
    # Zones d'intervention (pour enquêteurs)
    assigned_provinces = models.JSONField(
        default=list, 
        blank=True,
        help_text="Provinces d'intervention autorisées",
        verbose_name="Provinces assignées"
    )
    current_location_lat = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name="Latitude actuelle"
    )
    current_location_lng = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name="Longitude actuelle"
    )
    
    # Sécurité et audit
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    force_password_change = models.BooleanField(default=False)
    
    # Dates importantes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Utilisateur RSU"
        verbose_name_plural = "Utilisateurs RSU"
        db_table = 'rsu_users'
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"
        
    def get_provinces_display(self):
        """Affichage des provinces assignées"""
        return [PROVINCES.get(code, {}).get('name', code) for code in self.assigned_provinces]
        
    def can_access_province(self, province_code):
        """Vérification d'accès à une province"""
        if self.user_type == 'ADMIN':
            return True
        return province_code in self.assigned_provinces
        
    def is_surveyor(self):
        """Vérifie si l'utilisateur est enquêteur"""
        return self.user_type == 'SURVEYOR'
        
    def is_supervisor(self):
        """Vérifie si l'utilisateur est superviseur"""
        return self.user_type in ['SUPERVISOR', 'ADMIN']