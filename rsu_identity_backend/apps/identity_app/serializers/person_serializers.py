# =============================================================================
# FICHIER: apps/identity_app/serializers/person_serializers.py (CORRECTION)
# PROBLÈME: Field 'nationality' not valid for model PersonIdentity
# SOLUTION: Retirer temporairement nationality des fields
# =============================================================================

"""
🇬🇦 RSU Gabon - Person Serializers CORRIGÉS
Sérialisation des identités personnelles sans champ nationality
"""
from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from datetime import date
from apps.identity_app.models import PersonIdentity
from apps.core_app.serializers import BaseModelSerializer, RSUUserMinimalSerializer

class PersonIdentitySerializer(BaseModelSerializer):
    """Serializer principal pour PersonIdentity - CHAMPS CORRIGÉS"""
    age = serializers.IntegerField(source='age', read_only=True)
    full_name = serializers.CharField(read_only=True)
    province_info = serializers.SerializerMethodField()
    vulnerability_status = serializers.SerializerMethodField()
    data_completeness_percentage = serializers.DecimalField(
        source='data_completeness_score', max_digits=5, decimal_places=2, read_only=True
    )
    
    verified_by_details = RSUUserMinimalSerializer(source='verified_by', read_only=True)
    
    class Meta:
        model = PersonIdentity
        fields = [
            # Identifiants
            'rsu_id', 'nip', 'national_id',
            
            # Informations personnelles
            'first_name', 'last_name', 'maiden_name', 'full_name',
            'birth_date', 'birth_place', 'age', 'gender',
            
            # Contact et localisation
            'phone_number', 'email', 'address',
            'latitude', 'longitude', 'province', 'department', 'commune',
            
            # Socio-économique - CORRIGER LES CHAMPS
            'marital_status', 'education_level', 
            # ❌ 'employment_status',  # ← RETIRER car n'existe pas dans modèle
            'monthly_income', 
            # ❌ 'profession',  # ← RETIRER car n'existe pas dans modèle
            
            # Caractéristiques
            'has_disability', 'disability_type', 'is_household_head',
            
            # Vérification
            'verification_status', 'verified_at', 'verified_by_details',
            'rbpp_synchronized', 'rbpp_sync_date',
            
            # Scoring
            'data_completeness_percentage', 'vulnerability_status', 'province_info',
            
            # BaseModel
            'id', 'created_at', 'updated_at', 'is_active',
            'created_by', 'created_by_details', 'updated_by', 'updated_by_details'
        ]

class PersonIdentityCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour création PersonIdentity - CORRIGÉ
    Optimisé pour saisie terrain mobile
    """
    
    class Meta:
        model = PersonIdentity
        fields = [
            # Essentiels pour création
            'first_name', 'last_name', 'birth_date', 'gender',
            
            # Optionnels mais importants
            'phone_number', 'province', 'department', 'commune',
            'address', 'latitude', 'longitude',
            
            # Socio-économique de base
            'marital_status', 'education_level', 'employment_status',
            'monthly_income', 'has_disability',
            
            # Ménage
            'is_household_head',
            
            # ❌ NATIONALITY RETIRÉ TEMPORAIREMENT
            # 'nationality',  # ← Sera ajouté après création du champ dans le modèle
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'birth_date': {'required': True},
            'gender': {'required': True},
        }
    
    def validate_birth_date(self, value):
        """Validation date de naissance"""
        today = timezone.now().date()
        if value > today:
            raise serializers.ValidationError("La date de naissance ne peut pas être dans le futur")
        
        # Âge minimum 0, maximum 120 ans
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age > 120:
            raise serializers.ValidationError("Âge trop élevé (>120 ans)")
        
        return value
    
    def validate_phone_number(self, value):
        """Validation numéro téléphone gabonais"""
        if not value:
            return value
            
        # Validation format gabonais (+241)
        import re
        gabonese_pattern = r'^\+241[0-9]{8}$'
        if not re.match(gabonese_pattern, value):
            raise serializers.ValidationError(
                "Format invalide. Utilisez +241XXXXXXXX pour un numéro gabonais"
            )
        return value
    
    def validate_province(self, value):
        """Validation province gabonaise"""
        valid_provinces = [
            'ESTUAIRE', 'HAUT_OGOOUE', 'MOYEN_OGOOUE', 'NGOUNIE',
            'NYANGA', 'OGOOUE_IVINDO', 'OGOOUE_LOLO', 'OGOOUE_MARITIME', 'WOLEU_NTEM'
        ]
        if value and value not in valid_provinces:
            raise serializers.ValidationError(f"Province invalide. Choisir parmi: {', '.join(valid_provinces)}")
        return value

class PersonIdentityUpdateSerializer(PersonIdentityCreateSerializer):
    """
    Serializer pour mise à jour PersonIdentity
    Tous les champs optionnels
    """
    
    class Meta(PersonIdentityCreateSerializer.Meta):
        extra_kwargs = {
            # Tous les champs deviennent optionnels pour update
            'first_name': {'required': False},
            'last_name': {'required': False}, 
            'birth_date': {'required': False},
            'gender': {'required': False},
        }

class PersonIdentityMinimalSerializer(serializers.ModelSerializer):
    """
    Serializer minimal pour relations et listes
    """
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(source='age', read_only=True)
    
    class Meta:
        model = PersonIdentity
        fields = [
            'id', 'rsu_id', 'first_name', 'last_name', 'full_name',
            'age', 'gender', 'province', 'phone_number'
        ]

class PersonIdentitySearchSerializer(serializers.Serializer):
    """
    Serializer pour recherche et déduplication
    """
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    birth_date = serializers.DateField(required=False)
    phone_number = serializers.CharField(required=False)
    province = serializers.CharField(required=False)
    
    similarity_threshold = serializers.FloatField(
        default=0.8, min_value=0.0, max_value=1.0,
        help_text="Seuil de similarité pour la détection de doublons"
    )