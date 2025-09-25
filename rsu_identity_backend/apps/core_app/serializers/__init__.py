# 🇬🇦 RSU GABON - CORE APP SERIALIZERS
# Standards Top 1% - Django REST Framework

# =============================================================================
# FICHIER: apps/core_app/serializers/__init__.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Core Serializers
Sérialisation des modèles de base du système
"""
from .user_serializers import RSUUserSerializer, RSUUserCreateSerializer, RSUUserUpdateSerializer, RSUUserMinimalSerializer
from .audit_serializers import AuditLogSerializer

from .base_serializers import BaseModelSerializer


__all__ = [
    'RSUUserSerializer', 'RSUUserCreateSerializer', 'RSUUserUpdateSerializer', RSUUserMinimalSerializer,
    'AuditLogSerializer', 'BaseModelSerializer'
]

