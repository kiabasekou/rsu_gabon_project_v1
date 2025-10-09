"""
🇬🇦 RSU Gabon - Programs App Models
Standards Top 1% - Gestion Programmes Sociaux
Fichier: rsu_identity_backend/apps/programs_app/models.py
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.core_app.models import RSUUser
from apps.identity_app.models import PersonIdentity, Household


class ProgramCategory(models.Model):
    """Catégories de programmes sociaux"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom catégorie"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icône/emoji représentant la catégorie"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'program_categories'
        verbose_name = 'Catégorie de Programme'
        verbose_name_plural = 'Catégories de Programmes'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SocialProgram(models.Model):
    """Programme d'aide sociale"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('ACTIVE', 'Actif'),
        ('PAUSED', 'Suspendu'),
        ('CLOSED', 'Clôturé'),
    ]
    
    FREQUENCY_CHOICES = [
        ('ONE_TIME', 'Ponctuel'),
        ('MONTHLY', 'Mensuel'),
        ('QUARTERLY', 'Trimestriel'),
        ('ANNUAL', 'Annuel'),
    ]
    
    # Informations de base
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code programme",
        help_text="Ex: TMC-2025, ALLOC-FAM"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nom du programme"
    )
    category = models.ForeignKey(
        ProgramCategory,
        on_delete=models.PROTECT,
        related_name='programs',
        verbose_name="Catégorie"
    )
    description = models.TextField(
        verbose_name="Description détaillée"
    )
    objectives = models.TextField(
        blank=True,
        verbose_name="Objectifs du programme"
    )
    
    # Statut et dates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name="Statut"
    )
    start_date = models.DateField(
        verbose_name="Date de début"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de fin"
    )
    
    # Budget et montants
    total_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Budget total (FCFA)"
    )
    budget_spent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Budget dépensé (FCFA)"
    )
    benefit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Montant de l'aide (FCFA)",
        help_text="Montant par bénéficiaire"
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='MONTHLY',
        verbose_name="Fréquence de versement"
    )
    
    # Capacité
    max_beneficiaries = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre max de bénéficiaires",
        help_text="Laisser vide si illimité"
    )
    current_beneficiaries = models.PositiveIntegerField(
        default=0,
        verbose_name="Bénéficiaires actuels"
    )
    
    # Critères d'éligibilité (JSON)
    eligibility_criteria = models.JSONField(
        default=dict,
        verbose_name="Critères d'éligibilité",
        help_text="""
        {
            "vulnerability_min": 50,
            "age_min": 18,
            "age_max": 65,
            "provinces": ["ESTUAIRE", "HAUT_OGOOUE"],
            "gender": "F",
            "household_size_min": 3
        }
        """
    )
    
    # Géolocalisation
    target_provinces = models.JSONField(
        default=list,
        verbose_name="Provinces ciblées",
        help_text="Liste des provinces ['ESTUAIRE', 'NGOUNIE']"
    )
    
    # Gestion
    managed_by = models.ForeignKey(
        RSUUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_programs',
        verbose_name="Géré par"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        RSUUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_programs'
    )
    
    class Meta:
        db_table = 'social_programs'
        verbose_name = 'Programme Social'
        verbose_name_plural = 'Programmes Sociaux'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_active(self):
        """Vérifie si le programme est actif"""
        if self.status != 'ACTIVE':
            return False
        
        today = timezone.now().date()
        if today < self.start_date:
            return False
        
        if self.end_date and today > self.end_date:
            return False
        
        return True
    
    @property
    def budget_remaining(self):
        """Budget restant"""
        return self.total_budget - self.budget_spent
    
    @property
    def capacity_remaining(self):
        """Places restantes"""
        if not self.max_beneficiaries:
            return None
        return self.max_beneficiaries - self.current_beneficiaries
    
    @property
    def is_full(self):
        """Programme complet?"""
        if not self.max_beneficiaries:
            return False
        return self.current_beneficiaries >= self.max_beneficiaries


class ProgramEnrollment(models.Model):
    """Inscription d'un bénéficiaire à un programme"""
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Rejeté'),
        ('ACTIVE', 'Actif'),
        ('SUSPENDED', 'Suspendu'),
        ('COMPLETED', 'Terminé'),
    ]
    
    # Relations
    program = models.ForeignKey(
        SocialProgram,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Programme"
    )
    beneficiary = models.ForeignKey(
        PersonIdentity,
        on_delete=models.CASCADE,
        related_name='program_enrollments',
        verbose_name="Bénéficiaire"
    )
    household = models.ForeignKey(
        Household,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='program_enrollments',
        verbose_name="Ménage"
    )
    
    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Statut"
    )
    
    # Dates
    enrollment_date = models.DateField(
        auto_now_add=True,
        verbose_name="Date d'inscription"
    )
    approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'approbation"
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de début"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de fin"
    )
    
    # Scoring
    eligibility_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Score d'éligibilité",
        help_text="Score automatique de matching avec critères"
    )
    
    # Montants
    total_received = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Total reçu (FCFA)"
    )
    payments_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de paiements"
    )
    
    # Notes et justification
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Motif de rejet"
    )
    
    # Gestion
    approved_by = models.ForeignKey(
        RSUUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_enrollments',
        verbose_name="Approuvé par"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'program_enrollments'
        verbose_name = 'Inscription Programme'
        verbose_name_plural = 'Inscriptions Programmes'
        ordering = ['-created_at']
        unique_together = [['program', 'beneficiary']]
        indexes = [
            models.Index(fields=['status', 'enrollment_date']),
            models.Index(fields=['program', 'status']),
        ]
    
    def __str__(self):
        return f"{self.beneficiary.full_name} → {self.program.code}"


class Payment(models.Model):
    """Paiement/Transfert monétaire"""
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PROCESSING', 'En traitement'),
        ('COMPLETED', 'Complété'),
        ('FAILED', 'Échoué'),
        ('CANCELLED', 'Annulé'),
    ]
    
    METHOD_CHOICES = [
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK_TRANSFER', 'Virement bancaire'),
        ('CASH', 'Espèces'),
        ('CHECK', 'Chèque'),
    ]
    
    # Relations
    enrollment = models.ForeignKey(
        ProgramEnrollment,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Inscription"
    )
    beneficiary = models.ForeignKey(
        PersonIdentity,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Bénéficiaire"
    )
    program = models.ForeignKey(
        SocialProgram,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Programme"
    )
    
    # Montant
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Montant (FCFA)"
    )
    
    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Statut"
    )
    
    # Méthode et détails
    payment_method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        verbose_name="Méthode de paiement"
    )
    payment_reference = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Référence paiement"
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID transaction",
        help_text="ID externe (operateur mobile, banque)"
    )
    
    # Dates
    scheduled_date = models.DateField(
        verbose_name="Date prévue"
    )
    processed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de traitement"
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    failure_reason = models.TextField(
        blank=True,
        verbose_name="Motif d'échec"
    )
    
    # Gestion
    processed_by = models.ForeignKey(
        RSUUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payments',
        verbose_name="Traité par"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['status', 'scheduled_date']),
            models.Index(fields=['payment_reference']),
            models.Index(fields=['beneficiary', 'status']),
        ]
    
    def __str__(self):
        return f"{self.payment_reference} - {self.amount} FCFA"