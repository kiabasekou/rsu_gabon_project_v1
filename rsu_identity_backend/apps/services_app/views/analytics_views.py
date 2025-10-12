"""
🇬🇦 RSU Gabon - Analytics ViewSet pour Dashboard
Standards Top 1% - APIs Analytics et Statistiques
Fichier: rsu_identity_backend/apps/services_app/views/analytics_views.py
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.identity_app.models import PersonIdentity, Household
from apps.services_app.models import VulnerabilityAssessment, SocialProgramEligibility
from apps.core_app.permissions import IsSurveyorOrHigher


class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet pour Analytics et Statistiques Dashboard
    
    Endpoints:
    - GET /api/v1/analytics/dashboard/ - Vue d'ensemble complète
    - GET /api/v1/analytics/vulnerability-stats/ - Stats vulnérabilité
    - GET /api/v1/analytics/geographic-distribution/ - Répartition géographique
    - GET /api/v1/analytics/demographic-insights/ - Insights démographiques
    """
    
    permission_classes = [IsAuthenticated, IsSurveyorOrHigher]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Vue d'ensemble complète du dashboard
        
        Returns:
            {
                'overview': {...},
                'vulnerability': {...},
                'geographic': {...},
                'demographic': {...},
                'recent_activity': {...}
            }
        """
        try:
            # 1. VUE D'ENSEMBLE
            overview = self._get_overview_stats()
            
            # 2. STATISTIQUES VULNÉRABILITÉ
            vulnerability = self._get_vulnerability_stats()
            
            # 3. RÉPARTITION GÉOGRAPHIQUE
            geographic = self._get_geographic_distribution()
            
            # 4. INSIGHTS DÉMOGRAPHIQUES
            demographic = self._get_demographic_insights()
            
            # 5. ACTIVITÉ RÉCENTE
            recent_activity = self._get_recent_activity()
            
            return Response({
                'overview': overview,
                'vulnerability': vulnerability,
                'geographic': geographic,
                'demographic': demographic,
                'recent_activity': recent_activity,
                'generated_at': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur génération dashboard: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_overview_stats(self):
        """Statistiques générales"""
        total_persons = PersonIdentity.objects.count()
        total_households = Household.objects.count()
        total_assessments = VulnerabilityAssessment.objects.count()
        
        # Personnes vérifiées
        verified_persons = PersonIdentity.objects.filter(
            verification_status='VERIFIED'
        ).count()
        
        # Taux de complétude moyen
        avg_completeness = PersonIdentity.objects.aggregate(
            avg_score=Avg('data_completeness_score')
        )['avg_score'] or 0
        
        # Personnes créées cette semaine
        week_ago = timezone.now() - timedelta(days=7)
        persons_this_week = PersonIdentity.objects.filter(
            created_at__gte=week_ago
        ).count()
        
        return {
            'total_persons': total_persons,
            'total_households': total_households,
            'total_assessments': total_assessments,
            'verified_persons': verified_persons,
            'verification_rate': round((verified_persons / total_persons * 100) if total_persons > 0 else 0, 2),
            'avg_completeness': round(float(avg_completeness), 2),
            'persons_this_week': persons_this_week
        }
    
    def _get_vulnerability_stats(self):
        """Statistiques vulnérabilité détaillées"""
        # Répartition par niveau
        level_distribution = VulnerabilityAssessment.objects.values(
            'risk_level'
        ).annotate(
            count=Count('id')
        ).order_by('risk_level')
        
        # Score moyen par niveau
        avg_scores = {}
        for level_data in level_distribution:
            level = level_data['risk_level']
            avg_score = VulnerabilityAssessment.objects.filter(
                risk_level=level
            ).aggregate(avg=Avg('vulnerability_score'))['avg']
            avg_scores[level] = round(float(avg_score or 0), 2)
        
        # Personnes par niveau de vulnérabilité
        critical = PersonIdentity.objects.filter(
            vulnerability_level='CRITICAL'
        ).count()
        high = PersonIdentity.objects.filter(
            vulnerability_level='HIGH'
        ).count()
        moderate = PersonIdentity.objects.filter(
            vulnerability_level='MODERATE'
        ).count()
        low = PersonIdentity.objects.filter(
            vulnerability_level='LOW'
        ).count()
        
        # Score moyen global
        global_avg = PersonIdentity.objects.aggregate(
            avg=Avg('vulnerability_score')
        )['avg'] or 0
        
        return {
            'distribution': {
                'critical': critical,
                'high': high,
                'moderate': moderate,
                'low': low
            },
            'assessment_count': VulnerabilityAssessment.objects.count(),
            'avg_scores_by_level': avg_scores,
            'global_average_score': round(float(global_avg), 2),
            'trend': self._calculate_vulnerability_trend()
        }
    
    def _get_geographic_distribution(self):
        """Répartition géographique"""
        # Par province
        province_stats = PersonIdentity.objects.values(
            'province'
        ).annotate(
            count=Count('id'),
            avg_vulnerability=Avg('vulnerability_score'),
            critical_count=Count('id', filter=Q(vulnerability_level='CRITICAL')),
            high_count=Count('id', filter=Q(vulnerability_level='HIGH'))
        ).order_by('-count')
        
        # Top 5 communes
        commune_stats = PersonIdentity.objects.exclude(
            commune__isnull=True
        ).values(
            'commune', 'province'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return {
            'by_province': [
                {
                    'province': item['province'],
                    'count': item['count'],
                    'avg_vulnerability': round(float(item['avg_vulnerability'] or 0), 2),
                    'critical_count': item['critical_count'],
                    'high_count': item['high_count']
                }
                for item in province_stats
            ],
            'top_communes': [
                {
                    'commune': item['commune'],
                    'province': item['province'],
                    'count': item['count']
                }
                for item in commune_stats
            ]
        }
    
    def _get_demographic_insights(self):
        """Insights démographiques"""
        # Répartition par genre
        gender_stats = PersonIdentity.objects.values('gender').annotate(
            count=Count('id')
        )
        
        # Tranches d'âge (approximatif basé sur birth_date)
        today = timezone.now().date()
        minors = PersonIdentity.objects.filter(
            birth_date__gte=today - timedelta(days=18*365)
        ).count()
        
        adults = PersonIdentity.objects.filter(
            birth_date__lt=today - timedelta(days=18*365),
            birth_date__gte=today - timedelta(days=65*365)
        ).count()
        
        seniors = PersonIdentity.objects.filter(
            birth_date__lt=today - timedelta(days=65*365)
        ).count()
        
        # Statut marital
        marital_stats = PersonIdentity.objects.values('marital_status').annotate(
            count=Count('id')
        )
        
        # Niveau éducation
        education_stats = PersonIdentity.objects.values('education_level').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Statut emploi
        employment_stats = PersonIdentity.objects.values('employment_status').annotate(
            count=Count('id')
        )
        
        return {
            'by_gender': {item['gender']: item['count'] for item in gender_stats},
            'by_age_group': {
                'minors': minors,
                'adults': adults,
                'seniors': seniors
            },
            'by_marital_status': {item['marital_status']: item['count'] for item in marital_stats if item['marital_status']},
            'by_education': [
                {'level': item['education_level'], 'count': item['count']}
                for item in education_stats if item['education_level']
            ],
            'by_employment': {item['employment_status']: item['count'] for item in employment_stats if item['employment_status']}
        }
    
    def _get_recent_activity(self):
        """Activité récente"""
        # 10 dernières personnes créées
        recent_persons = PersonIdentity.objects.order_by('-created_at')[:10].values(
            'rsu_id', 'first_name', 'last_name', 'province', 'created_at'
        )
        
        # 10 dernières évaluations
        recent_assessments = VulnerabilityAssessment.objects.select_related(
            'person'
        ).order_by('-assessment_date')[:10].values(
            'person__rsu_id',
            'person__first_name',
            'person__last_name',
            'vulnerability_score',
            'risk_level',
            'assessment_date'
        )
        
        return {
            'recent_persons': list(recent_persons),
            'recent_assessments': [
                {
                    'person_rsu_id': item['person__rsu_id'],
                    'person_name': f"{item['person__first_name']} {item['person__last_name']}",
                    'vulnerability_score': float(item['vulnerability_score']),
                    'risk_level': item['risk_level'],
                    'assessment_date': item['assessment_date'].isoformat()
                }
                for item in recent_assessments
            ]
        }
    
    def _calculate_vulnerability_trend(self):
        """Calcule tendance vulnérabilité (30 derniers jours)"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        recent = VulnerabilityAssessment.objects.filter(
            assessment_date__gte=thirty_days_ago
        ).aggregate(avg=Avg('vulnerability_score'))['avg'] or 0
        
        older = VulnerabilityAssessment.objects.filter(
            assessment_date__lt=thirty_days_ago
        ).aggregate(avg=Avg('vulnerability_score'))['avg'] or 0
        
        if older == 0:
            return 'stable'
        
        change_pct = ((recent - older) / older) * 100
        
        if change_pct > 5:
            return 'increasing'
        elif change_pct < -5:
            return 'decreasing'
        else:
            return 'stable'
    
    @action(detail=False, methods=['get'])
    def vulnerability_stats(self, request):
        """Stats vulnérabilité détaillées"""
        return Response(self._get_vulnerability_stats())
    
    @action(detail=False, methods=['get'])
    def geographic_distribution(self, request):
        """Répartition géographique"""
        return Response(self._get_geographic_distribution())
    
    @action(detail=False, methods=['get'])
    def demographic_insights(self, request):
        """Insights démographiques"""
        return Response(self._get_demographic_insights())