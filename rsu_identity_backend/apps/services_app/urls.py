# ===================================================================
# RSU GABON - INTÉGRATION SERVICES APP DANS ARCHITECTURE EXISTANTE
# Standards Top 1% - Continuité avec Core + Identity Apps
# ===================================================================

# apps/services_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import eligibility_views, VulnerabilityAssessmentViewSet, SocialProgramEligibilityViewSet, SocialProgramViewSet, ProgramEligibilityViewSet
router = DefaultRouter()
router.register(r'vulnerability-assessments', VulnerabilityAssessmentViewSet)
router.register(r'program-eligibilities', SocialProgramEligibilityViewSet)
router.register(r'social-programs', SocialProgramViewSet)
router.register(r'program-eligibility', ProgramEligibilityViewSet)

urlpatterns = router.urls


# Fichier : rsu_identity_backend/apps/services_app/urls.py


urlpatterns = router.urls

