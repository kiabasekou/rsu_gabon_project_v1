# =============================================================================
# FICHIER: apps/identity_app/urls.py - CORRECTION CRITIQUE STATUS 500
# Ce fichier MANQUAIT et causait NoReverseMatch dans tous les tests
# =============================================================================

"""
🇬🇦 RSU Gabon - Identity App URLs
Routing des APIs REST pour identités et ménages
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# IMPORTS CORRECTS selon structure réelle des views
from .views.person_views import PersonIdentityViewSet
from .views.household_views import HouseholdViewSet, HouseholdMemberViewSet

# Imports optionnels (commentés si non disponibles)
try:
    from .views.geographic_views import GeographicDataViewSet
    GEOGRAPHIC_AVAILABLE = True
except ImportError:
    GEOGRAPHIC_AVAILABLE = False

try:
    from .views.rbpp_views import RBPPSyncViewSet  
    RBPP_AVAILABLE = True
except ImportError:
    RBPP_AVAILABLE = False

app_name = 'identity_app'

# Router pour les ViewSets
router = DefaultRouter()

# ViewSets OBLIGATOIRES (doivent exister)
router.register(r'persons', PersonIdentityViewSet, basename='personidentity')
router.register(r'households', HouseholdViewSet, basename='household')
router.register(r'household-members', HouseholdMemberViewSet, basename='householdmember')

# ViewSets OPTIONNELS (ajoutés seulement si disponibles)
if GEOGRAPHIC_AVAILABLE:
    router.register(r'geographic-data', GeographicDataViewSet, basename='geographicdata')

if RBPP_AVAILABLE:
    router.register(r'rbpp-sync', RBPPSyncViewSet, basename='rbppsync')

urlpatterns = [
    # APIs REST avec router
    path('', include(router.urls)),
    
    # URLs personnalisées additionnelles si nécessaire
    # path('stats/', views.identity_stats, name='identity-stats'),
]

# ============================================================================= 
# URLS GÉNÉRÉES AUTOMATIQUEMENT PAR LE ROUTER:
# =============================================================================
# 
# PERSONS API:
# GET    /api/v1/identity/persons/                     → personidentity-list
# POST   /api/v1/identity/persons/                     → personidentity-list  
# GET    /api/v1/identity/persons/{id}/                → personidentity-detail
# PUT    /api/v1/identity/persons/{id}/                → personidentity-detail
# DELETE /api/v1/identity/persons/{id}/                → personidentity-detail
# 
# HOUSEHOLDS API:
# GET    /api/v1/identity/households/                  → household-list
# POST   /api/v1/identity/households/                  → household-list
# GET    /api/v1/identity/households/{id}/             → household-detail
# PUT    /api/v1/identity/households/{id}/             → household-detail
# DELETE /api/v1/identity/households/{id}/             → household-detail
#
# ACTIONS PERSONNALISÉES (si définies dans ViewSets):
# POST   /api/v1/identity/persons/{id}/validate_nip/           → personidentity-validate-nip
# POST   /api/v1/identity/persons/{id}/search_duplicates/      → personidentity-search-duplicates  
# GET    /api/v1/identity/persons/vulnerability_report/        → personidentity-vulnerability-report
# GET    /api/v1/identity/households/{id}/add_member/          → household-add-member
# 
# =============================================================================