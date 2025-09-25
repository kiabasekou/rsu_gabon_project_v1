
# =============================================================================
# FICHIER: apps/identity_app/views/rbpp_views.py
# =============================================================================

"""
🇬🇦 RSU Gabon - RBPP ViewSets
APIs pour synchronisation registre biométrique
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.identity_app.models import RBPPSync
from apps.identity_app.serializers import RBPPSyncSerializer
from apps.core_app.views.permissions import IsAdminOrSupervisor

class RBPPSyncViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour historique synchronisations RBPP
    Lecture seule pour audit et monitoring
    """
    queryset = RBPPSync.objects.all()
    serializer_class = RBPPSyncSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    filterset_fields = ['sync_type', 'sync_status', 'person']
    ordering_fields = ['created_at', 'duration_seconds']
    ordering = ['-created_at']
