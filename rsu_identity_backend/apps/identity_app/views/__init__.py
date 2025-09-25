# 🇬🇦 RSU GABON - IDENTITY APP VIEWSETS
# Standards Top 1% - APIs REST pour identités et ménages

# =============================================================================
# FICHIER: apps/identity_app/views/__init__.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Identity Views
ViewSets pour les APIs d'identité et géolocalisation
"""
from .person_views import PersonIdentityViewSet
from .household_views import HouseholdViewSet, HouseholdMemberViewSet
from .geographic_views import GeographicDataViewSet
from .rbpp_views import RBPPSyncViewSet

__all__ = [
    'PersonIdentityViewSet', 'HouseholdViewSet', 'HouseholdMemberViewSet',
    'GeographicDataViewSet', 'RBPPSyncViewSet'
]
