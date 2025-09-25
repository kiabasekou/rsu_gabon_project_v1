
# =============================================================================
# CORRECTION 3: apps/identity_app/urls.py - Placeholder fonctionnel
# =============================================================================

from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter

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
# À activer plus tard:
# router.register(r'persons', PersonIdentityViewSet, basename='persons')

urlpatterns = [
    path('', include(router.urls)),
    # Placeholder temporaire
    path('status/', identity_placeholder, name='status'),
]