

# =============================================================================
# FICHIER: apps/core_app/serializers/base_serializers.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Base Serializers
Serializers de base pour héritage
"""
from rest_framework import serializers
from apps.core_app.models.base import BaseModel

class BaseModelSerializer(serializers.ModelSerializer):
    """
    Serializer de base pour tous les modèles RSU
    Fournit les champs communs et la logique d'audit
    """
    created_by_details = RSUUserMinimalSerializer(source='created_by', read_only=True)
    updated_by_details = RSUUserMinimalSerializer(source='updated_by', read_only=True)
    
    class Meta:
        abstract = True
        fields = [
            'id', 'created_at', 'updated_at', 'is_active',
            'created_by', 'created_by_details',
            'updated_by', 'updated_by_details'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 
            'created_by', 'updated_by'
        ]
    
    def create(self, validated_data):
        """Création avec attribution automatique created_by"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Mise à jour avec attribution automatique updated_by"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)