# ===================================================================
# RSU GABON - URLS SERVICES APP CORRIGÉES
# Routes API pour programmes sociaux
# ===================================================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.analytics_views import AnalyticsViewSet
from .views.vulnerability_views import VulnerabilityAssessmentViewSet
from .views.eligibility_views import EligibilityViewSet

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
router.register(r'analytics', AnalyticsViewSet, basename='analytics')
router.register(r'vulnerability-assessments', VulnerabilityAssessmentViewSet, basename='vulnerability-assessment')
router.register(r'eligibility', EligibilityViewSet, basename='eligibility')


# Configuration de l'app name pour les namespaces
app_name = 'services_app'

# URLs patterns
urlpatterns = [
    path('', include(router.urls)),
]

"""
🇬🇦 RSU Gabon - Services App URLs
Fichier: rsu_identity_backend/apps/services_app/urls.py
"""
