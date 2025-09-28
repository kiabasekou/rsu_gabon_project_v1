# ===================================================================
# RSU GABON - INTÉGRATION SERVICES APP DANS ARCHITECTURE EXISTANTE
# Standards Top 1% - Continuité avec Core + Identity Apps
# ===================================================================


# apps/services_app/models.py
from django.db import models
#from django.contrib.postgres.fields import JSONField #supprimé dans les versions récentes de Django (à partir de Django 4.0).
from django.db.models import JSONField
from apps.core_app.models import BaseModel
from apps.identity_app.models import PersonIdentity

class VulnerabilityAssessment(BaseModel):
    """
    Évaluations vulnérabilité avec historique
    Stockage des scores et recommandations IA
    """
    person = models.ForeignKey(
        PersonIdentity,
        on_delete=models.CASCADE,
        related_name='vulnerability_assessments',
        verbose_name="Personne évaluée"
    )
    
    # Scores calculés
    global_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score global vulnérabilité (0-100)"
    )
    
    vulnerability_level = models.CharField(
        max_length=20,
        choices=[
            ('CRITICAL', 'Critique'),
            ('HIGH', 'Élevée'),
            ('MODERATE', 'Modérée'),
            ('LOW', 'Faible'),
        ],
        verbose_name="Niveau vulnérabilité"
    )
    
    # Scores par dimension (JSON)
    dimension_scores = JSONField(
        default=dict,
        verbose_name="Scores par dimension"
    )
    
    # Recommandations IA
    priority_interventions = JSONField(
        default=list,
        verbose_name="Interventions prioritaires"
    )
    
    social_programs_eligibility = JSONField(
        default=dict,
        verbose_name="Éligibilité programmes sociaux"
    )
    
    geographic_priority_zone = models.CharField(
        max_length=30,
        verbose_name="Zone priorité géographique"
    )
    
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score confiance évaluation"
    )
    
    # Métadonnées
    assessment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date évaluation"
    )
    
    assessed_by = models.ForeignKey(
        'core_app.RSUUser',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Évaluateur"
    )
    
    class Meta:
        db_table = 'services_vulnerability_assessments'
        verbose_name = "Évaluation vulnérabilité"
        verbose_name_plural = "Évaluations vulnérabilité"
        ordering = ['-assessment_date']

class SocialProgramEligibility(BaseModel):
    """
    Éligibilité programmes sociaux calculée par IA
    """
    person = models.ForeignKey(
        PersonIdentity,
        on_delete=models.CASCADE,
        related_name='program_eligibilities'
    )
    
    program_code = models.CharField(
        max_length=50,
        choices=[
            ('TRANSFERTS_MONETAIRES', 'Transferts Monétaires'),
            ('NUTRITION_MATERNELLE', 'Nutrition Maternelle'),
            ('DEVELOPPEMENT_RURAL', 'Développement Rural'),
            ('FORMATION_PROFESSIONNELLE', 'Formation Professionnelle'),
            ('AIDE_URGENCE', 'Aide d\'Urgence'),
            ('SANTE_GRATUITE', 'Soins Santé Gratuits'),
            ('BOURSES_EDUCATION', 'Bourses Éducation'),
            ('APPUI_HANDICAP', 'Appui Handicap'),
        ],
        verbose_name="Code programme"
    )
    
    eligibility_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Score éligibilité (0-100)"
    )
    
    recommendation_level = models.CharField(
        max_length=20,
        choices=[
            ('IMMEDIATE', 'Immédiate'),
            ('HIGH', 'Prioritaire'),
            ('MEDIUM', 'Modérée'),
            ('LOW', 'Faible'),
        ],
        verbose_name="Niveau recommandation"
    )
    
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'services_program_eligibility'
        unique_together = ('person', 'program_code')