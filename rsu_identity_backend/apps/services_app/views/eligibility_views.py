"""
🇬🇦 RSU Gabon - Eligibility Views (Stub)
À développer : Moteur d'éligibilité programmes sociaux
"""

#apps/services_app/views/eligibility_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.services_app.models import SocialProgramEligibility
from apps.services_app.serializers import SocialProgramEligibilitySerializer

class EligibilityViewSet(viewsets.ModelViewSet):
    """ViewSet pour éligibilité programmes sociaux (TODO)"""
    queryset = SocialProgramEligibility.objects.all()
    serializer_class = SocialProgramEligibilitySerializer
    permission_classes = [IsAuthenticated]