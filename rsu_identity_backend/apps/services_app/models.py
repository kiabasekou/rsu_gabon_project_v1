# ===================================================================
# RSU GABON - MODÈLE SOCIAL PROGRAM PARAMÉTRABLE
# Standards Top 1% - Budgets configurables par administrateurs
# ===================================================================

from django.db import models
from django.db.models import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core_app.models import BaseModel

class SocialProgram(BaseModel):
    """
    Modèle maître des programmes sociaux gouvernementaux
    Paramètres configurables par les administrateurs
    """
    
    # Identification programme
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code programme",
        help_text="Code unique du programme (ex: AIDE_ALIMENTAIRE)"
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nom du programme",
        help_text="Nom complet du programme social"
    )
    
    description = models.TextField(
        verbose_name="Description",
        help_text="Description détaillée du programme et objectifs"
    )
    
    # Statut et activation
    is_active = models.BooleanField(
        default=True,
        verbose_name="Programme actif",
        help_text="Désactiver temporairement un programme"
    )
    
    # Paramètres budgétaires (CONFIGURABLES)
    budget_total_fcfa = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Budget total alloué (FCFA)",
        help_text="Budget annuel total alloué au programme"
    )
    
    budget_used_fcfa = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Budget utilisé (FCFA)",
        help_text="Montant déjà engagé ou dépensé"
    )
    
    benefit_amount_fcfa = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Montant bénéfice unitaire (FCFA)",
        help_text="Montant standard par bénéficiaire"
    )
    
    # Paramètres temporels
    duration_months = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        verbose_name="Durée standard (mois)",
        help_text="Durée standard du programme pour un bénéficiaire"
    )
    
    # Critères d'éligibilité (CONFIGURABLES)
    eligibility_criteria = JSONField(
        default=dict,
        verbose_name="Critères d'éligibilité",
        help_text="Critères techniques configurables"
    )
    
    # Exemple structure eligibility_criteria:
    # {
    #     "vulnerability_threshold": 60,
    #     "age_min": 18,
    #     "age_max": 65,
    #     "priority_provinces": ["NYANGA", "OGOOUE_LOLO"],
    #     "requires_children": true,
    #     "min_children": 2,
    #     "gender_preference": "F",
    #     "special_conditions": ["handicap", "orphelin"]
    # }
    
    # Paramètres opérationnels
    max_beneficiaries = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Maximum bénéficiaires",
        help_text="Limite du nombre de bénéficiaires (null = illimité)"
    )
    
    current_beneficiaries = models.PositiveIntegerField(
        default=0,
        verbose_name="Bénéficiaires actuels",
        help_text="Nombre actuel de bénéficiaires inscrits"
    )
    
    # Géolocalisation et ciblage
    target_provinces = JSONField(
        default=list,
        verbose_name="Provinces cibles",
        help_text="Liste des provinces prioritaires pour ce programme"
    )
    
    # Métadonnées programme
    program_type = models.CharField(
        max_length=30,
        choices=[
            ('CASH_TRANSFER', 'Transfert monétaire'),
            ('IN_KIND', 'Aide en nature'),
            ('SERVICE', 'Prestation de service'),
            ('TRAINING', 'Formation'),
            ('CREDIT', 'Crédit/Financement'),
            ('HEALTHCARE', 'Santé'),
            ('EDUCATION', 'Éducation'),
            ('HOUSING', 'Logement'),
            ('EMERGENCY', 'Aide d\'urgence'),
        ],
        verbose_name="Type de programme"
    )
    
    priority_level = models.CharField(
        max_length=20,
        choices=[
            ('CRITICAL', 'Critique'),
            ('HIGH', 'Élevée'),
            ('MEDIUM', 'Moyenne'),
            ('LOW', 'Faible'),
        ],
        default='MEDIUM',
        verbose_name="Niveau de priorité gouvernementale"
    )
    
    # Dates de validité
    start_date = models.DateField(
        verbose_name="Date de début",
        help_text="Date de lancement du programme"
    )
    
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de fin",
        help_text="Date de fin prévue (null = programme permanent)"
    )
    
    # Contact et responsabilité
    responsible_ministry = models.CharField(
        max_length=100,
        verbose_name="Ministère responsable",
        help_text="Ministère ou organisme gestionnaire"
    )
    
    contact_person = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Personne de contact",
        help_text="Responsable administratif du programme"
    )
    
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone contact",
        help_text="Numéro de téléphone du responsable"
    )
    
    contact_email = models.EmailField(
        blank=True,
        verbose_name="Email contact",
        help_text="Email du responsable du programme"
    )
    
    # Paramètres avancés
    requires_documents = JSONField(
        default=list,
        verbose_name="Documents requis",
        help_text="Liste des documents nécessaires pour l'inscription"
    )
    
    automated_enrollment = models.BooleanField(
        default=False,
        verbose_name="Inscription automatique",
        help_text="Inscription automatique des personnes éligibles"
    )
    
    payment_frequency = models.CharField(
        max_length=20,
        choices=[
            ('MONTHLY', 'Mensuel'),
            ('QUARTERLY', 'Trimestriel'),
            ('BIANNUAL', 'Semestriel'),
            ('ANNUAL', 'Annuel'),
            ('ONE_TIME', 'Paiement unique'),
        ],
        default='MONTHLY',
        verbose_name="Fréquence de paiement"
    )
    
    # Indicateurs de performance
    success_indicators = JSONField(
        default=dict,
        verbose_name="Indicateurs de succès",
        help_text="KPI et métriques de performance du programme"
    )
    
    class Meta:
        db_table = 'services_social_programs'
        verbose_name = "Programme Social"
        verbose_name_plural = "Programmes Sociaux"
        ordering = ['priority_level', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def budget_remaining_fcfa(self):
        """Budget restant disponible"""
        return self.budget_total_fcfa - self.budget_used_fcfa
    
    @property
    def budget_utilization_percentage(self):
        """Pourcentage d'utilisation du budget"""
        if self.budget_total_fcfa > 0:
            return (self.budget_used_fcfa / self.budget_total_fcfa) * 100
        return 0
    
    @property
    def is_budget_available(self):
        """Vérifie si budget disponible pour nouveaux bénéficiaires"""
        return self.budget_remaining_fcfa >= self.benefit_amount_fcfa
    
    @property
    def can_accept_new_beneficiaries(self):
        """Vérifie si peut accepter nouveaux bénéficiaires"""
        # Vérifier limite nombre
        if self.max_beneficiaries and self.current_beneficiaries >= self.max_beneficiaries:
            return False
        
        # Vérifier budget
        if not self.is_budget_available:
            return False
        
        # Vérifier dates
        from django.utils import timezone
        if self.end_date and timezone.now().date() > self.end_date:
            return False
        
        return self.is_active
    
    @property
    def estimated_beneficiaries_possible(self):
        """Nombre estimé de bénéficiaires possibles avec budget restant"""
        if self.benefit_amount_fcfa > 0:
            return int(self.budget_remaining_fcfa / self.benefit_amount_fcfa)
        return 0
    
    def update_budget_usage(self, amount_fcfa):
        """Met à jour l'utilisation du budget"""
        self.budget_used_fcfa += amount_fcfa
        self.save(update_fields=['budget_used_fcfa'])
    
    def add_beneficiary(self):
        """Ajoute un bénéficiaire et met à jour les compteurs"""
        if self.can_accept_new_beneficiaries:
            self.current_beneficiaries += 1
            self.update_budget_usage(self.benefit_amount_fcfa)
            self.save(update_fields=['current_beneficiaries'])
            return True
        return False
    
    def remove_beneficiary(self, refund_budget=True):
        """Retire un bénéficiaire et ajuste les compteurs"""
        if self.current_beneficiaries > 0:
            self.current_beneficiaries -= 1
            if refund_budget:
                self.budget_used_fcfa = max(0, self.budget_used_fcfa - self.benefit_amount_fcfa)
            self.save(update_fields=['current_beneficiaries', 'budget_used_fcfa'])


class ProgramBudgetHistory(BaseModel):
    """
    Historique des modifications budgétaires
    Traçabilité des changements administrateurs
    """
    program = models.ForeignKey(
        SocialProgram,
        on_delete=models.CASCADE,
        related_name='budget_history',
        verbose_name="Programme"
    )
    
    # Ancien état
    previous_budget_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Ancien budget total"
    )
    
    previous_benefit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ancien montant bénéfice"
    )
    
    # Nouvel état
    new_budget_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Nouveau budget total"
    )
    
    new_benefit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Nouveau montant bénéfice"
    )
    
    # Métadonnées changement
    change_reason = models.TextField(
        verbose_name="Raison du changement",
        help_text="Justification de la modification budgétaire"
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
    
    approved_by = models.ForeignKey(
        'core_app.RSUUser',
        on_delete=models.PROTECT,
        verbose_name="Approuvé par",
        help_text="Administrateur ayant approuvé le changement"
    )
    
    effective_date = models.DateField(
        verbose_name="Date d'effet",
        help_text="Date d'entrée en vigueur du changement"
    )
    
    class Meta:
        db_table = 'services_program_budget_history'
        verbose_name = "Historique Budget Programme"
        verbose_name_plural = "Historiques Budgets Programmes"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Changement budget {self.program.name} - {self.created_at.strftime('%d/%m/%Y')}"