#!/bin/bash

# 🇬🇦 RSU GABON - CRÉATION MODÈLES MODULAIRES
# Standards Top 1% - Structure Modulaire Django

echo "🏗️ Création des modèles modulaires RSU..."
echo "========================================"

# Vérification répertoire de travail
if [ ! -f "manage.py" ]; then
    echo "❌ Erreur: manage.py non trouvé"
    echo "🔧 Assurez-vous d'être dans rsu_identity_backend/"
    exit 1
fi

echo "✅ Répertoire backend trouvé"

# 1. CORE APP - Modèles de base système
echo "🔨 Création modèles Core App..."

cat > apps/core_app/models/__init__.py << 'EOF'
"""
🇬🇦 RSU Gabon - Core Models
Modèles de base du système RSU
"""
from .users import RSUUser
from .audit import AuditLog
from .base import BaseModel

__all__ = ['RSUUser', 'AuditLog', 'BaseModel']
EOF

cat > apps/core_app/models/base.py << 'EOF'
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
EOF

cat > apps/core_app/models/users.py << 'EOF'
"""
🇬🇦 RSU Gabon - Modèles Utilisateurs
Système d'authentification RSU
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from utils.gabonese_data import GABON_PROVINCES

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
    
    PROVINCES_CHOICES = [(code, data['name']) for code, data in GABON_PROVINCES.items()]
    
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
        return [GABON_PROVINCES.get(code, {}).get('name', code) for code in self.assigned_provinces]
        
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
EOF

cat > apps/core_app/models/audit.py << 'EOF'
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
EOF

# 2. IDENTITY APP - Modèles identité et géolocalisation
echo "🔨 Création modèles Identity App..."

cat > apps/identity_app/models/__init__.py << 'EOF'
"""
🇬🇦 RSU Gabon - Identity Models
Modèles pour la gestion des identités
"""
from .person import PersonIdentity
from .household import Household, HouseholdMember
from .geographic import GeographicData
from .rbpp import RBPPSync

__all__ = ['PersonIdentity', 'Household', 'HouseholdMember', 'GeographicData', 'RBPPSync']
EOF

cat > apps/identity_app/models/person.py << 'EOF'
"""
🇬🇦 RSU Gabon - Modèle Personne
Identité principale dans le RSU
"""
from django.db import models
from django.core.validators import RegexValidator
from apps.core_app.models.base import BaseModel
from utils.gabonese_data import GABON_PROVINCES, generate_rsu_id
import uuid

class PersonIdentity(BaseModel):
    """
    Identité principale d'une personne dans le RSU
    Cœur du système d'identification gabonais
    """
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre/Non spécifié'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Célibataire'),
        ('MARRIED', 'Marié(e)'),
        ('DIVORCED', 'Divorcé(e)'),
        ('WIDOW', 'Veuf/Veuve'),
        ('COHABITING', 'Concubinage'),
        ('SEPARATED', 'Séparé(e)'),
    ]
    
    EDUCATION_LEVELS = [
        ('NONE', 'Aucune'),
        ('INCOMPLETE_PRIMARY', 'Primaire Incomplet'),
        ('PRIMARY', 'Primaire'),
        ('SECONDARY', 'Secondaire'),
        ('HIGH_SCHOOL', 'Baccalauréat'),
        ('TECHNICAL', 'Formation Technique'),
        ('UNIVERSITY', 'Universitaire'),
        ('POSTGRADUATE', 'Post-universitaire'),
    ]
    
    VERIFICATION_STATUS = [
        ('PENDING', 'En Attente'),
        ('VERIFIED', 'Vérifié'),
        ('REJECTED', 'Rejeté'),
        ('REQUIRES_REVIEW', 'Nécessite Révision'),
    ]
    
    PROVINCES_CHOICES = [(code, data['name']) for code, data in GABON_PROVINCES.items()]
    
    # === IDENTIFIANTS UNIQUES ===
    rsu_id = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="RSU ID",
        help_text="Identifiant unique RSU Gabon"
    )
    nip = models.CharField(
        max_length=13, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name="NIP",
        help_text="Numéro d'Identification Personnel (RBPP)"
    )
    national_id = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        verbose_name="CNI/Passeport",
        help_text="Carte Nationale d'Identité ou Passeport"
    )
    
    # === INFORMATIONS PERSONNELLES ===
    first_name = models.CharField(
        max_length=100,
        verbose_name="Prénom(s)"
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="Nom de famille"
    )
    maiden_name = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Nom de jeune fille"
    )
    birth_date = models.DateField(verbose_name="Date de naissance")
    birth_place = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        verbose_name="Lieu de naissance"
    )
    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES,
        verbose_name="Genre"
    )
    marital_status = models.CharField(
        max_length=20, 
        choices=MARITAL_STATUS_CHOICES,
        default='SINGLE',
        verbose_name="Statut matrimonial"
    )
    nationality = models.CharField(
        max_length=50, 
        default='Gabonaise',
        verbose_name="Nationalité"
    )
    
    # === ÉDUCATION ET PROFESSION ===
    education_level = models.CharField(
        max_length=30, 
        choices=EDUCATION_LEVELS,
        null=True, 
        blank=True,
        verbose_name="Niveau d'éducation"
    )
    occupation = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        verbose_name="Profession"
    )
    employer = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        verbose_name="Employeur"
    )
    monthly_income = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Revenus mensuels (FCFA)"
    )
    
    # === CONTACT ===
    phone_validator = RegexValidator(
        regex=r'^\+241[0-9]{8}$', 
        message="Format requis: +241XXXXXXXX"
    )
    phone_number = models.CharField(
        validators=[phone_validator], 
        max_length=13, 
        null=True, 
        blank=True,
        verbose_name="Téléphone principal"
    )
    phone_number_alt = models.CharField(
        validators=[phone_validator], 
        max_length=13, 
        null=True, 
        blank=True,
        verbose_name="Téléphone alternatif"
    )
    email = models.EmailField(
        null=True, 
        blank=True,
        verbose_name="Email"
    )
    
    # === LOCALISATION ===
    # Coordonnées GPS précises
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name="Latitude GPS"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name="Longitude GPS"
    )
    gps_accuracy = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Précision GPS (mètres)"
    )
    
    # Division administrative
    province = models.CharField(
        max_length=50, 
        choices=PROVINCES_CHOICES,
        null=True, 
        blank=True,
        verbose_name="Province"
    )
    department = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Département"
    )
    commune = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Commune"
    )
    district = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="District/Quartier"
    )
    address = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Adresse complète"
    )
    
    # === SANTÉ ET SOCIAL ===
    has_disability = models.BooleanField(
        default=False,
        verbose_name="Situation de handicap"
    )
    disability_details = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Détails handicap"
    )
    chronic_diseases = models.JSONField(
        default=list, 
        blank=True,
        verbose_name="Maladies chroniques"
    )
    is_household_head = models.BooleanField(
        default=False,
        verbose_name="Chef de ménage"
    )
    
    # === VALIDATION ET STATUT ===
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS, 
        default='PENDING',
        verbose_name="Statut de vérification"
    )
    verified_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Vérifié le"
    )
    verified_by = models.ForeignKey(
        'core_app.RSUUser',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='verified_persons',
        verbose_name="Vérifié par"
    )
    
    # === SYNCHRONISATION RBPP ===
    rbpp_synchronized = models.BooleanField(
        default=False,
        verbose_name="Synchronisé RBPP"
    )
    rbpp_last_sync = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Dernière sync RBPP"
    )
    rbpp_sync_errors = models.JSONField(
        default=list, 
        blank=True,
        verbose_name="Erreurs sync RBPP"
    )
    
    # === MÉTADONNÉES ===
    data_completeness_score = models.FloatField(
        default=0.0,
        verbose_name="Score complétude données"
    )
    last_survey_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Dernière enquête"
    )
    notes = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Notes"
    )
    
    def save(self, *args, **kwargs):
        """Génération automatique du RSU ID"""
        if not self.rsu_id:
            self.rsu_id = generate_rsu_id()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.rsu_id})"
    
    @property
    def full_name(self):
        """Nom complet"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calcul de l'âge"""
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    def get_province_info(self):
        """Informations détaillées sur la province"""
        return GABON_PROVINCES.get(self.province, {})
    
    def is_vulnerable_age(self):
        """Vérifie si la personne est dans une tranche d'âge vulnérable"""
        return self.age < 5 or self.age > 65
    
    def calculate_completeness_score(self):
        """Calcule le score de complétude des données"""
        required_fields = [
            'first_name', 'last_name', 'birth_date', 'gender', 
            'phone_number', 'province', 'address'
        ]
        optional_fields = [
            'email', 'occupation', 'education_level', 'monthly_income',
            'latitude', 'longitude', 'national_id'
        ]
        
        required_score = sum(1 for field in required_fields if getattr(self, field))
        optional_score = sum(0.5 for field in optional_fields if getattr(self, field))
        
        total_possible = len(required_fields) + len(optional_fields) * 0.5
        score = (required_score + optional_score) / total_possible * 100
        
        self.data_completeness_score = round(score, 2)
        return self.data_completeness_score
    
    class Meta:
        verbose_name = "Identité Personne"
        verbose_name_plural = "Identités Personnes"
        db_table = 'rsu_persons'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['rsu_id']),
            models.Index(fields=['nip']),
            models.Index(fields=['province', 'commune']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['birth_date']),
        ]
EOF

# Mise à jour du settings pour utiliser RSUUser
echo "⚙️ Mise à jour des settings pour RSUUser..."
cat >> rsu_identity/settings/base.py << 'EOF'

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'core_app.RSUUser'
EOF

# Création des migrations
echo "🗄️ Création des migrations..."
python manage.py makemigrations core_app
python manage.py makemigrations identity_app

echo "🗄️ Application des migrations..."
python manage.py migrate

echo ""
echo "✅ MODÈLES MODULAIRES CRÉÉS AVEC SUCCÈS!"
echo "======================================="
echo ""
echo "🏗️ Structure créée:"
echo "   ├── Core App:"
echo "   │   ├── RSUUser (utilisateurs système)"
echo "   │   ├── AuditLog (traçabilité gouvernementale)"
echo "   │   └── BaseModel (modèle abstrait)"
echo "   └── Identity App:"
echo "       └── PersonIdentity (identités RSU complètes)"
echo ""
echo "🔧 Prochaine étape: Créer le superutilisateur"
echo "   python manage.py shell"
echo "   >>> from apps.core_app.models import RSUUser"
echo "   >>> RSUUser.objects.create_superuser('admin', 'admin@rsu.ga', 'admin123')"
echo ""
echo "🎯 Les modèles sont maintenant prêts pour le développement!"