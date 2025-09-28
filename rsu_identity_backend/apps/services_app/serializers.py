# ===================================================================
# RSU GABON - SERVICES APP SERIALIZERS CORRIGÉS
# Standards Top 1% - Cohérence avec architecture DRF existante
# ===================================================================

from rest_framework import serializers
from django.utils import timezone
from apps.core_app.serializers.base_serializers import BaseModelSerializer
from apps.identity_app.serializers import PersonIdentityMinimalSerializer
from .models import (
    VulnerabilityAssessment, 
    SocialProgramEligibility,
    GeographicPriorityZone
)


class VulnerabilityAssessmentSerializer(BaseModelSerializer):
    """
    Serializer pour évaluations vulnérabilité
    Héritage BaseModelSerializer pour cohérence
    """
    # Relations en lecture seule avec détails
    person_details = PersonIdentityMinimalSerializer(source='person', read_only=True)
    person_name = serializers.CharField(source='person.full_name', read_only=True)
    person_rsu_id = serializers.CharField(source='person.rsu_id', read_only=True)
    person_province = serializers.CharField(source='person.province', read_only=True)
    
    # Détails évaluateur
    assessed_by_name = serializers.CharField(source='assessed_by.full_name', read_only=True)
    assessed_by_role = serializers.CharField(source='assessed_by.user_type', read_only=True)
    
    # Champs calculés
    vulnerability_level_display = serializers.CharField(
        source='get_vulnerability_level_display', 
        read_only=True
    )
    geographic_priority_zone_display = serializers.CharField(
        source='get_geographic_priority_zone_display', 
        read_only=True
    )
    validation_status_display = serializers.CharField(
        source='get_validation_status_display', 
        read_only=True
    )
    
    # Indicateurs métier
    is_critical = serializers.BooleanField(read_only=True)
    days_since_assessment = serializers.SerializerMethodField()
    
    class Meta:
        model = VulnerabilityAssessment
        fields = BaseModelSerializer.Meta.fields + [
            # Identification
            'person', 'person_details', 'person_name', 'person_rsu_id', 'person_province',
            
            # Scores et évaluation
            'global_score', 'vulnerability_level', 'vulnerability_level_display',
            'dimension_scores', 'confidence_score',
            
            # Recommandations IA
            'priority_interventions', 'social_programs_eligibility',
            'geographic_priority_zone', 'geographic_priority_zone_display',
            
            # Métadonnées évaluation
            'assessment_date', 'assessed_by', 'assessed_by_name', 'assessed_by_role',
            
            # Validation et qualité
            'validation_status', 'validation_status_display', 'validator_notes',
            
            # Indicateurs calculés
            'is_critical', 'days_since_assessment'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'assessment_date', 'is_critical', 'days_since_assessment'
        ]
    
    def get_days_since_assessment(self, obj):
        """Nombre de jours depuis l'évaluation"""
        if obj.assessment_date:
            delta = timezone.now() - obj.assessment_date
            return delta.days
        return None
    
    def validate_global_score(self, value):
        """Validation score global"""
        if not (0 <= value <= 100):
            raise serializers.ValidationError(
                "Le score global doit être entre 0 et 100"
            )
        return value
    
    def validate_confidence_score(self, value):
        """Validation score confiance"""
        if not (0 <= value <= 100):
            raise serializers.ValidationError(
                "Le score de confiance doit être entre 0 et 100"
            )
        return value
    
    def validate(self, attrs):
        """Validation croisée des données"""
        attrs = super().validate(attrs)
        
        # Cohérence niveau vulnérabilité vs score global
        global_score = attrs.get('global_score')
        vulnerability_level = attrs.get('vulnerability_level')
        
        if global_score and vulnerability_level:
            if global_score >= 80 and vulnerability_level not in ['CRITICAL', 'HIGH']:
                raise serializers.ValidationError(
                    "Score élevé (≥80) incompatible avec niveau vulnérabilité faible"
                )
            elif global_score <= 30 and vulnerability_level not in ['LOW', 'MODERATE']:
                raise serializers.ValidationError(
                    "Score faible (≤30) incompatible avec niveau vulnérabilité élevé"
                )
        
        return attrs


class SocialProgramEligibilitySerializer(BaseModelSerializer):
    """
    Serializer pour éligibilités programmes sociaux
    Validation métier contextualisée Gabon
    """
    # Relations avec détails
    person_details = PersonIdentityMinimalSerializer(source='person', read_only=True)
    person_name = serializers.CharField(source='person.full_name', read_only=True)
    person_rsu_id = serializers.CharField(source='person.rsu_id', read_only=True)
    
    # Affichages lisibles
    program_name = serializers.CharField(source='get_program_code_display', read_only=True)
    recommendation_level_display = serializers.CharField(
        source='get_recommendation_level_display', 
        read_only=True
    )
    enrollment_status_display = serializers.CharField(
        source='get_enrollment_status_display', 
        read_only=True
    )
    
    # Indicateurs métier
    is_highly_recommended = serializers.BooleanField(read_only=True)
    days_since_calculation = serializers.SerializerMethodField()
    estimated_benefit_amount_fcfa = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialProgramEligibility
        fields = BaseModelSerializer.Meta.fields + [
            # Identification
            'person', 'person_details', 'person_name', 'person_rsu_id',
            
            # Programme et éligibilité
            'program_code', 'program_name', 'eligibility_score',
            'recommendation_level', 'recommendation_level_display',
            
            # Détails critères
            'criteria_met', 'missing_documents', 
            'estimated_benefit_amount', 'estimated_benefit_amount_fcfa',
            
            # Historique et suivi
            'calculated_at', 'enrollment_status', 'enrollment_status_display',
            'enrollment_date',
            
            # Indicateurs calculés
            'is_highly_recommended', 'days_since_calculation'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'calculated_at', 'is_highly_recommended', 'days_since_calculation'
        ]
    
    def get_days_since_calculation(self, obj):
        """Nombre de jours depuis le calcul"""
        if obj.calculated_at:
            delta = timezone.now() - obj.calculated_at
            return delta.days
        return None
    
    def get_estimated_benefit_amount_fcfa(self, obj):
        """Montant formaté en FCFA"""
        if obj.estimated_benefit_amount:
            return f"{obj.estimated_benefit_amount:,.0f} FCFA"
        return None
    
    def validate_eligibility_score(self, value):
        """Validation score éligibilité"""
        if not (0 <= value <= 100):
            raise serializers.ValidationError(
                "Le score d'éligibilité doit être entre 0 et 100"
            )
        return value
    
    def validate_estimated_benefit_amount(self, value):
        """Validation montant bénéfice"""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Le montant estimé ne peut pas être négatif"
            )
        return value
    
    def validate(self, attrs):
        """Validation métier programmes sociaux Gabon"""
        attrs = super().validate(attrs)
        
        program_code = attrs.get('program_code')
        eligibility_score = attrs.get('eligibility_score')
        recommendation_level = attrs.get('recommendation_level')
        
        # Règles métier par programme
        if program_code and eligibility_score:
            # Programmes avec seuils élevés
            high_threshold_programs = ['AIDE_ALIMENTAIRE', 'AIDE_LOGEMENT', 'MICRO_CREDIT']
            
            if program_code in high_threshold_programs:
                if eligibility_score >= 80 and recommendation_level == 'NOT_ELIGIBLE':
                    raise serializers.ValidationError(
                        f"Score élevé ({eligibility_score}) incompatible avec 'Non éligible' pour {program_code}"
                    )
        
        # Validation dates enrollment
        enrollment_status = attrs.get('enrollment_status')
        enrollment_date = attrs.get('enrollment_date')
        
        if enrollment_status == 'ENROLLED' and not enrollment_date:
            raise serializers.ValidationError(
                "Date d'inscription requise pour statut 'Inscrit'"
            )
        
        if enrollment_status == 'NOT_ENROLLED' and enrollment_date:
            raise serializers.ValidationError(
                "Date d'inscription non permise pour statut 'Non inscrit'"
            )
        
        return attrs


class GeographicPriorityZoneSerializer(BaseModelSerializer):
    """
    Serializer pour zones priorité géographique
    Optimisation déploiement ressources gouvernementales
    """
    # Affichages lisibles
    province_display = serializers.CharField(source='get_province_display', read_only=True)
    priority_level_display = serializers.CharField(
        source='get_priority_level_display', 
        read_only=True
    )
    
    # Coordonnées formatées
    coordinates_display = serializers.SerializerMethodField()
    coverage_area_km2 = serializers.SerializerMethodField()
    
    # Statistiques calculées
    population_density = serializers.SerializerMethodField()
    
    class Meta:
        model = GeographicPriorityZone
        fields = BaseModelSerializer.Meta.fields + [
            # Identification zone
            'zone_code', 'zone_name', 'province', 'province_display',
            'priority_level', 'priority_level_display',
            
            # Indicateurs socio-économiques
            'vulnerability_indicators', 'population_estimate', 'population_density',
            
            # Géolocalisation
            'center_latitude', 'center_longitude', 'coordinates_display',
            'radius_km', 'coverage_area_km2'
        ]
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + [
            'coordinates_display', 'coverage_area_km2', 'population_density'
        ]
    
    def get_coordinates_display(self, obj):
        """Coordonnées GPS formatées"""
        if obj.center_latitude and obj.center_longitude:
            return f"{obj.center_latitude:.4f}, {obj.center_longitude:.4f}"
        return None
    
    def get_coverage_area_km2(self, obj):
        """Surface approximative de couverture"""
        if obj.radius_km:
            import math
            area = math.pi * (obj.radius_km ** 2)
            return round(area, 2)
        return None
    
    def get_population_density(self, obj):
        """Densité population par km²"""
        coverage_area = self.get_coverage_area_km2(obj)
        if coverage_area and coverage_area > 0:
            density = obj.population_estimate / coverage_area
            return round(density, 1)
        return None
    
    def validate_zone_code(self, value):
        """Validation code zone unique"""
        if value:
            value = value.upper().strip()
            if len(value) < 3:
                raise serializers.ValidationError(
                    "Le code zone doit contenir au moins 3 caractères"
                )
        return value
    
    def validate_population_estimate(self, value):
        """Validation estimation population"""
        if value <= 0:
            raise serializers.ValidationError(
                "L'estimation de population doit être positive"
            )
        if value > 500000:  # Sanity check pour zones
            raise serializers.ValidationError(
                "Estimation de population trop élevée pour une zone (max 500,000)"
            )
        return value
    
    def validate(self, attrs):
        """Validation géographique"""
        attrs = super().validate(attrs)
        
        # Validation coordonnées Gabon
        center_lat = attrs.get('center_latitude')
        center_lng = attrs.get('center_longitude')
        
        if center_lat and center_lng:
            # Limites approximatives du Gabon
            if not (-4.0 <= center_lat <= 2.5):
                raise serializers.ValidationError(
                    "Latitude hors limites Gabon (-4.0 à 2.5)"
                )
            if not (8.5 <= center_lng <= 15.0):
                raise serializers.ValidationError(
                    "Longitude hors limites Gabon (8.5 à 15.0)"
                )
        
        # Validation cohérence priority_level vs vulnerability_indicators
        priority_level = attrs.get('priority_level')
        vulnerability_indicators = attrs.get('vulnerability_indicators', {})
        
        if priority_level == 'CRITICAL' and vulnerability_indicators:
            # Zones critiques doivent avoir indicateurs élevés
            avg_vulnerability = sum(vulnerability_indicators.values()) / len(vulnerability_indicators) if vulnerability_indicators else 0
            if avg_vulnerability < 70:
                raise serializers.ValidationError(
                    "Zone 'Critique' doit avoir indicateurs vulnérabilité élevés (>70)"
                )
        
        return attrs


# Serializers minimaux pour relations
class VulnerabilityAssessmentMinimalSerializer(serializers.ModelSerializer):
    """Serializer minimal pour relations"""
    vulnerability_level_display = serializers.CharField(
        source='get_vulnerability_level_display', 
        read_only=True
    )
    
    class Meta:
        model = VulnerabilityAssessment
        fields = [
            'id', 'global_score', 'vulnerability_level', 'vulnerability_level_display',
            'assessment_date'
        ]


class SocialProgramEligibilityMinimalSerializer(serializers.ModelSerializer):
    """Serializer minimal pour relations"""
    program_name = serializers.CharField(source='get_program_code_display', read_only=True)
    
    class Meta:
        model = SocialProgramEligibility
        fields = [
            'id', 'program_code', 'program_name', 'eligibility_score',
            'recommendation_level', 'calculated_at'
        ]