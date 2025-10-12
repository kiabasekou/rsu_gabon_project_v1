from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.analytics_views import AnalyticsViewSet
from .views.vulnerability_views import VulnerabilityAssessmentViewSet
from .views.eligibility_views import EligibilityViewSet
from .views.program_views import (
    SocialProgramViewSet,
    ProgramBudgetChangeViewSet,
    SocialProgramEligibilityViewSet
)

router = DefaultRouter()
router.register(r'social-programs', SocialProgramViewSet, basename='socialprogram')
router.register(r'budget-changes', ProgramBudgetChangeViewSet, basename='programbudgetchange')
router.register(r'eligibility', SocialProgramEligibilityViewSet, basename='eligibility')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')
router.register(r'vulnerability-assessments', VulnerabilityAssessmentViewSet, basename='vulnerability-assessment')

app_name = 'services_app'

urlpatterns = [
    path('', include(router.urls)),
]