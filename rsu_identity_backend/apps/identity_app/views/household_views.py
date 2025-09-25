
# =============================================================================
# FICHIER: apps/identity_app/views/household_views.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Household ViewSets
APIs REST pour gestion des ménages
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Sum

from apps.identity_app.models import Household, HouseholdMember
from apps.identity_app.serializers import (
    HouseholdSerializer, HouseholdCreateSerializer,
    HouseholdMemberSerializer, HouseholdMemberCreateSerializer
)
from apps.core_app.views.permissions import IsSurveyorOrSupervisor
from apps.core_app.models import AuditLog

class HouseholdViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gestion des ménages
    """
    queryset = Household.objects.all()
    serializer_class = HouseholdSerializer
    permission_classes = [IsAuthenticated, IsSurveyorOrSupervisor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = [
        'household_type', 'housing_type', 'water_access', 'electricity_access',
        'province', 'has_disabled_members', 'has_elderly_members'
    ]
    search_fields = [
        'household_id', 'head_of_household__first_name', 'head_of_household__last_name'
    ]
    ordering_fields = ['created_at', 'household_size', 'total_monthly_income']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HouseholdCreateSerializer
        return HouseholdSerializer
    
    def get_queryset(self):
        """Filtrage géographique"""
        user = self.request.user
        queryset = Household.objects.select_related('head_of_household').prefetch_related('members')
        
        if user.is_staff or user.user_type == 'ADMIN':
            return queryset
        
        if hasattr(user, 'assigned_provinces') and user.assigned_provinces:
            return queryset.filter(province__in=user.assigned_provinces)
        
        return queryset.none()
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques des ménages"""
        queryset = self.get_queryset()
        
        stats = {
            'total_households': queryset.count(),
            'by_type': dict(queryset.values_list('household_type').annotate(Count('household_type'))),
            'average_size': queryset.aggregate(Avg('household_size'))['household_size__avg'],
            'total_population': queryset.aggregate(Sum('household_size'))['household_size__sum'],
            'vulnerability_indicators': {
                'with_disabilities': queryset.filter(has_disabled_members=True).count(),
                'with_elderly': queryset.filter(has_elderly_members=True).count(),
                'with_young_children': queryset.filter(has_children_under_5=True).count(),
                'female_headed': queryset.filter(head_of_household__gender='F').count()
            }
        }
        
        return Response(stats)


class HouseholdMemberViewSet(viewsets.ModelViewSet):
    """ViewSet pour membres de ménages"""
    queryset = HouseholdMember.objects.all()
    serializer_class = HouseholdMemberSerializer
    permission_classes = [IsAuthenticated, IsSurveyorOrSupervisor]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HouseholdMemberCreateSerializer
        return HouseholdMemberSerializer
