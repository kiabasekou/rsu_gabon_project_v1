# ✅ FICHIER COMPLET
from .vulnerability_views import VulnerabilityAssessmentViewSet
from .eligibility_views import EligibilityViewSet  
from .analytics_views import AnalyticsViewSet

# Si ces ViewSets existent dans models.py ou ailleurs
from ..models import (
    SocialProgram,
    ProgramBudgetChange,
    SocialProgramEligibility
)

__all__ = [
    'VulnerabilityAssessmentViewSet',
    'EligibilityViewSet',
    'AnalyticsViewSet',
    'SocialProgramViewSet',      # À créer si besoin
    'ProgramBudgetChangeViewSet', # À créer si besoin
    'SocialProgramEligibilityViewSet' # À créer si besoin
]