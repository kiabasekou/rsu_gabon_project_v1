# ===================================================================
# 🇬🇦 RSU GABON - MODÈLES DJANGO + APIs MOTEUR ÉLIGIBILITÉ
# Standards Top 1% - Intégration Architecture Existante
# ===================================================================

# apps/services_app/models/__init__.py - Ajout aux modèles existants

from django.db import models
from django.db.models import JSONField
from decimal import Decimal
from apps.core_app.models import BaseModel
from apps.identity_app.models import PersonIdentity

# ===================================================================
# MODÈLES PROGRAMMES SOCIAUX
# ===================================================================

class SocialProgram(BaseModel):
    """
    Catalogue des programmes sociaux gouvernementaux
    Configuration dynamique des critères d'éligibilité
    """
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Code programme"
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name="Nom du programme"
    )
    
    description = models.TextField(
        verbose_name="Description complète"
    )
    
    # Critères d'éligibilité dynamiques
    eligibility_criteria = JSONField(
        default=dict,
        verbose_name="Critères d'éligibilité",
        help_text="Configuration JSON des critères"
    )
    
    # Contraintes budgétaires
    annual_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Budget annuel (FCFA)"
    )
    
    max_beneficiaries = models.PositiveIntegerField(
        verbose_name="Nombre maximum bénéficiaires"
    )
    
    cost_per_beneficiary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Coût par bénéficiaire (FCFA)"
    )
    
    # Paramètres temporels
    application_deadline = models.DateField(
        null=True, blank=True,
        verbose_name="Date limite candidature"
    )
    
    program_duration_months = models.PositiveIntegerField(
        default=12,
        verbose_name="Durée programme (mois)"
    )
    
    # Ciblage géographique
    target_provinces = JSONField(
        default=list,
        verbose_name="Provinces ciblées"
    )
    
    urban_rural_preference = models.CharField(
        max_length=20,
        choices=[
            ('BOTH', 'Urbain et Rural'),
            ('URBAN_ONLY', 'Urbain seulement'),
            ('RURAL_ONLY', 'Rural seulement'),
            ('RURAL_PRIORITY', 'Priorité rurale'),
        ],
        default='BOTH',
        verbose_name="Préférence urbain/rural"
    )
    
    # Statut programme
    is_active = models.BooleanField(
        default=True,
        verbose_name="Programme actif"
    )
    
    launch_date = models.DateField(
        verbose_name="Date lancement"
    )
    
    class Meta:
        db_table = 'services_social_programs'
        verbose_name = "Programme social"
        verbose_name_plural = "Programmes sociaux"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def current_budget_utilization(self):
        """Calcul utilisation budgétaire actuelle"""
        total_allocated = self.eligibility_assessments.filter(
            allocation_decision='APPROVED'
        ).aggregate(
            total=models.Sum('estimated_annual_cost')
        )['total'] or Decimal('0')
        
        return (total_allocated / self.annual_budget) * 100 if self.annual_budget > 0 else 0
    
    @property
    def remaining_budget(self):
        """Budget restant disponible"""
        total_allocated = self.eligibility_assessments.filter(
            allocation_decision='APPROVED'
        ).aggregate(
            total=models.Sum('estimated_annual_cost')
        )['total'] or Decimal('0')
        
        return self.annual_budget - total_allocated

class ProgramEligibilityAssessment(BaseModel):
    """
    Évaluations d'éligibilité individuelles par programme
    Résultats du moteur IA avec historique complet
    """
    person = models.ForeignKey(
        PersonIdentity,
        on_delete=models.CASCADE,
        related_name='program_eligibility_assessments',
        verbose_name="Personne évaluée"
    )
    
    program = models.ForeignKey(
        SocialProgram,
        on_delete=models.CASCADE,
        related_name='eligibility_assessments',
        verbose_name="Programme social"
    )
    
    # Référence évaluation vulnérabilité
    vulnerability_assessment = models.ForeignKey(
        'VulnerabilityAssessment',
        on_delete=models.CASCADE,
        verbose_name="Évaluation vulnérabilité"
    )
    
    # Scores calculés par IA
    eligibility_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score éligibilité (0-100)"
    )
    
    compatibility_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score compatibilité (0-100)"
    )
    
    # Statut recommandation IA
    recommendation_status = models.CharField(
        max_length=30,
        choices=[
            ('HIGHLY_RECOMMENDED', 'Hautement recommandé'),
            ('RECOMMENDED', 'Recommandé'),
            ('CONDITIONAL', 'Conditionnel'),
            ('NOT_RECOMMENDED', 'Non recommandé'),
            ('INELIGIBLE', 'Non éligible'),
        ],
        verbose_name="Statut recommandation"
    )
    
    # Urgence intervention
    intervention_urgency = models.CharField(
        max_length=20,
        choices=[
            ('CRITICAL', 'Critique'),
            ('HIGH', 'Élevée'),
            ('MEDIUM', 'Moyenne'),
            ('LOW', 'Faible'),
        ],
        verbose_name="Urgence intervention"
    )
    
    # Estimations financières
    estimated_monthly_benefit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Bénéfice mensuel estimé (FCFA)"
    )
    
    estimated_annual_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Coût annuel estimé (FCFA)"
    )
    
    # Priorité de traitement
    processing_priority = models.PositiveIntegerField(
        verbose_name="Priorité traitement (1=plus prioritaire)"
    )
    
    # Impact estimé
    estimated_impact = models.CharField(
        max_length=20,
        choices=[
            ('TRANSFORMATIONAL', 'Transformationnel'),
            ('SIGNIFICANT', 'Significatif'),
            ('MODERATE', 'Modéré'),
            ('LIMITED', 'Limité'),
        ],
        verbose_name="Impact estimé"
    )
    
    # Facteurs d'éligibilité (JSON)
    eligibility_factors = JSONField(
        default=list,
        verbose_name="Facteurs d'éligibilité"
    )
    
    blocking_factors = JSONField(
        default=list,
        verbose_name="Facteurs bloquants"
    )
    
    required_documents = JSONField(
        default=list,
        verbose_name="Documents requis"
    )
    
    # Décision d'allocation
    allocation_decision = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'En attente'),
            ('APPROVED', 'Approuvé'),
            ('REJECTED', 'Rejeté'),
            ('ON_HOLD', 'En suspens'),
            ('CANCELLED', 'Annulé'),
        ],
        default='PENDING',
        verbose_name="Décision allocation"
    )
    
    allocation_date = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Date décision allocation"
    )
    
    # Agent responsable
    assessed_by = models.ForeignKey(
        'core_app.RSUUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='eligibility_assessments',
        verbose_name="Agent évaluateur"
    )
    
    approved_by = models.ForeignKey(
        'core_app.RSUUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_eligibility_assessments',
        verbose_name="Agent approbateur"
    )
    
    # Métadonnées
    assessment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date évaluation"
    )
    
    criteria_snapshot = JSONField(
        default=dict,
        verbose_name="Snapshot critères utilisés"
    )
    
    class Meta:
        db_table = 'services_program_eligibility_assessments'
        verbose_name = "Évaluation éligibilité programme"
        verbose_name_plural = "Évaluations éligibilité programmes"
        ordering = ['-assessment_date', 'processing_priority']
        unique_together = ['person', 'program', 'vulnerability_assessment']
    
    def __str__(self):
        return f"{self.person} - {self.program.code} ({self.recommendation_status})"
    
    @property
    def is_approved(self):
        return self.allocation_decision == 'APPROVED'
    
    @property
    def monthly_allocation(self):
        return self.estimated_monthly_benefit if self.is_approved else Decimal('0')

class GlobalInterventionRecommendation(BaseModel):
    """
    Recommandations globales d'intervention sociale
    Synthèse multi-programmes par personne
    """
    person = models.OneToOneField(
        PersonIdentity,
        on_delete=models.CASCADE,
        related_name='global_intervention_recommendation',
        verbose_name="Personne"
    )
    
    vulnerability_assessment = models.ForeignKey(
        'VulnerabilityAssessment',
        on_delete=models.CASCADE,
        verbose_name="Évaluation vulnérabilité de référence"
    )
    
    # Recommandations générées par IA
    primary_interventions = JSONField(
        default=list,
        verbose_name="Interventions prioritaires"
    )
    
    complementary_actions = JSONField(
        default=list,
        verbose_name="Actions complémentaires"
    )
    
    preventive_measures = JSONField(
        default=list,
        verbose_name="Mesures préventives"
    )
    
    # Métriques globales
    total_recommended_programs = models.PositiveIntegerField(
        verbose_name="Nombre programmes recommandés"
    )
    
    estimated_total_monthly_benefit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Bénéfice mensuel total estimé (FCFA)"
    )
    
    case_complexity = models.CharField(
        max_length=20,
        choices=[
            ('SIMPLE', 'Simple'),
            ('MODÉRÉ', 'Modéré'),
            ('COMPLEXE', 'Complexe'),
            ('TRÈS_COMPLEXE', 'Très complexe'),
        ],
        verbose_name="Complexité du cas"
    )
    
    # Planification suivi
    next_evaluation_date = models.DateField(
        verbose_name="Prochaine évaluation"
    )
    
    follow_up_frequency_months = models.PositiveIntegerField(
        default=3,
        verbose_name="Fréquence suivi (mois)"
    )
    
    # Statut global
    implementation_status = models.CharField(
        max_length=20,
        choices=[
            ('DRAFT', 'Brouillon'),
            ('VALIDATED', 'Validé'),
            ('IN_PROGRESS', 'En cours'),
            ('COMPLETED', 'Terminé'),
            ('SUSPENDED', 'Suspendu'),
        ],
        default='DRAFT',
        verbose_name="Statut mise en œuvre"
    )
    
    class Meta:
        db_table = 'services_global_intervention_recommendations'
        verbose_name = "Recommandation intervention globale"
        verbose_name_plural = "Recommandations interventions globales"
        ordering = ['-created_at']

class AllocationOptimizationBatch(BaseModel):
    """
    Résultats optimisation allocation ressources par batch
    Processus d'allocation optimisée multi-programmes
    """
    batch_name = models.CharField(
        max_length=100,
        verbose_name="Nom du batch"
    )
    
    # Paramètres optimisation
    optimization_objective = models.CharField(
        max_length=30,
        choices=[
            ('maximize_coverage', 'Maximiser couverture'),
            ('maximize_impact', 'Maximiser impact'),
            ('minimize_cost', 'Minimiser coût'),
            ('balance_equity', 'Équilibrer équité'),
        ],
        verbose_name="Objectif optimisation"
    )
    
    target_geographic_zones = JSONField(
        default=list,
        verbose_name="Zones géographiques ciblées"
    )
    
    budget_constraints = JSONField(
        default=dict,
        verbose_name="Contraintes budgétaires"
    )
    
    # Résultats optimisation
    total_persons_evaluated = models.PositiveIntegerField(
        verbose_name="Personnes évaluées"
    )
    
    total_persons_allocated = models.PositiveIntegerField(
        verbose_name="Personnes allouées"
    )
    
    total_allocated_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Budget total alloué (FCFA)"
    )
    
    coverage_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Taux de couverture (%)"
    )
    
    # Détails par programme
    budget_utilization_details = JSONField(
        default=dict,
        verbose_name="Détails utilisation budgétaire"
    )
    
    allocation_matrix = JSONField(
        default=dict,
        verbose_name="Matrice allocation optimisée"
    )
    
    # Métadonnées processus
    optimization_duration_seconds = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Durée optimisation (secondes)"
    )
    
    processed_by = models.ForeignKey(
        'core_app.RSUUser',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Traité par"
    )
    
    class Meta:
        db_table = 'services_allocation_optimization_batches'
        verbose_name = "Batch optimisation allocation"
        verbose_name_plural = "Batches optimisation allocation"
        ordering = ['-created_at']
