# =============================================================================
# FICHIER: apps/identity_app/models/geographic.py
# CORRECTION: Alignement avec les tests attendus
# =============================================================================

"""
🇬🇦 RSU Gabon - Modèle Données Géographiques
Ciblage zones prioritaires et accessibilité services
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core_app.models.base import BaseModel
from utils.gabonese_data import PROVINCES

class GeographicData(BaseModel):
    """
    Données géographiques et d'accessibilité des services
    Pour ciblage programmes sociaux par zone
    """
    ZONE_TYPES = [
        ('URBAN_CENTER', 'Centre Urbain'),
        ('URBAN_PERIPHERY', 'Périphérie Urbaine'),
        ('RURAL_ACCESSIBLE', 'Rural Accessible'),
        ('RURAL_REMOTE', 'Rural Isolé'),
        ('COASTAL', 'Zone Côtière'),
        ('FOREST', 'Zone Forestière'),
        ('MINING', 'Zone Minière'),
        ('BORDER', 'Zone Frontalière'),
    ]
    
    PROVINCES_CHOICES = [(code, data['name']) for code, data in PROVINCES.items()]
    
    # === IDENTIFIANTS GÉOGRAPHIQUES ===
    location_name = models.CharField(
        max_length=200,
        verbose_name="Nom localité"
    )
    province = models.CharField(
        max_length=50,
        choices=PROVINCES_CHOICES,
        verbose_name="Province"
    )
    commune = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Commune"
    )
    # ✅ AJOUT: Champ department attendu par test_accessibility_score_calculation
    department = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Département"
    )
    # ✅ AJOUT: Champ district attendu par les tests
    district = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="District/Arrondissement"
    )
    zone_type = models.CharField(
        max_length=30,
        choices=ZONE_TYPES,
        default='RURAL_ACCESSIBLE',
        verbose_name="Type de zone"
    )
    
    # === COORDONNÉES GPS ===
    # ✅ AJOUT: Champs latitude/longitude attendus par les tests
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-4.0),  # Limite sud Gabon
            MaxValueValidator(2.3)    # Limite nord Gabon
        ],
        verbose_name="Latitude"
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(8.5),   # Limite ouest Gabon
            MaxValueValidator(14.5)   # Limite est Gabon
        ],
        verbose_name="Longitude"
    )
    
    # === ACCESSIBILITÉ SERVICES ===
    # ✅ AJOUT: Champs distances attendus par les tests
    distance_to_hospital = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Distance hôpital (km)",
        help_text="Distance au centre de santé le plus proche"
    )
    distance_to_school = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Distance école (km)",
        help_text="Distance à l'école primaire la plus proche"
    )
    distance_to_market = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Distance marché (km)"
    )
    distance_to_road = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Distance route praticable (km)"
    )
    
    # === INFRASTRUCTURES DISPONIBLES ===
    # ✅ AJOUT: Champs infrastructure attendus par les tests
    has_electricity = models.BooleanField(
        default=False,
        verbose_name="Accès électricité"
    )
    has_water = models.BooleanField(
        default=False,
        verbose_name="Accès eau potable"
    )
    has_road_access = models.BooleanField(
        default=False,
        verbose_name="Accès routier praticable"
    )
    has_mobile_coverage = models.BooleanField(
        default=False,
        verbose_name="Couverture mobile"
    )
    has_internet = models.BooleanField(
        default=False,
        verbose_name="Accès internet"
    )
    
    # === DONNÉES DÉMOGRAPHIQUES ===
    estimated_population = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Population estimée"
    )
    population_density = models.CharField(
        max_length=20,
        choices=[
            ('VERY_LOW', 'Très Faible'),
            ('LOW', 'Faible'),
            ('MEDIUM', 'Moyenne'),
            ('HIGH', 'Élevée'),
            ('VERY_HIGH', 'Très Élevée'),
        ],
        null=True,
        blank=True,
        verbose_name="Densité population"
    )
    
    # === SCORES CALCULÉS ===
    accessibility_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Score accessibilité (0-100)"
    )
    vulnerability_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Score vulnérabilité (0-100)"
    )
    priority_level = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Faible'),
            ('MEDIUM', 'Moyenne'),
            ('HIGH', 'Élevée'),
            ('CRITICAL', 'Critique'),
        ],
        default='MEDIUM',
        verbose_name="Niveau priorité"
    )
    
    def calculate_accessibility_score(self):
        """
        ✅ MÉTHODE ATTENDUE PAR LES TESTS
        Calcule score d'accessibilité basé sur distances et infrastructures
        """
        score = 0
        max_score = 100
        
        # Score infrastructure (40 points max)
        infrastructure_items = [
            self.has_electricity,
            self.has_water,
            self.has_road_access,
            self.has_mobile_coverage
        ]
        infrastructure_score = sum(infrastructure_items) * 10  # 10 points par item
        
        # Score distances (60 points max)
        distance_score = 0
        distances = [
            ('hospital', self.distance_to_hospital),
            ('school', self.distance_to_school),
            ('market', self.distance_to_market),
            ('road', self.distance_to_road)
        ]
        
        for service, distance in distances:
            if distance is not None:
                # Plus la distance est courte, plus le score est élevé
                if distance <= 5:
                    distance_score += 15  # Excellent accès
                elif distance <= 15:
                    distance_score += 10  # Bon accès
                elif distance <= 30:
                    distance_score += 5   # Accès moyen
                # Distance > 30km = 0 points
        
        total_score = infrastructure_score + distance_score
        self.accessibility_score = min(total_score, max_score)
        return self.accessibility_score
    
    def save(self, *args, **kwargs):
        """Auto-calcul scores avant sauvegarde"""
        self.calculate_accessibility_score()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.location_name} - {self.get_province_display()}"
    
    class Meta:
        verbose_name = "Données Géographiques"
        verbose_name_plural = "Données Géographiques"
        db_table = 'rsu_geographic_data'
        ordering = ['province', 'location_name']
        unique_together = [['location_name', 'province', 'commune']]
        indexes = [
            models.Index(fields=['province', 'zone_type']),
            models.Index(fields=['accessibility_score']),
            models.Index(fields=['priority_level']),
        ]