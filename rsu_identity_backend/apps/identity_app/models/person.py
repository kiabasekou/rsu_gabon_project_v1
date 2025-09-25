"""
🇬🇦 RSU Gabon - Modèle Personne
Identité principale dans le RSU
"""
from django.db import models
from django.core.validators import RegexValidator
from apps.core_app.models.base import BaseModel
from utils.gabonese_data import PROVINCES, generate_rsu_id
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