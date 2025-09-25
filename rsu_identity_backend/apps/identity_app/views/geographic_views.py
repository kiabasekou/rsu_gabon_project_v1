# =============================================================================
# FICHIER: apps/identity_app/views/geographic_views.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Geographic ViewSets
APIs REST pour données géographiques et ciblage
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg

from apps.identity_app.models import GeographicData
from apps.identity_app.serializers import GeographicDataSerializer
from apps.core_app.views.permissions import IsAdminOrSupervisor

class GeographicDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour données géographiques
    Ciblage et planification des programmes
    """
    queryset = GeographicData.objects.all()
    serializer_class = GeographicDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = [
        'province', 'zone_type', 'road_condition', 
        'mobile_network_coverage', 'internet_available'
    ]
    search_fields = ['location_name', 'province', 'department', 'commune']
    ordering_fields = ['accessibility_score', 'service_availability_score', 'population_estimate']
    ordering = ['-accessibility_score']
    
    @action(detail=False, methods=['get'])
    def priority_zones(self, request):
        """
        Zones prioritaires pour interventions
        Basé sur faible accessibilité et haute population
        """
        min_population = int(request.query_params.get('min_population', 1000))
        max_accessibility = float(request.query_params.get('max_accessibility', 50))
        
        priority_zones = self.get_queryset().filter(
            accessibility_score__lte=max_accessibility,
            population_estimate__gte=min_population
        ).order_by('accessibility_score')
        
        serializer = self.get_serializer(priority_zones, many=True)
        return Response({
            'criteria': {
                'max_accessibility_score': max_accessibility,
                'min_population': min_population
            },
            'zones': serializer.data,
            'total_priority_zones': priority_zones.count()
        })