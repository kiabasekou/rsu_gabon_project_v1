from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import (
    SocialProgram, 
    ProgramBudgetChange,
    SocialProgramEligibility  # ✅ AJOUTER CETTE LIGNE
)
from ..serializers import (
    SocialProgramSerializer, 
    ProgramBudgetChangeSerializer,
    SocialProgramEligibilitySerializer  # ✅ AJOUTER CETTE LIGNE
)

class SocialProgramViewSet(viewsets.ModelViewSet):
    queryset = SocialProgram.objects.all()
    serializer_class = SocialProgramSerializer
    permission_classes = [IsAuthenticated]

class ProgramBudgetChangeViewSet(viewsets.ModelViewSet):
    queryset = ProgramBudgetChange.objects.all()
    serializer_class = ProgramBudgetChangeSerializer
    permission_classes = [IsAuthenticated]

class SocialProgramEligibilityViewSet(viewsets.ModelViewSet):
    queryset = SocialProgramEligibility.objects.all()
    serializer_class = SocialProgramEligibilitySerializer
    permission_classes = [IsAuthenticated]