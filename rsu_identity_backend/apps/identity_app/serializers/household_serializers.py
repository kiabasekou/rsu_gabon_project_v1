
# =============================================================================
# FICHIER: apps/identity_app/serializers/household_serializers.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Household Serializers
Sérialisation des ménages et membres
"""
from rest_framework import serializers
from apps.identity_app.models import Household, HouseholdMember
from apps.core_app.serializers import BaseModelSerializer
from .person_serializers import PersonIdentityMinimalSerializer

class HouseholdMemberSerializer(BaseModelSerializer):
    """Serializer pour membres de ménage"""
    person_details = PersonIdentityMinimalSerializer(source='person', read_only=True)
    relationship_display = serializers.CharField(
        source='get_relationship_to_head_display', read_only=True
    )
    
    class Meta:
        model = HouseholdMember
        fields = [
            'id', 'person', 'person_details', 'relationship_to_head', 
            'relationship_display', 'joined_household_date', 'left_household_date',
            'is_current_member', 'contributes_to_income', 'monthly_contribution',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class HouseholdMemberCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création membre de ménage"""
    
    class Meta:
        model = HouseholdMember
        fields = [
            'person', 'relationship_to_head', 'joined_household_date',
            'contributes_to_income', 'monthly_contribution'
        ]
        extra_kwargs = {
            'person': {'required': True},
            'relationship_to_head': {'required': True}
        }

class HouseholdSerializer(BaseModelSerializer):
    """
    Serializer principal pour Household
    Vue complète avec membres et statistiques
    """
    head_details = PersonIdentityMinimalSerializer(source='head_of_household', read_only=True)
    members = HouseholdMemberSerializer(many=True, read_only=True)
    members_count = serializers.IntegerField(source='get_members_count', read_only=True)
    dependency_ratio = serializers.SerializerMethodField()
    household_type_display = serializers.CharField(
        source='get_household_type_display', read_only=True
    )
    vulnerability_indicators = serializers.SerializerMethodField()
    
    class Meta:
        model = Household
        fields = [
            # Identification
            'household_id', 'head_of_household', 'head_details',
            
            # Caractéristiques
            'household_type', 'household_type_display', 'household_size',
            'housing_type', 'number_of_rooms',
            
            # Services
            'water_access', 'electricity_access', 'has_toilet',
            
            # Économie
            'total_monthly_income', 'has_bank_account', 'assets',
            
            # Agriculture
            'has_agricultural_land', 'agricultural_land_size', 'livestock',
            
            # Vulnérabilités
            'has_disabled_members', 'has_elderly_members',
            'has_pregnant_women', 'has_children_under_5',
            'vulnerability_indicators',
            
            # Localisation
            'latitude', 'longitude', 'province',
            
            # Métadonnées
            'last_visit_date', 'vulnerability_score',
            'members', 'members_count', 'dependency_ratio',
            
            # BaseModel
            'id', 'created_at', 'updated_at', 'is_active',
            'created_by', 'created_by_details', 'updated_by', 'updated_by_details'
        ]
        read_only_fields = [
            'household_id', 'members_count', 'dependency_ratio',
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
    
    def get_dependency_ratio(self, obj):
        """Calcul ratio de dépendance"""
        return obj.calculate_dependency_ratio()
    
    def get_vulnerability_indicators(self, obj):
        """Indicateurs de vulnérabilité du ménage"""
        indicators = []
        
        if obj.has_disabled_members:
            indicators.append('disabled_members')
        if obj.has_elderly_members:
            indicators.append('elderly_members')
        if obj.has_children_under_5:
            indicators.append('young_children')
        if obj.has_pregnant_women:
            indicators.append('pregnant_women')
        if obj.total_monthly_income and obj.total_monthly_income < 150000:
            indicators.append('low_income')
        if obj.water_access in ['VENDOR', 'NONE']:
            indicators.append('water_access_poor')
        if obj.electricity_access == 'NONE':
            indicators.append('no_electricity')
        if not obj.has_toilet:
            indicators.append('no_sanitation')
        
        return {
            'indicators': indicators,
            'count': len(indicators),
            'level': 'HIGH' if len(indicators) >= 4 else 'MODERATE' if len(indicators) >= 2 else 'LOW'
        }

class HouseholdCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour création de ménage
    Essentiels pour enquêtes terrain
    """
    
    class Meta:
        model = Household
        fields = [
            'head_of_household', 'household_type', 'household_size',
            'housing_type', 'number_of_rooms',
            'water_access', 'electricity_access', 'has_toilet',
            'total_monthly_income', 'has_bank_account',
            'has_disabled_members', 'has_elderly_members',
            'has_pregnant_women', 'has_children_under_5',
            'latitude', 'longitude'
        ]
        extra_kwargs = {
            'head_of_household': {'required': True},
            'household_size': {'required': True}
        }
    
    def validate_household_size(self, value):
        """Validation taille ménage"""
        if value < 1:
            raise serializers.ValidationError("La taille du ménage doit être d'au moins 1 personne")
        if value > 30:  # Limite haute pour ménages étendus gabonais
            raise serializers.ValidationError("Taille de ménage exceptionnellement grande")
        return value
