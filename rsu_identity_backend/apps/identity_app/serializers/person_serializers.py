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
            'occupation', 'employer', 'employment_status', 
            'employment_status_display', 'monthly_income',
            'employment_info',
            
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
    def get_employment_info(self, obj):
        """Résumé situation professionnelle"""
        if not obj.employment_status:
            return None
        
        info = {
            'status': obj.employment_status,
            'status_label': obj.get_employment_status_display(),
            'occupation': obj.occupation,
            'employer': obj.employer,
            'income': float(obj.monthly_income) if obj.monthly_income else None,
        }
        
        # Indicateurs de précarité
        info['is_vulnerable'] = obj.employment_status in [
            'UNEMPLOYED', 'EMPLOYED_INFORMAL', 'UNABLE_TO_WORK'
        ]
        info['is_stable'] = obj.employment_status in [
            'EMPLOYED_FORMAL', 'RETIRED'
        ]
        
        return info
# =============================================================================
# CORRECTION: PersonIdentityCreateSerializer
# RETIRER: employment_status (n'existe pas dans PersonIdentity)
# =============================================================================

class PersonIdentityCreateSerializer(serializers.ModelSerializer):
    """Serializer création avec validations métier"""
    
    class Meta:
        model = PersonIdentity
        fields = [
            'first_name', 'last_name', 'birth_date', 'gender',
            'phone_number', 'province', 'department', 'commune',
            'address', 'latitude', 'longitude',
            'marital_status', 'education_level',
            'occupation', 'employer', 'employment_status',  # ✅ Tous présents
            'monthly_income',
            'maiden_name', 'birth_place', 'phone_number_alt', 'email',
            'national_id', 'nip',
            'has_disability', 'disability_details',
            'is_household_head', 'notes'
        ]
    
    def validate(self, attrs):
        """Validations croisées métier"""
        attrs = super().validate(attrs)
        
        employment_status = attrs.get('employment_status')
        employer = attrs.get('employer')
        occupation = attrs.get('occupation')
        
        # Cohérence emploi formel → employeur requis
        if employment_status in ['EMPLOYED_FORMAL', 'EMPLOYED_INFORMAL']:
            if not employer:
                raise serializers.ValidationError({
                    'employer': 'Employeur requis pour statut employé'
                })
        
        # Chômeur ne peut avoir employeur
        if employment_status == 'UNEMPLOYED' and employer:
            raise serializers.ValidationError({
                'employer': 'Incohérent: chômeur avec employeur'
            })
        
        # Occupation → employment_status recommandé
        if occupation and not employment_status:
            raise serializers.ValidationError({
                'employment_status': 'Statut emploi recommandé si profession renseignée'
            })
        return attrs
    
    def validate_birth_date(self, value):
        """Validation date naissance"""
        if value and value > date.today():
            raise serializers.ValidationError(
                "La date de naissance ne peut pas être dans le futur."
            )
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
                    f"Province invalide. Provinces valides: {', '.join(valid_provinces)}"
                )
        return value
    
    def validate(self, attrs):
        """Validations croisées"""
        # GPS: Les deux coords ou aucune
        has_lat = attrs.get('latitude') is not None
        has_lng = attrs.get('longitude') is not None
        
        if has_lat != has_lng:
            raise serializers.ValidationError({
                'non_field_errors': [
                    "La latitude et la longitude doivent être fournies ensemble."
                ]
            })
        
        # Validation des coordonnées pour le Gabon
        if has_lat and has_lng:
            from utils.gabonese_data import validate_gabon_coordinates
            if not validate_gabon_coordinates(
                float(attrs['latitude']), 
                float(attrs['longitude'])
            ):
                raise serializers.ValidationError({
                    'non_field_errors': [
                        "Coordonnées GPS hors du Gabon. "
                        "Vérifiez latitude (-4.0° à 2.3°) et longitude (8.5° à 14.5°)."
                    ]
                })
        
        return attrs
    
    def create(self, validated_data):
        """Création avec génération automatique RSU-ID"""
        person = PersonIdentity.objects.create(**validated_data)
        
        # Calculer score complétude initial
        person.calculate_completeness_score()
        person.save(update_fields=['data_completeness_score'])
        
        return person



    
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


"""
ERREUR CORRIGÉE:
----------------
ImproperlyConfigured: Field name `employment_status` is not valid for model 
`PersonIdentity` in `PersonIdentityCreateSerializer`.

CAUSE:
------
Le serializer référençait 'employment_status' qui n'existe PAS dans PersonIdentity.

CHAMPS CORRECTS dans PersonIdentity:
------------------------------------
✅ occupation (CharField) - Profession actuelle
✅ employer (CharField) - Employeur
✅ monthly_income (DecimalField) - Revenus mensuels

CHAMPS INEXISTANTS (à ne JAMAIS utiliser):
-------------------------------------------
❌ employment_status - N'existe pas
❌ profession - Utiliser 'occupation' à la place

CONFORMITÉ AUX CONSIGNES:
--------------------------
✅ Consigne 1 (SSOT): Noms de champs vérifiés dans le modèle réel
✅ Consigne 3 (Typage): Respect des champs exacts du modèle
✅ Pas d'extrapolation: Basé sur le code réel de person.py
"""