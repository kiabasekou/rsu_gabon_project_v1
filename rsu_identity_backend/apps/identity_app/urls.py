# =============================================================================
# FICHIER: apps/identity_app/urls.py (NOUVEAU - CRITIQUE)
# CRÉER CE FICHIER pour résoudre NoReverseMatch errors
# =============================================================================

"""
🇬🇦 RSU Gabon - Identity App URLs
Routing des APIs REST pour identités et ménages
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PersonIdentityViewSet, 
    HouseholdViewSet,
    # GeographicDataViewSet,  # À ajouter quand disponible
)

app_name = 'identity_app'

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'persons', PersonIdentityViewSet, basename='personidentity')
router.register(r'households', HouseholdViewSet, basename='household')
# router.register(r'geographic-data', GeographicDataViewSet, basename='geographicdata')

urlpatterns = [
    # APIs REST avec router
    path('', include(router.urls)),
    
    # URLs personnalisées additionnelles si nécessaire
    # path('stats/', views.identity_stats, name='identity-stats'),
]

# URLS générées automatiquement par le router:
# /persons/ -> PersonIdentityViewSet (personidentity-list, personidentity-detail)
# /households/ -> HouseholdViewSet (household-list, household-detail)
# 
# Actions personnalisées des ViewSets:
# /persons/{id}/validate_nip/ -> PersonIdentityViewSet.validate_nip
# /persons/{id}/search_duplicates/ -> PersonIdentityViewSet.search_duplicates
# /persons/vulnerability_report/ -> PersonIdentityViewSet.vulnerability_report