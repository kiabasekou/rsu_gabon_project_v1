
# =============================================================================
# FICHIER: apps/core_app/views/audit_views.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Audit ViewSets  
APIs REST pour consultation des logs d'audit
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.core_app.models import AuditLog
from apps.core_app.serializers import AuditLogSerializer
from .permissions import IsAdminOrAuditor

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consultation des logs d'audit
    
    Fonctionnalités:
    - Lecture seule (conformité audit)
    - Filtrage avancé par utilisateur, action, période
    - Statistiques et rapports d'audit
    - Export pour gouvernance
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'severity', 'user__user_type', 'user']
    search_fields = ['description', 'user__username', 'ip_address']
    ordering_fields = ['created_at', 'severity', 'action']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Permissions strictes pour audit"""
        if self.action in ['stats', 'export', 'user_activity']:
            permission_classes = [IsAuthenticated, IsAdminOrAuditor]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrage selon permissions utilisateur"""
        user = self.request.user
        queryset = AuditLog.objects.all()
        
        # Admins et auditeurs voient tout
        if user.is_staff or user.user_type in ['ADMIN', 'AUDITOR']:
            return queryset
        
        # Superviseurs voient leur équipe
        elif user.user_type == 'SUPERVISOR':
            team_users = RSUUser.objects.filter(
                assigned_provinces__overlap=user.assigned_provinces
            )
            return queryset.filter(user__in=team_users)
        
        # Autres utilisateurs voient leurs actions uniquement
        else:
            return queryset.filter(user=user)
    
    def list(self, request, *args, **kwargs):
        """Liste avec filtres temporels automatiques"""
        # Filtrage par défaut: 30 derniers jours
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(created_at__gte=start_date)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminOrAuditor])
    def stats(self, request):
        """Statistiques d'audit"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(created_at__gte=start_date)
        
        stats = {
            'period_days': days,
            'total_actions': queryset.count(),
            'unique_users': queryset.values('user').distinct().count(),
            'by_action': {},
            'by_severity': {},
            'by_user_type': {},
            'recent_critical': []
        }
        
        # Actions par type
        actions = queryset.values('action').annotate(count=Count('action'))
        for item in actions:
            stats['by_action'][item['action']] = item['count']
        
        # Par sévérité
        severities = queryset.values('severity').annotate(count=Count('severity'))
        for item in severities:
            stats['by_severity'][item['severity']] = item['count']
        
        # Par type utilisateur
        user_types = queryset.values('user__user_type').annotate(count=Count('user__user_type'))
        for item in user_types:
            stats['by_user_type'][item['user__user_type']] = item['count']
        
        # Actions critiques récentes
        critical_logs = queryset.filter(severity='CRITICAL')[:10]
        stats['recent_critical'] = AuditLogSerializer(
            critical_logs, many=True, context={'request': request}
        ).data
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """Activité d'un utilisateur spécifique"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id requis'}, status=400)
        
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(
            user_id=user_id,
            created_at__gte=start_date
        )
        
        # Vérification permissions
        if not (request.user.is_staff or 
                request.user.user_type in ['ADMIN', 'AUDITOR'] or 
                str(request.user.id) == user_id):
            return Response({'error': 'Permission refusée'}, status=403)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'period_days': days,
            'total_actions': queryset.count(),
            'actions': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def suspicious_activity(self, request):
        """Détection d'activité suspecte"""
        if not (request.user.is_staff or request.user.user_type in ['ADMIN', 'AUDITOR']):
            return Response({'error': 'Permission refusée'}, status=403)
        
        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        suspicious = {
            'multiple_failed_logins': [],
            'unusual_access_patterns': [],
            'bulk_operations': []
        }
        
        # Échecs de connexion multiples
        failed_logins = AuditLog.objects.filter(
            action='LOGIN_FAILED',
            created_at__gte=last_hour
        ).values('ip_address', 'user_agent').annotate(
            count=Count('id')
        ).filter(count__gte=5)
        
        suspicious['multiple_failed_logins'] = list(failed_logins)
        
        # Opérations en lot suspectes
        bulk_ops = AuditLog.objects.filter(
            action__in=['CREATE', 'UPDATE', 'DELETE'],
            created_at__gte=last_hour
        ).values('user').annotate(
            count=Count('id')
        ).filter(count__gte=50)
        
        suspicious['bulk_operations'] = list(bulk_ops)
        
        return Response(suspicious)