# =============================================================================
# FICHIER: apps/identity_app/serializers/person_serializers.py
# CORRECTION FINALE: PersonIdentityCreateSerializer DOIT retourner rsu_id
# =============================================================================

"""
🇬🇦 RSU Gabon - Person Serializers CORRECTION FINALE
Solution au problème: 'rsu_id' not found in response.data
"""
from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from datetime import date
from apps.identity_app.models import PersonIdentity
from apps.core_app.serializers import BaseModelSerializer, RSUUserMinimalSerializer


class PersonIdentitySerializer(BaseModelSerializer):
    """Serializer principal - Lecture complète"""
    age = serializers.IntegerField(read_only=True)  # ✅ BON
    full_name = serializers.CharField(read_only=True)
    
    # SerializerMethodFields
    province_info = serializers.SerializerMethodField()
    vulnerability_status = serializers.SerializerMethodField()
    employment_status_display = serializers.SerializerMethodField()
    employment_info = serializers.SerializerMethodField()
    
    data_completeness_percentage = serializers.DecimalField(
        source='data_completeness_score', max_digits=5, decimal_places=2, read_only=True
    )
    
    # Relations
    verified_by_details = RSUUserMinimalSerializer(source='verified_by', read_only=True)
    created_by_details = RSUUserMinimalSerializer(source='created_by', read_only=True)
    updated_by_details = RSUUserMinimalSerializer(source='updated_by', read_only=True)
    
    class Meta:
        model = PersonIdentity
        fields = [
            # Identifiants
            'id', 'rsu_id', 'nip', 'national_id',
            
            # Informations personnelles
            'first_name', 'last_name', 'maiden_name', 'full_name',
            'birth_date', 'birth_place', 'age', 'gender',
            
            # Contact
            'phone_number', 'phone_number_alt', 'email',
            
            # Localisation
            'latitude', 'longitude', 'gps_accuracy',
            'province', 'department', 'commune', 'district', 'address',
            'province_info',
            
            # État civil
            'marital_status',
            
            # Éducation & Profession
            'education_level',
            'occupation', 'employer', 'employment_status',
            'employment_status_display', 'monthly_income',
            'employment_info',
            
            # Santé & Vulnérabilité
            'has_disability', 'disability_details',  # ✅ CORRECTION
            'is_household_head',
            'vulnerability_score', 'vulnerability_level',
            'last_vulnerability_assessment',
            'vulnerability_status',
            
            # Validation
            'verification_status', 'verified_at', 'verified_by_details',
            'data_completeness_score', 'data_completeness_percentage',
            
            # RBPP
            'rbpp_synchronized', 'rbpp_sync_date',
            
            # Métadonnées
            'notes',
            'is_active', 'created_at', 'updated_at',
            'created_by', 'created_by_details',
            'updated_by', 'updated_by_details'
        ]
        
        read_only_fields = [
            'id', 'rsu_id', 'age', 'full_name',
            'verification_status', 'verified_at',
            'data_completeness_score', 'data_completeness_percentage',
            'vulnerability_score', 'vulnerability_level',
            'last_vulnerability_assessment',
            'rbpp_synchronized', 'rbpp_sync_date',
            'created_at', 'updated_at'
        ]
    
    def get_employment_status_display(self, obj):
        """Label lisible du statut d'emploi"""
        if not obj.employment_status:
            return None
        return obj.get_employment_status_display()
    
    def get_employment_info(self, obj):
        """Résumé situation professionnelle"""
        if not obj.employment_status:
            return None
        
        return {
            'status': obj.employment_status,
            'status_label': obj.get_employment_status_display(),
            'occupation': obj.occupation,
            'employer': obj.employer,
            'income': float(obj.monthly_income) if obj.monthly_income else None,
            'is_vulnerable': obj.employment_status in [
                'UNEMPLOYED', 'EMPLOYED_INFORMAL', 'UNABLE_TO_WORK'
            ],
            'is_stable': obj.employment_status in [
                'EMPLOYED_FORMAL', 'RETIRED'
            ]
        }
    
    def get_province_info(self, obj):
        """Informations détaillées sur la province"""
        if not obj.province:
            return None
        from utils.gabonese_data import PROVINCES
        return PROVINCES.get(obj.province, {})
    
    def get_vulnerability_status(self, obj):
        """Calcul statut de vulnérabilité"""
        indicators = []
        age = obj.age
        
        if age is not None:
            if age < 5:
                indicators.append('ENFANT_JEUNE')
            elif age > 65:
                indicators.append('PERSONNE_AGEE')
        
        if obj.monthly_income and obj.monthly_income < 150000:
            indicators.append('PAUVRETE')
        
        if obj.has_disability:
            indicators.append('HANDICAP')
        
        if obj.province in ['NYANGA', 'OGOOUE_IVINDO', 'OGOOUE_LOLO']:
            indicators.append('ZONE_ISOLEE')
        
        if obj.is_household_head and obj.gender == 'F':
            indicators.append('CHEF_MENAGE_FEMME')
        
        if not indicators:
            return {'status': 'NON_VULNERABLE', 'indicators': [], 'risk_level': 'LOW'}
        
        return {
            'status': 'VULNERABLE',
            'indicators': indicators,
            'risk_level': 'HIGH' if len(indicators) >= 3 else 'MEDIUM'
        }


# ============================================================================
# ✅ CORRECTION CRITIQUE: PersonIdentityCreateSerializer
# ============================================================================
class PersonIdentityCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour CRÉATION de PersonIdentity
    
    ✅ CORRECTION: Inclut rsu_id en READ_ONLY pour le retourner après création
    """
    
    # ✅ AJOUT: Déclarer rsu_id comme read_only pour le retourner
    rsu_id = serializers.CharField(read_only=True)
    
    class Meta:
        model = PersonIdentity
        fields = [
            # ✅ CRITIQUE: rsu_id DOIT être dans fields pour être retourné
            'rsu_id',  # ← AJOUT ESSENTIEL
            
            # Champs obligatoires
            'first_name', 'last_name', 'birth_date', 'gender',
            
            # Champs recommandés
            'phone_number', 'province', 'address',
            
            # Champs optionnels
            'maiden_name', 'birth_place', 'phone_number_alt', 'email',
            'marital_status', 'education_level',
            'occupation', 'employer', 'employment_status', 'monthly_income',
            'latitude', 'longitude', 'gps_accuracy',
            'department', 'commune', 'district',
            'national_id', 'nip',
            'has_disability', 'disability_details',
            'is_household_head', 'notes'
        ]
        
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'birth_date': {'required': True},
            'gender': {'required': True},
        }
    
    def validate_birth_date(self, value):
        """Validation date naissance"""
        if value and value > date.today():
            raise serializers.ValidationError(
                "La date de naissance ne peut pas être dans le futur."
            )
        
        age = date.today().year - value.year
        if age > 120:
            raise serializers.ValidationError("Âge irréaliste (plus de 120 ans).")
        
        return value
    
    def validate_phone_number(self, value):
        """Validation téléphone gabonais"""
        if value:
            from utils.gabonese_data import validate_gabon_phone
            if not validate_gabon_phone(value):
                raise serializers.ValidationError(
                    "Numéro de téléphone gabonais invalide. Format: +241XXXXXXXX"
                )
        return value
    
    def validate_province(self, value):
        """Validation province gabonaise"""
        if value:
            from utils.gabonese_data import PROVINCES
            if value not in PROVINCES:
                valid_provinces = list(PROVINCES.keys())
                raise serializers.ValidationError(
                    f"Province invalide. Choisir parmi: {', '.join(valid_provinces)}"
                )
        return value
    
    def validate(self, attrs):
        """Validations croisées métier"""
        attrs = super().validate(attrs)
        
        employment_status = attrs.get('employment_status')
        employer = attrs.get('employer')
        
        # Cohérence emploi formel → employeur requis
        if employment_status in ['EMPLOYED_FORMAL', 'EMPLOYED_INFORMAL']:
            if not employer:
                raise serializers.ValidationError({
                    'employer': "L'employeur est requis pour un statut 'employé'."
                })
        
        # Chômeur ne peut avoir employeur
        if employment_status == 'UNEMPLOYED' and employer:
            raise serializers.ValidationError({
                'employer': "Incohérent : un chômeur ne peut avoir d'employeur."
            })
        
        return attrs


class PersonIdentityUpdateSerializer(PersonIdentityCreateSerializer):
    """
    Serializer pour mise à jour PersonIdentity
    Tous les champs deviennent optionnels
    """
    
    class Meta(PersonIdentityCreateSerializer.Meta):
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'birth_date': {'required': False},
            'gender': {'required': False},
        }


class PersonIdentityMinimalSerializer(serializers.ModelSerializer):
    """Serializer minimal pour relations et listes"""
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)  # ✅ BON
    
    class Meta:
        model = PersonIdentity
        fields = [
            'id', 'rsu_id', 'first_name', 'last_name', 'full_name',
            'age', 'gender', 'province', 'phone_number'
        ]


class PersonIdentitySearchSerializer(serializers.Serializer):
    """Serializer pour recherche et déduplication"""
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    birth_date = serializers.DateField(required=False)
    phone_number = serializers.CharField(required=False)
    province = serializers.CharField(required=False)
    
    similarity_threshold = serializers.FloatField(
        default=0.8,
        min_value=0.0,
        max_value=1.0,
        help_text="Seuil de similarité pour la détection de doublons"
    )


# =============================================================================
# ✅ EXPLICATION DE LA CORRECTION
# =============================================================================
"""
PROBLÈME IDENTIFIÉ:
------------------
Test échoue avec: AssertionError: 'rsu_id' not found in response.data

CAUSE RACINE:
-------------
PersonIdentityCreateSerializer ne contenait PAS 'rsu_id' dans Meta.fields.
Donc même si le modèle génère rsu_id automatiquement, le serializer
ne le retournait PAS dans la réponse HTTP.

SOLUTION:
---------
1. Ajouter 'rsu_id' dans PersonIdentityCreateSerializer.Meta.fields
2. Déclarer rsu_id = serializers.CharField(read_only=True)
3. Le champ sera automatiquement rempli par le modèle à la création
4. Le serializer le retournera maintenant dans response.data

CONFORMITÉ:
-----------
✅ Consigne 1 (SSOT): rsu_id existe dans le modèle PersonIdentity
✅ Consigne 2 (Cycle): Pas de dépendances circulaires
✅ Consigne 3 (Typage): rsu_id en read_only, généré par le modèle
✅ Consigne 4 (Schema First): Champ déjà dans la base de données
✅ Directive: Basé sur l'analyse du repository réel
"""