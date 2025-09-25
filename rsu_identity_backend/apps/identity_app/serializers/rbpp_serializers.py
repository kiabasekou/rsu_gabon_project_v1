

# 🇬🇦 RSU GABON - IDENTITY APP SERIALIZERS
# Standards Top 1% - Sérialisation des identités et ménages

# =============================================================================
# FICHIER: apps/identity_app/serializers/rbpp_serializers.py
# =============================================================================

"""
🇬🇦 RSU Gabon - RBPP Serializers
Sérialisation des synchronisations RBPP
"""
from rest_framework import serializers
from apps.identity_app.models import RBPPSync
from apps.core_app.serializers import BaseModelSerializer
from .person_serializers import PersonIdentityMinimalSerializer

class RBPPSyncSerializer(BaseModelSerializer):
    """
    Serializer pour synchronisations RBPP
    Lecture seule - créé automatiquement par le système
    """
    person_details = PersonIdentityMinimalSerializer(source='person', read_only=True)
    sync_type_display = serializers.CharField(source='get_sync_type_display', read_only=True)
    sync_status_display = serializers.CharField(source='get_sync_status_display', read_only=True)
    duration_display = serializers.SerializerMethodField()
    can_retry = serializers.BooleanField(source='can_retry', read_only=True)
    
    class Meta:
        model = RBPPSync
        fields = [
            'id', 'person', 'person_details',
            'sync_type', 'sync_type_display', 'sync_status', 'sync_status_display',
            'rbpp_request_id', 'nip_requested', 'nip_returned',
            'rbpp_response_data', 'biometric_match_score', 'data_discrepancies',
            'error_code', 'error_message',
            'started_at', 'completed_at', 'duration_seconds', 'duration_display',
            'retry_count', 'max_retries', 'next_retry_at', 'can_retry',
            'created_at', 'updated_at'
        ]
        read_only_fields = '__all__'  # Tout en lecture seule
    
    def get_duration_display(self, obj):
        """Affichage durée formaté"""
        if obj.duration_seconds:
            if obj.duration_seconds < 60:
                return f"{obj.duration_seconds}s"
            else:
                minutes = obj.duration_seconds // 60
                seconds = obj.duration_seconds % 60
                return f"{minutes}m {seconds}s"
        return None