
# =============================================================================
# FICHIER: apps/core_app/serializers/user_serializers.py
# =============================================================================

"""
🇬🇦 RSU Gabon - User Serializers
Sérialisation des utilisateurs RSU avec sécurité gouvernementale
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from apps.core_app.models import RSUUser
from utils.gabonese_data import PROVINCES

class RSUUserSerializer(serializers.ModelSerializer):
    """
    Serializer principal pour RSUUser
    Lecture complète avec informations sensibles filtrées
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    provinces_display = serializers.SerializerMethodField()
    is_surveyor = serializers.BooleanField(source='is_surveyor', read_only=True)
    is_supervisor = serializers.BooleanField(source='is_supervisor', read_only=True)
    
    class Meta:
        model = RSUUser
        fields = [
            'id', 'username', 'employee_id', 'full_name',
            'first_name', 'last_name', 'email', 'phone_number',
            'user_type', 'user_type_display', 'department',
            'assigned_provinces', 'provinces_display',
            'is_active', 'is_staff', 'is_surveyor', 'is_supervisor',
            'date_joined', 'last_login', 'last_activity',
            'created_at', 'updated_at'
        ]
        # CORRECTION: Était une chaîne, doit être une liste/tuple
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    
    def get_provinces_display(self, obj):
        """Affichage lisible des provinces assignées"""
        return obj.get_provinces_display()
    
    def validate_phone_number(self, value):
        """Validation téléphone gabonais"""
        if value:
            from utils.gabonese_data import validate_gabon_phone
            if not validate_gabon_phone(value):
                raise serializers.ValidationError(
                    "Format téléphone invalide. Utilisez +241XXXXXXXX"
                )
        return value
    
    def validate_assigned_provinces(self, value):
        """Validation des provinces assignées"""
        if value:
            valid_provinces = set(PROVINCES.keys())
            invalid_provinces = set(value) - valid_provinces
            if invalid_provinces:
                raise serializers.ValidationError(
                    f"Provinces invalides: {', '.join(invalid_provinces)}"
                )
        return value
    
    def to_representation(self, instance):
        """Personnalisation de la sortie selon les permissions"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Masquer informations sensibles selon le niveau d'accès
        if request and hasattr(request, 'user'):
            current_user = request.user
            
            # Seuls admins et superviseurs voient certaines infos
            if not (current_user.is_supervisor() or current_user.is_staff):
                sensitive_fields = ['employee_id', 'phone_number', 'last_activity']
                for field in sensitive_fields:
                    data.pop(field, None)
                    
            # L'utilisateur ne voit que ses propres infos complètes
            if current_user != instance and not current_user.is_staff:
                data.pop('email', None)
                
        return data


class RSUUserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour création d'utilisateur
    Validation renforcée pour sécurité gouvernementale
    """
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = RSUUser
        fields = [
            'username', 'employee_id', 'first_name', 'last_name',
            'email', 'phone_number', 'password', 'password_confirm',
            'user_type', 'department', 'assigned_provinces'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'employee_id': {'required': True},
        }
    
    def validate(self, attrs):
        """Validation croisée des champs"""
        # Validation mot de passe
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                "Les mots de passe ne correspondent pas"
            )
        
        # Validation mot de passe Django
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})
        
        return attrs
    
    def validate_employee_id(self, value):
        """Validation unicité employee_id"""
        if RSUUser.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError(
                "Cet ID employé existe déjà"
            )
        return value
    
    def validate_username(self, value):
        """Validation format username"""
        if len(value) < 3:
            raise serializers.ValidationError(
                "Le nom d'utilisateur doit contenir au moins 3 caractères"
            )
        return value
    
    def create(self, validated_data):
        """Création utilisateur avec hash du mot de passe"""
        validated_data.pop('password_confirm')  # Retirer confirmation
        password = validated_data.pop('password')
        
        # Création utilisateur
        user = RSUUser.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user


class RSUUserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour mise à jour utilisateur
    Champs modifiables limités selon les permissions
    """
    
    class Meta:
        model = RSUUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'department', 'assigned_provinces', 'is_active'
        ]
    
    def validate_phone_number(self, value):
        """Validation téléphone gabonais"""
        if value:
            from utils.gabonese_data import validate_gabon_phone
            if not validate_gabon_phone(value):
                raise serializers.ValidationError(
                    "Format téléphone invalide. Utilisez +241XXXXXXXX"
                )
        return value
    
    def update(self, instance, validated_data):
        """Mise à jour avec audit automatique"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Log des modifications pour audit
            changes = {}
            for field, new_value in validated_data.items():
                old_value = getattr(instance, field)
                if old_value != new_value:
                    changes[field] = {'old': old_value, 'new': new_value}
            
            # Sauvegarder les modifications
            instance = super().update(instance, validated_data)
            
            # Créer log d'audit si des changements
            if changes:
                from apps.core_app.models import AuditLog
                AuditLog.log_action(
                    user=request.user,
                    action='UPDATE',
                    description=f"Modification utilisateur {instance.username}",
                    obj=instance,
                    changes=changes,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
        
        return instance


class RSUUserMinimalSerializer(serializers.ModelSerializer):
    """
    Serializer minimal pour références rapides
    Utilisé dans les relations ForeignKey
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = RSUUser
        fields = ['id', 'username', 'full_name', 'user_type']
        read_only_fields = ['id', 'username', 'full_name', 'user_type']
