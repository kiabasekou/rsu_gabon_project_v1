# ===================================================================
# RSU GABON - INTÉGRATION SERVICES APP DANS ARCHITECTURE EXISTANTE
# Standards Top 1% - Continuité avec Core + Identity Apps
# ===================================================================

# apps/services_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VulnerabilityAssessmentViewSet, SocialProgramEligibilityViewSet

router = DefaultRouter()
router.register(r'vulnerability-assessments', VulnerabilityAssessmentViewSet)
router.register(r'program-eligibilities', SocialProgramEligibilityViewSet)

urlpatterns = router.urls
