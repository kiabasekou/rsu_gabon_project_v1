
# =============================================================================
# FICHIER: apps/identity_app/serializers/person_serializers.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Person Serializers
Sérialisation des identités personnelles
"""
from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from apps.identity_app.models import PersonIdentity
from apps.core_app.serializers import BaseModelSerializer, RSUUserMinimalSerializer
from utils.gabonese_data import PROVINCES, validate_gabon_phone

class PersonIdentitySerializer(BaseModelSerializer):
    """
    Serializer principal pour PersonIdentity
    Vue complète avec calculs automatiques
    """
    age = serializers.IntegerField(source='age', read_only=True)
    full_name = serializers.CharField(source='full_name', read_only=True)
    province_info = serializers.SerializerMethodField()
    vulnerability_status = serializers.SerializerMethodField()
    data_completeness_percentage = serializers.DecimalField(
        source='data_completeness_score', max_digits=5, decimal_places=2, read_only=True
    )
    
    # Relations
    verified_by_details = RSUUserMinimalSerializer(source='verified_by', read_only=True)
    
    class Meta:
        model = PersonIdentity
        fields = [
            # Identifiants
            'rsu_id', 'nip', 'national_id',
            
            # Informations personnelles
            'first_name', 'last_name', 'maiden_name', 'full_name',
            'birth_date', 'birth_place', 'age', 'gender', 'marital_status', 'nationality',
            
            # Éducation & Profession
            'education_level', 'occupation', 'employer', 'monthly_income',
            
            # Contact
            'phone_number', 'phone_number_alt', 'email',
            
            # Localisation
            'latitude', 'longitude', 'gps_accuracy',
            'province', 'department', 'commune', 'district', 'address',
            'province_info',
            
            # Santé & Social
            'has_disability', 'disability_details', 'chronic_diseases',
            'is_household_head',
            
            # Validation
            'verification_status', 'verified_at', 'verified_by', 'verified_by_details',
            
            # RBPP
            'rbpp_synchronized', 'rbpp_last_sync', 'rbpp_sync_errors',
            
            # Métadonnées
            'data_completeness_score', 'data_completeness_percentage',
            'vulnerability_status', 'last_survey_date', 'notes',
            
            # Hérité de BaseModel
            'id', 'created_at', 'updated_at', 'is_active',
            'created_by', 'created_by_details', 'updated_by', 'updated_by_details'
        ]
        read_only_fields = [
            'rsu_id', 'age', 'full_name', 'data_completeness_score',
            'rbpp_last_sync', 'verified_at',
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
    
    def get_province_info(self, obj):
        """Informations détaillées de la province"""
        if obj.province:
            province_data = PROVINCES.get(obj.province, {})
            return {
                'code': obj.province,
                'name': province_data.get('name', obj.province),
                'capital': province_data.get('capital'),
                'type': province_data.get('type')
            }
        return None
    
    def get_vulnerability_status(self, obj):
        """Statut de vulnérabilité calculé"""
        # Logique simplifiée - sera remplacée par le service de scoring
        factors = []
        
        if obj.age and (obj.age < 5 or obj.age > 65):
            factors.append('age_vulnerable')
        if obj.has_disability:
            factors.append('disability')
        if obj.gender == 'F' and obj.is_household_head:
            factors.append('female_head_household')
        if obj.monthly_income and obj.monthly_income < 75000:
            factors.append('extreme_poverty')
        
        level = 'LOW'
        if len(factors) >= 3:
            level = 'CRITICAL'
        elif len(factors) >= 2:
            level = 'HIGH'
        elif len(factors) >= 1:
            level = 'MODERATE'
        
        return {
            'level': level,
            'factors': factors,
            'score_estimated': len(factors) * 25  # Estimation simple
        }
    
    def validate_phone_number(self, value):
        """Validation téléphone gabonais"""
        if value and not validate_gabon_phone(value):
            raise serializers.ValidationError(
                "Format téléphone invalide. Utilisez +241XXXXXXXX"
            )
        return value
    
    def validate_phone_number_alt(self, value):
        """Validation téléphone alternatif gabonais"""
        if value and not validate_gabon_phone(value):
            raise serializers.ValidationError(
                "Format téléphone invalide. Utilisez +241XXXXXXXX"
            )
        return value
    
    def validate_province(self, value):
        """Validation code province"""
        if value and value not in GABON_PROVINCES:
            raise serializers.ValidationError(
                f"Province invalide. Provinces valides: {list(PROVINCES.keys())}"
            )
        return value
    
    def validate_birth_date(self, value):
        """Validation date de naissance"""
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "La date de naissance ne peut pas être dans le futur"
            )
        
        # Âge maximum 150 ans
        age_limit = timezone.now().date().replace(year=timezone.now().year - 150)
        if value < age_limit:
            raise serializers.ValidationError(
                "Date de naissance trop ancienne"
            )
        
        return value
    
    def validate(self, attrs):
        """Validations croisées"""
        # Validation géolocalisation
        lat = attrs.get('latitude')
        lng = attrs.get('longitude')
        
        if (lat is not None and lng is None) or (lat is None and lng is not None):
            raise serializers.ValidationError(
                "Latitude et longitude doivent être fournies ensemble"
            )
        
        # Validation coordonnées Gabon (approximative)
        if lat and lng:
            if not (-4.0 <= float(lat) <= 2.5 and 8.5 <= float(lng) <= 15.0):
                raise serializers.ValidationError(
                    "Coordonnées GPS hors du territoire gabonais"
                )
        
        return attrs
    
    def update(self, instance, validated_data):
        """Mise à jour avec recalcul automatique"""
        # Sauvegarder l'instance
        instance = super().update(instance, validated_data)
        
        # Recalculer le score de complétude
        instance.calculate_completeness_score()
        instance.save(update_fields=['data_completeness_score'])
        
        return instance


class PersonIdentityCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour création d'identité
    Champs essentiels uniquement pour enquêtes terrain
    """
    
    class Meta:
        model = PersonIdentity
        fields = [
            # Essentiels
            'first_name', 'last_name', 'birth_date', 'gender',
            'phone_number', 'province', 'address',
            
            # Optionnels création rapide
            'maiden_name', 'birth_place', 'marital_status',
            'education_level', 'occupation', 'monthly_income',
            'latitude', 'longitude', 'gps_accuracy',
            'department', 'commune', 'district',
            'has_disability', 'disability_details',
            'is_household_head', 'email', 'notes'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'birth_date': {'required': True},
            'gender': {'required': True},
        }
    
    def create(self, validated_data):
        """Création avec génération automatique RSU-ID"""
        # Générer RSU-ID automatiquement dans le modèle
        person = PersonIdentity.objects.create(**validated_data)
        
        # Calculer score complétude initial
        person.calculate_completeness_score()
        person.save(update_fields=['data_completeness_score'])
        
        return person


class PersonIdentityUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour mise à jour partielle
    Tous les champs modifiables sauf identifiants
    """
    
    class Meta:
        model = PersonIdentity
        fields = [
            # Informations modifiables
            'first_name', 'last_name', 'maiden_name',
            'birth_place', 'marital_status', 'nationality',
            'education_level', 'occupation', 'employer', 'monthly_income',
            'phone_number', 'phone_number_alt', 'email',
            'latitude', 'longitude', 'gps_accuracy',
            'province', 'department', 'commune', 'district', 'address',
            'has_disability', 'disability_details', 'chronic_diseases',
            'is_household_head', 'notes'
        ]
    
    def update(self, instance, validated_data):
        """Mise à jour avec recalcul scores"""
        instance = super().update(instance, validated_data)
        instance.calculate_completeness_score()
        instance.save(update_fields=['data_completeness_score'])
        return instance


class PersonIdentityMinimalSerializer(serializers.ModelSerializer):
    """
    Serializer minimal pour listes et références
    """
    full_name = serializers.CharField(source='full_name', read_only=True)
    age = serializers.IntegerField(source='age', read_only=True)
    
    class Meta:
        model = PersonIdentity
        fields = [
            'rsu_id', 'full_name', 'age', 'gender', 
            'province', 'verification_status'
        ]
        read_only_fields = '__all__'


class PersonIdentitySearchSerializer(serializers.ModelSerializer):
    """
    Serializer pour recherche et déduplication
    Champs clés pour identification
    """
    full_name = serializers.CharField(source='full_name', read_only=True)
    age = serializers.IntegerField(source='age', read_only=True)
    similarity_score = serializers.FloatField(read_only=True)  # Ajouté dynamiquement
    
    class Meta:
        model = PersonIdentity
        fields = [
            'rsu_id', 'full_name', 'birth_date', 'age', 'gender',
            'phone_number', 'province', 'commune', 
            'verification_status', 'similarity_score'
        ]
        read_only_fields = '__all__'
