
# =============================================================================
# FICHIER: apps/core_app/views/permissions.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Permissions Personnalisées
Classes de permissions pour sécurité gouvernementale
"""
from rest_framework import permissions

class IsAdminOrSupervisor(permissions.BasePermission):
    """
    Permission pour administrateurs et superviseurs uniquement
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_staff or 
             request.user.user_type in ['ADMIN', 'SUPERVISOR'])
        )

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission pour propriétaire de l'objet ou administrateur
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Écriture pour propriétaire ou admin
        return (
            obj == request.user or
            request.user.is_staff or
            request.user.user_type == 'ADMIN'
        )

class IsAdminOrAuditor(permissions.BasePermission):
    """
    Permission pour administrateurs et auditeurs
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_staff or 
             request.user.user_type in ['ADMIN', 'AUDITOR'])
        )

class IsSurveyorOrSupervisor(permissions.BasePermission):
    """
    Permission pour enquêteurs et leurs superviseurs
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.user_type in ['SURVEYOR', 'SUPERVISOR', 'ADMIN']
        )

class CanAccessProvince(permissions.BasePermission):
    """
    Permission basée sur les provinces assignées
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.user_type == 'ADMIN':
            return True
        
        # Vérifier si l'utilisateur a accès à la province de l'objet
        if hasattr(obj, 'province') and obj.province:
            return request.user.can_access_province(obj.province)
        
        return True