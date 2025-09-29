# ===================================================================
# RSU GABON - MODÈLES SERVICES APP - VERSION COMPLÈTE
# Remplacement du fichier incomplet
# ===================================================================

from django.db import models
from django.db.models import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.core_app.models import BaseModel

# ===================================================================
# MODÈLE PRINCIPAL: SOCIAL PROGRAM
# ===================================================================

class SocialProgram(BaseModel):
    """
    Modèle maître des programmes sociaux gouvernementaux
    Budgets et paramètres configurables par administrateurs
    """
    
    # Identifiants programme
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code programme",
        help_text="Code unique (ex: AIDE_ALIMENTAIRE)"
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nom du programme"
    )
    
    description = models.TextField(
        verbose_name="Description détaillée"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Programme actif"
    )
    
    # BUDGETS AJUSTABLES par administrateurs
    annual_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Budget annuel (FCFA)"
    )
    
    budget_used_fcfa = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Budget utilisé (FCFA)"
    )
    
    benefit_amount_fcfa = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Montant par bénéficiaire (FCFA)"
    )
    
    # Paramètres opérationnels
    duration_months = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        verbose_name="Durée standard (mois)"
    )
    
    max_beneficiaries = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Nombre max bénéficiaires"
    )
    
    current_beneficiaries = models.PositiveIntegerField(
        default=0,
        verbose_name="Bénéficiaires actuels"
    )
    
    # Critères configurables
    eligibility_criteria = JSONField(
        default=dict,
        verbose_name="Critères d'éligibilité",
        help_text="Configuration JSON des critères"
    )
    
    target_provinces = JSONField(
        default=list,
        verbose_name="Provinces ciblées"
    )
    
    urban_rural_preference = models.CharField(
        max_length=10,
        choices=[
            ('URBAN', 'Zones urbaines'),
            ('RURAL', 'Zones rurales'),
            ('BOTH', 'Urbain et rural'),
        ],
        default='BOTH',
        verbose_name="Préférence géographique"
    )
    
    program_type = models.CharField(
        max_length=20,
        choices=[
            ('CASH_TRANSFER', 'Transfert monétaire'),
            ('FOOD_AID', 'Aide alimentaire'),
            ('HEALTHCARE', 'Santé'),
            ('EDUCATION', 'Éducation'),
            ('HOUSING', 'Logement'),
            ('TRAINING', 'Formation'),
            ('MICROCREDIT', 'Micro-crédit'),
        ],
        verbose_name="Type de programme"
    )
    
    automated_enrollment = models.BooleanField(
        default=False,
        verbose_name="Inscription automatique"
    )
    
    requires_documents = models.BooleanField(
        default=True,
        verbose_name="Nécessite documents"
    )
    
    # Propriétés calculées
    @property
    def remaining_budget(self):
        return self.annual_budget - self.budget_used_fcfa
    
    @property
    def budget_utilization_percentage(self):
        if self.annual_budget > 0:
            return (self.budget_used_fcfa / self.annual_budget) * 100
        return 0
    
    @property
    def current_budget_utilization(self):
        return f"{self.budget_utilization_percentage:.1f}%"
    
    @property
    def can_accept_new_beneficiaries(self):
        return (
            self.is_active and 
            self.current_beneficiaries < self.max_beneficiaries and
            self.remaining_budget >= self.benefit_amount_fcfa
        )
    
    @property
    def is_budget_available(self):
        return self.remaining_budget >= self.benefit_amount_fcfa
    
    class Meta:
        db_table = 'services_social_programs'
        verbose_name = "Programme Social"
        verbose_name_plural = "Programmes Sociaux"
        ordering = ['name']
        
    def __str__(self):
        return f"{self.code} - {self.name}"


# ===================================================================
# ÉLIGIBILITÉ AUX PROGRAMMES
# ===================================================================

class SocialProgramEligibility(BaseModel):
    """
    Évaluation d'éligibilité personne/programme
    """
    
    person = models.ForeignKey(
        'identity_app.PersonIdentity',
        on_delete=models.CASCADE,
        related_name='program_eligibilities',
        verbose_name="Personne"
    )
    
    program_code = models.CharField(
        max_length=20,
        verbose_name="Code programme"
    )
    
    # Scores IA
    eligibility_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score éligibilité (0-100)"
    )
    
    recommendation_level = models.CharField(
        max_length=30,
        choices=[
            ('HIGHLY_RECOMMENDED', 'Fortement recommandé'),
            ('RECOMMENDED', 'Recommandé'),
            ('CONDITIONALLY_ELIGIBLE', 'Éligible sous conditions'),
            ('NOT_ELIGIBLE', 'Non éligible'),
        ],
        verbose_name="Niveau recommandation"
    )
    
    processing_priority = models.CharField(
        max_length=10,
        choices=[
            ('URGENT', 'Urgent'),
            ('HIGH', 'Priorité haute'),
            ('MEDIUM', 'Priorité moyenne'),
            ('LOW', 'Priorité basse'),
        ],
        default='MEDIUM',
        verbose_name="Priorité traitement"
    )
    
    # Facteurs détaillés
    eligibility_factors = JSONField(
        default=list,
        verbose_name="Facteurs d'éligibilité"
    )
    
    blocking_factors = JSONField(
        default=list,
        verbose_name="Facteurs bloquants"
    )
    
    # Estimations
    estimated_monthly_benefit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Bénéfice mensuel estimé (FCFA)"
    )
    
    estimated_impact = models.CharField(
        max_length=10,
        choices=[
            ('HIGH', 'Impact élevé'),
            ('MEDIUM', 'Impact moyen'),
            ('LOW', 'Impact faible'),
        ],
        null=True,
        blank=True,
        verbose_name="Impact estimé"
    )
    
    intervention_urgency = models.CharField(
        max_length=15,
        choices=[
            ('IMMEDIATE', 'Immédiat'),
            ('WITHIN_WEEK', 'Dans la semaine'),
            ('WITHIN_MONTH', 'Dans le mois'),
            ('ROUTINE', 'Routine'),
        ],
        default='ROUTINE',
        verbose_name="Urgence intervention"
    )
    
    assessment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date évaluation"
    )
    
    assessment_notes = models.TextField(
        blank=True,
        verbose_name="Notes d'évaluation"
    )
    
    class Meta:
        db_table = 'services_program_eligibility'
        verbose_name = "Éligibilité Programme"
        verbose_name_plural = "Éligibilités Programmes"
        ordering = ['-assessment_date']
        constraints = [
            models.UniqueConstraint(
                fields=['person', 'program_code'],
                name='unique_person_program_eligibility'
            )
        ]
        
    def __str__(self):
        return f"{self.person.full_name} - {self.program_code}"


# ===================================================================
# ÉVALUATION VULNÉRABILITÉ
# ===================================================================

class VulnerabilityAssessment(BaseModel):
    """
    Évaluation vulnérabilité multidimensionnelle
    """
    
    person = models.ForeignKey(
        'identity_app.PersonIdentity',
        on_delete=models.CASCADE,
        related_name='vulnerability_assessments',
        verbose_name="Personne"
    )
    
    # Score global
    vulnerability_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score vulnérabilité global (0-100)"
    )
    
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('CRITICAL', 'Critique'),
            ('HIGH', 'Élevée'),
            ('MODERATE', 'Modérée'),
            ('LOW', 'Faible'),
        ],
        verbose_name="Niveau de risque"
    )
    
    # Scores par dimension
    household_composition_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score composition ménage"
    )
    
    economic_vulnerability_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score vulnérabilité économique"
    )
    
    social_vulnerability_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score vulnérabilité sociale"
    )
    
    # Facteurs identifiés
    vulnerability_factors = JSONField(
        default=list,
        verbose_name="Facteurs de vulnérabilité"
    )
    
    risk_factors = JSONField(
        default=list,
        verbose_name="Facteurs de risque"
    )
    
    protective_factors = JSONField(
        default=list,
        verbose_name="Facteurs protecteurs"
    )
    
    # Recommandations
    recommendations = JSONField(
        default=list,
        verbose_name="Recommandations"
    )
    
    priority_interventions = JSONField(
        default=list,
        verbose_name="Interventions prioritaires"
    )
    
    assessment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date évaluation"
    )
    
    assessment_notes = models.TextField(
        blank=True,
        verbose_name="Notes d'évaluation"
    )
    
    class Meta:
        db_table = 'services_vulnerability_assessments'
        verbose_name = "Évaluation vulnérabilité"
        verbose_name_plural = "Évaluations vulnérabilité"
        ordering = ['-assessment_date']
        
    def __str__(self):
        return f"{self.person.full_name} - Vulnérabilité {self.risk_level}"


# ===================================================================
# HISTORIQUE MODIFICATIONS BUDGÉTAIRES
# ===================================================================

class ProgramBudgetChange(BaseModel):
    """
    Traçabilité modifications budgétaires
    Pour audit gouvernemental
    """
    
    program = models.ForeignKey(
        SocialProgram,
        on_delete=models.CASCADE,
        related_name='budget_changes',
        verbose_name="Programme"
    )
    
    change_type = models.CharField(
        max_length=20,
        choices=[
            ('INCREASE', 'Augmentation budget'),
            ('DECREASE', 'Réduction budget'),
            ('REALLOCATION', 'Réaffectation budgétaire'),
            ('ADJUSTMENT', 'Ajustement technique'),
            ('POLICY_CHANGE', 'Changement politique'),
        ],
        verbose_name="Type de changement"
    )
    
    # Montants
    previous_budget_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Ancien budget total"
    )
    
    new_budget_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Nouveau budget total"
    )
    
    amount_change_fcfa = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Montant du changement (FCFA)"
    )
    
    # Justification
    justification = models.TextField(
        verbose_name="Justification détaillée"
    )
    
    budget_source = models.CharField(
        max_length=50,
        verbose_name="Source budgétaire"
    )
    
    # Approbation
    approved_by = models.ForeignKey(
        'core_app.RSUUser',
        on_delete=models.PROTECT,
        verbose_name="Approuvé par"
    )
    
    approval_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date d'approbation"
    )
    
    class Meta:
        db_table = 'services_program_budget_changes'
        verbose_name = "Modification Budget Programme"
        verbose_name_plural = "Modifications Budgets Programmes"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Changement budget {self.program.name} - {self.created_at.strftime('%d/%m/%Y')}"