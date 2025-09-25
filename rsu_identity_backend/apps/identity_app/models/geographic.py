

# =============================================================================
# FICHIER: apps/identity_app/models/geographic.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Modèles Géographiques
Données géospatiales et accessibilité des services
"""
from django.db import models
from apps.core_app.models.base import BaseModel

class GeographicData(BaseModel):
    """
    Données géographiques et d'accessibilité pour chaque localité
    Essentiel pour le ciblage géographique des programmes
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
    
    ROAD_CONDITIONS = [
        ('PAVED', 'Route Goudronnée'),
        ('GRAVEL', 'Route en Gravier'),
        ('DIRT', 'Piste en Terre'),
        ('SEASONAL', 'Praticable en Saison Sèche'),
        ('IMPASSABLE', 'Impraticable'),
    ]
    
    # Identification géographique
    location_name = models.CharField(
        max_length=200,
        verbose_name="Nom de la Localité"
    )
    province = models.CharField(
        max_length=50,
        verbose_name="Province"
    )
    department = models.CharField(
        max_length=100,
        verbose_name="Département"
    )
    commune = models.CharField(
        max_length=100,
        verbose_name="Commune"
    )
    
    # Coordonnées centrales de la zone
    center_latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        verbose_name="Latitude Centre"
    )
    center_longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        verbose_name="Longitude Centre"
    )
    
    # Caractéristiques géographiques
    zone_type = models.CharField(
        max_length=20, 
        choices=ZONE_TYPES,
        verbose_name="Type de Zone"
    )
    population_estimate = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name="Population Estimée"
    )
    area_km2 = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Superficie (km²)"
    )
    
    # Accessibilité transport
    road_condition = models.CharField(
        max_length=20, 
        choices=ROAD_CONDITIONS,
        null=True, 
        blank=True,
        verbose_name="État des Routes"
    )
    distance_to_main_road_km = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Distance Route Principale (km)"
    )
    public_transport_available = models.BooleanField(
        default=False,
        verbose_name="Transport Public Disponible"
    )
    
    # Services essentiels - Distances en kilomètres
    distance_to_health_center_km = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Distance Centre de Santé (km)"
    )
    distance_to_hospital_km = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Distance Hôpital (km)"
    )
    distance_to_school_km = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Distance École (km)"
    )
    distance_to_secondary_school_km = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Distance Collège/Lycée (km)"
    )
    distance_to_market_km = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Distance Marché (km)"
    )
    distance_to_bank_km = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Distance Banque (km)"
    )
    distance_to_admin_center_km = models.FloatField(
        null=True, 
        blank=True,
        verbose_name="Distance Centre Administratif (km)"
    )
    
    # Connectivité
    mobile_network_coverage = models.BooleanField(
        default=False,
        verbose_name="Couverture Réseau Mobile"
    )
    internet_available = models.BooleanField(
        default=False,
        verbose_name="Internet Disponible"
    )
    
    # Risques et défis
    flood_risk = models.BooleanField(
        default=False,
        verbose_name="Risque d'Inondation"
    )
    difficult_access_rainy_season = models.BooleanField(
        default=False,
        verbose_name="Accès Difficile Saison Pluies"
    )
    security_concerns = models.BooleanField(
        default=False,
        verbose_name="Préoccupations Sécuritaires"
    )
    
    # Scores calculés
    accessibility_score = models.FloatField(
        default=0.0,
        verbose_name="Score d'Accessibilité"
    )
    service_availability_score = models.FloatField(
        default=0.0,
        verbose_name="Score Disponibilité Services"
    )
    
    def calculate_accessibility_score(self):
        """
        Calcule le score d'accessibilité basé sur les distances et infrastructures
        Score de 0 (très isolé) à 100 (très accessible)
        """
        score = 100
        
        # Pénalités distance services essentiels
        if self.distance_to_health_center_km:
            if self.distance_to_health_center_km > 50:
                score -= 30
            elif self.distance_to_health_center_km > 20:
                score -= 15
                
        if self.distance_to_school_km:
            if self.distance_to_school_km > 10:
                score -= 20
            elif self.distance_to_school_km > 5:
                score -= 10
                
        if self.distance_to_market_km:
            if self.distance_to_market_km > 30:
                score -= 15
                
        # Bonus/pénalités infrastructure
        if self.road_condition == 'IMPASSABLE':
            score -= 25
        elif self.road_condition == 'SEASONAL':
            score -= 15
        elif self.road_condition == 'PAVED':
            score += 10
            
        if self.public_transport_available:
            score += 10
            
        if self.mobile_network_coverage:
            score += 5
            
        if self.difficult_access_rainy_season:
            score -= 10
            
        self.accessibility_score = max(0, min(100, score))
        return self.accessibility_score
    
    def __str__(self):
        return f"{self.location_name} ({self.province})"
    
    class Meta:
        verbose_name = "Données Géographiques"
        verbose_name_plural = "Données Géographiques"
        db_table = 'rsu_geographic_data'
        unique_together = ['location_name', 'province', 'commune']
        ordering = ['province', 'location_name']
