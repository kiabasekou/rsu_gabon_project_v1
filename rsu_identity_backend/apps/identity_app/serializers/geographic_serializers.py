
# =============================================================================
# FICHIER: apps/identity_app/serializers/geographic_serializers.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Geographic Serializers
Sérialisation des données géographiques
"""
from rest_framework import serializers
from apps.identity_app.models import GeographicData
from apps.core_app.serializers import BaseModelSerializer

class GeographicDataSerializer(BaseModelSerializer):
    """
    Serializer pour données géographiques
    Calcul automatique des scores d'accessibilité
    """
    zone_type_display = serializers.CharField(
        source='get_zone_type_display', read_only=True
    )
    road_condition_display = serializers.CharField(
        source='get_road_condition_display', read_only=True
    )
    accessibility_level = serializers.SerializerMethodField()
    services_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = GeographicData
        fields = [
            # Identification
            'location_name', 'province', 'department', 'commune',
            
            # Coordonnées
            'center_latitude', 'center_longitude',
            
            # Caractéristiques
            'zone_type', 'zone_type_display', 'population_estimate', 'area_km2',
            'road_condition', 'road_condition_display', 'distance_to_main_road_km',
            'public_transport_available',
            
            # Distances services
            'distance_to_health_center_km', 'distance_to_hospital_km',
            'distance_to_school_km', 'distance_to_secondary_school_km',
            'distance_to_market_km', 'distance_to_bank_km',
            'distance_to_admin_center_km',
            
            # Connectivité
            'mobile_network_coverage', 'internet_available',
            
            # Risques
            'flood_risk', 'difficult_access_rainy_season', 'security_concerns',
            
            # Scores
            'accessibility_score', 'service_availability_score',
            'accessibility_level', 'services_summary',
            
            # BaseModel
            'id', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = [
            'accessibility_score', 'service_availability_score',
            'id', 'created_at', 'updated_at'
        ]
    
    def get_accessibility_level(self, obj):
        """Niveau d'accessibilité textuel"""
        score = obj.accessibility_score
        if score >= 80:
            return 'TRÈS_ACCESSIBLE'
        elif score >= 60:
            return 'ACCESSIBLE'
        elif score >= 40:
            return 'MOYENNEMENT_ACCESSIBLE'
        elif score >= 20:
            return 'PEU_ACCESSIBLE'
        else:
            return 'TRÈS_ISOLÉ'
    
    def get_services_summary(self, obj):
        """Résumé des services disponibles"""
        services = {}
        
        if obj.distance_to_health_center_km:
            services['santé'] = f"{obj.distance_to_health_center_km}km"
        if obj.distance_to_school_km:
            services['école'] = f"{obj.distance_to_school_km}km"
        if obj.distance_to_market_km:
            services['marché'] = f"{obj.distance_to_market_km}km"
        if obj.distance_to_bank_km:
            services['banque'] = f"{obj.distance_to_bank_km}km"
        
        return services
    
    def update(self, instance, validated_data):
        """Mise à jour avec recalcul des scores"""
        instance = super().update(instance, validated_data)
        instance.calculate_accessibility_score()
        instance.save(update_fields=['accessibility_score'])
        return instance