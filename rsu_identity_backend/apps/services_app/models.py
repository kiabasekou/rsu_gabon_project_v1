# ===================================================================
# RSU GABON - MODÈLES SERVICES APP - VERSION COMPLÈTE
# Remplacement du fichier incomplet
# ===================================================================
#rsu_identity_backend\apps\services_app\models.py

from django.db import models
from django.db.models import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.core_app.models import BaseModel
from apps.programs_app.models import SocialProgram as MasterProgram
from django.conf import settings
from apps.identity_app.models.person import PersonIdentity
from apps.programs_app.models import SocialProgram


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
    """Évaluation vulnérabilité liée à un programme"""
    
    program = models.ForeignKey(
        MasterProgram,  # ← Référence vers programs_app
        on_delete=models.CASCADE,
        related_name='vulnerability_assessments',
        verbose_name="Programme"
    )
    person = models.ForeignKey(
        PersonIdentity,
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

# ===================================================================
# COÛTS INTERVENTION GÉOGRAPHIQUES (Configurable Admin)
# ===================================================================

class GeographicInterventionCost(BaseModel):
    """
    Coûts d'intervention par zone géographique
    Configurable par les administrateurs
    """
    
    ZONE_CHOICES = [
        ('ZONE_1', 'Zone Critique'),
        ('ZONE_2', 'Zone Priorité Élevée'),
        ('ZONE_3', 'Zone Priorité Modérée'),
        ('ZONE_4', 'Zone Standard'),
    ]
    
    zone_key = models.CharField(
        max_length=20,
        unique=True,
        choices=ZONE_CHOICES,
        verbose_name="Zone géographique"
    )
    
    cost_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Coût par personne (FCFA)"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ✅ CORRECT
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Dernière modification par"
    )
    
    last_updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    class Meta:
        db_table = 'services_intervention_costs'
        verbose_name = "Coût d'intervention géographique"
        verbose_name_plural = "Coûts d'intervention géographiques"
        ordering = ['zone_key']
    
    def __str__(self):
        return f"{self.get_zone_key_display()} - {self.cost_per_person:,.0f} FCFA"