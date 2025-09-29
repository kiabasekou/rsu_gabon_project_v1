# ===================================================================
# RSU GABON - URLS SERVICES APP CORRIGÉES
# Routes API pour programmes sociaux
# ===================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SocialProgramViewSet, 
    ProgramBudgetChangeViewSet,
    SocialProgramEligibilityViewSet,
    VulnerabilityAssessmentViewSet
)

# Configuration du router
router = DefaultRouter()

# Enregistrement des ViewSets
router.register(r'social-programs', SocialProgramViewSet, basename='socialprogram')
router.register(r'budget-changes', ProgramBudgetChangeViewSet, basename='programbudgetchange')
router.register(r'eligibilities', SocialProgramEligibilityViewSet, basename='eligibility')
router.register(r'vulnerability-assessments', VulnerabilityAssessmentViewSet, basename='vulnerability')

# Configuration de l'app name pour les namespaces
app_name = 'services_app'

# URLs patterns
urlpatterns = [
    path('', include(router.urls)),
]