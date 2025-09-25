
# =============================================================================
# FICHIER: apps/core_app/serializers/audit_serializers.py  
# =============================================================================

"""
🇬🇦 RSU Gabon - Audit Serializers
Sérialisation des logs d'audit pour gouvernance
"""
from rest_framework import serializers
from apps.core_app.models import AuditLog
from .user_serializers import RSUUserMinimalSerializer

class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer pour les logs d'audit
    Lecture seule pour préserver l'intégrité
    """
    user_details = RSUUserMinimalSerializer(source='user', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    object_repr = serializers.SerializerMethodField()
    location_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'created_at', 'user', 'user_details',
            'action', 'action_display', 'severity', 'severity_display',
            'description', 'content_type', 'object_id', 'object_repr',
            'changes', 'ip_address', 'user_agent',
            'location_lat', 'location_lng', 'location_display'
        ]
        read_only_fields = '__all__'  # Aucun champ modifiable
    
    def get_object_repr(self, obj):
        """Représentation de l'objet concerné"""
        if obj.content_object:
            return str(obj.content_object)[:100]
        return None
    
    def get_location_display(self, obj):
        """Affichage de la localisation si disponible"""
        if obj.location_lat and obj.location_lng:
            return f"{obj.location_lat:.4f}, {obj.location_lng:.4f}"
        return None
    
    def to_representation(self, instance):
        """Filtrage selon les permissions utilisateur"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):
            current_user = request.user
            
            # Seuls les admins et auditeurs voient tout
            if not (current_user.user_type in ['ADMIN', 'AUDITOR'] or current_user.is_staff):
                # Autres utilisateurs : infos limitées
                sensitive_fields = ['user_agent', 'session_key', 'changes']
                for field in sensitive_fields:
                    data.pop(field, None)
                
                # Enquêteurs ne voient que leurs propres actions
                if current_user.user_type == 'SURVEYOR' and instance.user != current_user:
                    return None  # Sera filtré côté ViewSet
        
        return data
