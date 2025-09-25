
# =============================================================================
# FICHIER: apps/identity_app/urls.py (MISE À JOUR)
# =============================================================================

"""
🇬🇦 RSU Gabon - Identity URLs Complets
Routing des APIs Identity App
"""

from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import (
    PersonIdentityViewSet, HouseholdViewSet, HouseholdMemberViewSet,
    GeographicDataViewSet, RBPPSyncViewSet
)


app_name = 'identity_app'

def identity_placeholder(request):
    """Placeholder pour Identity APIs"""
    return JsonResponse({
        'message': 'Identity APIs - En développement',
        'status': 'Coming Soon',
        'endpoints_plannés': [
            'persons/', 'households/', 'geographic-data/', 'rbpp-sync/'
        ]
    })

# Router pour futurs ViewSets
router = DefaultRouter()
router = DefaultRouter()
router.register(r'persons', PersonIdentityViewSet, basename='persons')
router.register(r'households', HouseholdViewSet, basename='households')
router.register(r'household-members', HouseholdMemberViewSet, basename='household-members')
router.register(r'geographic-data', GeographicDataViewSet, basename='geographic-data')
router.register(r'rbpp-sync', RBPPSyncViewSet, basename='rbpp-sync')



urlpatterns = [
    path('', include(router.urls)),
    # Placeholder temporaire
    path('status/', identity_placeholder, name='status'),
]