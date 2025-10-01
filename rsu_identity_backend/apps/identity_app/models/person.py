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
from django.core.exceptions import ValidationError
import re


def validate_gabonese_phone(phone_number):
    """
    Validation spécifique numéros de téléphone gabonais
    Formats acceptés:
    - +241 XX XXX XXX (international)
    - 0X XXX XXXX (national)
    
    Opérateurs Gabon:
    - Gabon Telecom: +241 01/02/03/04/05
    - Airtel: +241 77/78/79  
    - Moov: +241 62/66/67
    """
    if not phone_number:
        return  # Champ optionnel
    
    # Nettoyer le numéro (supprimer espaces, tirets)
    clean_number = re.sub(r'[\s\-\(\)]', '', phone_number)
    
    # Pattern pour numéros gabonais
    gabonese_patterns = [
        r'^\+241[0-9]{8}$',           # +241XXXXXXXX (international)
        r'^00241[0-9]{8}$',           # 00241XXXXXXXX (international alternatif)
        r'^0[1-9][0-9]{7}$',          # 0XXXXXXXX (national)
    ]
    
    # Vérifier si le numéro correspond aux patterns gabonais
    is_valid = any(re.match(pattern, clean_number) for pattern in gabonese_patterns)
    
    if not is_valid:
        raise ValidationError(
            'Numéro de téléphone invalide. '
            'Formats acceptés: +241XXXXXXXX ou 0XXXXXXXX (Gabon uniquement)'
        )
    
    # Validation opérateurs spécifiques
    if clean_number.startswith('+241'):
        prefix = clean_number[4:6]  # 2 chiffres après +241
    elif clean_number.startswith('00241'):
        prefix = clean_number[5:7]  # 2 chiffres après 00241
    elif clean_number.startswith('0'):
        prefix = clean_number[1:3]  # 2 chiffres après 0
    else:
        prefix = None
    
    # Préfixes valides au Gabon (2024)
    valid_prefixes = [
        '01', '02', '03', '04', '05',  # Gabon Telecom fixe
        '06', '07',                    # Gabon Telecom mobile
        '62', '66', '67',              # Moov (anciennement Azur)  
        '77', '78', '79',              # Airtel
    ]
    
    if prefix and prefix not in valid_prefixes:
        raise ValidationError(
            f'Préfixe {prefix} non reconnu pour un opérateur gabonais. '
            f'Préfixes valides: {", ".join(valid_prefixes)}'
        )

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
    nationality = models.CharField(
    max_length=50,
    default='GABONAISE',
    choices=[
        ('GABONAISE', 'Gabonaise'),
        ('AUTRE_CEMAC', 'Autre CEMAC'),
        ('AUTRE_AFRIQUE', 'Autre Afrique'),
        ('AUTRE', 'Autre'),
    ],
    verbose_name="Nationalité"
)
    # === CONTACT ===
    phone_validator = RegexValidator(
        regex=r'^\+241[0-9]{8}$',
        message="Format requis: +241XXXXXXXX pour Gabon"
    )
        # Dans le modèle PersonIdentity, ajouter:
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_gabonese_phone],  # ← Ajout validateur
        verbose_name="Numéro de Téléphone",
        help_text="Format: +241XXXXXXXX ou 0XXXXXXXX"
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
    # === VULNÉRABILITÉ (Calculée par services) ===
    vulnerability_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Score de vulnérabilité (0-100)",
        help_text="Calculé automatiquement par le service de vulnérabilité"
    )

    VULNERABILITY_LEVELS = [
        ('CRITICAL', 'Critique'),
        ('HIGH', 'Élevée'),
        ('MODERATE', 'Modérée'),
        ('LOW', 'Faible'),
    ]

    vulnerability_level = models.CharField(
        max_length=20,
        choices=VULNERABILITY_LEVELS,
        null=True,
        blank=True,
        verbose_name="Niveau de vulnérabilité"
    )

    last_vulnerability_assessment = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière évaluation vulnérabilité"
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
    
    def clean(self):
        """Validation et génération automatique RSU-ID"""
        # ✅ CORRECTION: Générer RSU-ID AVANT validation si manquant
        if not self.rsu_id:
            from utils.gabonese_data import generate_rsu_id
            self.rsu_id = generate_rsu_id()
        
        # Validation dates
        if self.birth_date and self.birth_date > django_timezone.now().date():
            raise ValidationError("La date de naissance ne peut pas être dans le futur")
        
        super().clean()

    def save(self, *args, **kwargs):
        """Sauvegarde avec génération automatique RSU-ID"""
        # ✅ CORRECTION: Générer RSU-ID AVANT sauvegarde si manquant
        if not self.rsu_id:
            from utils.gabonese_data import generate_rsu_id
            self.rsu_id = generate_rsu_id()
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """Nom complet de la personne"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calcul de l'âge en années avec gestion des types de données"""
        if not self.birth_date:
            return None
        
        # ✅ CORRECTION: Gestion des types de données (str ou date)
        birth_date = self.birth_date
        if isinstance(birth_date, str):
            from datetime import datetime
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        today = django_timezone.now().date()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
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
    
