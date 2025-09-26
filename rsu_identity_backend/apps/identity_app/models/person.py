# =============================================================================
# FICHIER: apps/identity_app/models/person.py
# CORRECTION: Import et usage correct de generate_rsu_id
# =============================================================================

"""
🇬🇦 RSU Gabon - Modèle Personne
Identité principale dans le RSU
"""
from datetime import timezone
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone as django_timezone
from apps.core_app.models.base import BaseModel
from utils.gabonese_data import PROVINCES, generate_rsu_id  # Import correct
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
    
    PROVINCES_CHOICES = [(code, data['name']) for code, data in PROVINCES.items()]
    
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
    birth_date = models.DateField(
        verbose_name="Date de naissance"
    )
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
        max_length=15,
        choices=MARITAL_STATUS_CHOICES,
        default='SINGLE',
        verbose_name="Statut matrimonial"
    )
    
    # === CONTACT ===
    phone_validator = RegexValidator(
        regex=r'^\+241[0-9]{8}$',
        message="Format requis: +241XXXXXXXX pour Gabon"
    )
    phone_number = models.CharField(
        validators=[phone_validator],
        max_length=13,
        null=True,
        blank=True,
        verbose_name="Téléphone principal"
    )
    email = models.EmailField(
        null=True, 
        blank=True,
        verbose_name="Email"
    )
    
    # === ÉDUCATION ET PROFESSION ===
    education_level = models.CharField(
        max_length=20,
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
    monthly_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Revenus mensuels (FCFA)"
    )
    
    # === LOCALISATION ===
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
    province = models.CharField(
        max_length=20,
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
        blank=True
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
    
    # === VULNÉRABILITÉ ===
    has_disability = models.BooleanField(
        default=False,
        verbose_name="Situation de handicap"
    )
    disability_details = models.TextField(
        null=True,
        blank=True,
        verbose_name="Détails handicap"
    )
    is_household_head = models.BooleanField(
        default=False,
        verbose_name="Chef de ménage"
    )
    
    # === VALIDATION ET QUALITÉ ===
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='PENDING',
        verbose_name="Statut vérification"
    )
    verified_by = models.ForeignKey(
        'core_app.RSUUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_persons',
        verbose_name="Vérifié par"
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date vérification"
    )
    data_completeness_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Score complétude (%)"
    )
    
    # === INTÉGRATION EXTERNE ===
    rbpp_synchronized = models.BooleanField(
        default=False,
        verbose_name="Synchronisé RBPP"
    )
    rbpp_sync_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière sync RBPP"
    )
    
    # === MÉTADONNÉES ===
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notes"
    )
    
    def save(self, *args, **kwargs):
        # CORRECTION: Appel correct de la fonction generate_rsu_id
        if not self.rsu_id:
            self.rsu_id = generate_rsu_id()  # Fonction importée, pas méthode d'instance
        super().save(*args, **kwargs)

    def clean(self):
        # CORRECTION: Appel correct dans clean aussi
        if not self.rsu_id:
            self.rsu_id = generate_rsu_id()  # Fonction importée, pas méthode d'instance
        
        # Validation dates
        if self.birth_date and self.birth_date > django_timezone.now().date():
            from django.core.exceptions import ValidationError
            raise ValidationError("La date de naissance ne peut pas être dans le futur")
    
    @property
    def full_name(self):
        """Nom complet de la personne"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calcul de l'âge en années"""
        if not self.birth_date:
            return None
        today = django_timezone.now().date()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    def calculate_completeness_score(self):
        """Calcul du score de complétude des données"""
        total_fields = 20  # Nombre de champs importants
        filled_fields = 0
        
        # Champs obligatoires (poids 2)
        required_fields = ['first_name', 'last_name', 'birth_date', 'gender']
        for field in required_fields:
            if getattr(self, field):
                filled_fields += 2
        
        # Champs importants (poids 1)
        important_fields = [
            'phone_number', 'province', 'address', 'occupation',
            'education_level', 'marital_status', 'birth_place'
        ]
        for field in important_fields:
            if getattr(self, field):
                filled_fields += 1
        
        # Champs GPS
        if self.latitude and self.longitude:
            filled_fields += 2
        
        # Score en pourcentage
        score = (filled_fields / total_fields) * 100
        self.data_completeness_score = round(min(score, 100.00), 2)
        return self.data_completeness_score
    
    def get_vulnerability_indicators(self):
        """Indicateurs de vulnérabilité"""
        indicators = []
        
        if self.has_disability:
            indicators.append('DISABILITY')
        
        if self.age and self.age >= 60:
            indicators.append('ELDERLY')
        
        if self.age and self.age < 18:
            indicators.append('MINOR')
        
        if self.is_household_head and self.gender == 'F':
            indicators.append('FEMALE_HEAD')
        
        if self.monthly_income and self.monthly_income < 75000:  # Seuil pauvreté
            indicators.append('EXTREME_POVERTY')
        
        return indicators
    
    def __str__(self):
        return f"{self.full_name} ({self.rsu_id})"
    
    class Meta:
        verbose_name = "Identité Personne"
        verbose_name_plural = "Identités Personnes"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['rsu_id']),
            models.Index(fields=['nip']),
            models.Index(fields=['province', 'verification_status']),
            models.Index(fields=['created_at']),
        ]