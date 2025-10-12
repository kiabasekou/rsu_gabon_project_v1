"""
🇬🇦 RSU Gabon - Analytics Views
Endpoints pour Dashboard Admin React
Standards Top 1% - Architecture RESTful
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from apps.programs_app.models import SocialProgram

from apps.identity_app.models import PersonIdentity, Household
from apps.services_app.models import VulnerabilityAssessment
from apps.core_app.models import RSUUser


class DashboardStatsAPIView(APIView):
    """
    Vue d'ensemble statistiques pour Dashboard Admin
    GET /api/v1/analytics/dashboard/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Statistiques globales du système"""
        
        # Calcul période de croissance (30 derniers jours)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Statistiques Bénéficiaires
        total_beneficiaries = PersonIdentity.objects.count()
        new_beneficiaries_month = PersonIdentity.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        beneficiaries_growth = (
            (new_beneficiaries_month / total_beneficiaries * 100) 
            if total_beneficiaries > 0 else 0
        )
        
        # Statistiques Ménages
        total_households = Household.objects.count()
        new_households_month = Household.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        households_growth = (
            (new_households_month / total_households * 100)
            if total_households > 0 else 0
        )
        
        # Score vulnérabilité moyen
        avg_vulnerability = VulnerabilityAssessment.objects.aggregate(
            avg_score=Avg('vulnerability_score')
        )['avg_score'] or 0
        
        

        active_programs = SocialProgram.objects.filter(status='ACTIVE').count()
        
        # Distribution par province
        # Distribution par province
        province_distribution = list(
            PersonIdentity.objects.values('province')
            .annotate(
                value=Count('id')
            )
            .order_by('-value')
        )

        # Noms de provinces lisibles
        PROVINCE_NAMES = {
            'ESTUAIRE': 'Estuaire',
            'HAUT_OGOOUE': 'Haut-Ogooué',
            'MOYEN_OGOOUE': 'Moyen-Ogooué',
            'NGOUNIE': 'Ngounié',
            'NYANGA': 'Nyanga',
            'OGOOUE_IVINDO': 'Ogooué-Ivindo',
            'OGOOUE_LOLO': 'Ogooué-Lolo',
            'OGOOUE_MARITIME': 'Ogooué-Maritime',
            'WOLEU_NTEM': 'Woleu-Ntem',
        }

        # Calculer total pour pourcentages
        total_count = sum(item['value'] for item in province_distribution)

        # Enrichir avec noms et pourcentages
        for item in province_distribution:
            item['name'] = PROVINCE_NAMES.get(item['province'], item['province'])
            item['percentage'] = (item['value'] / total_count * 100) if total_count > 0 else 0
        
        # Enrôlements mensuels (6 derniers mois)
        monthly_enrollments = []
        for i in range(5, -1, -1):
            month_start = timezone.now() - timedelta(days=30*i)
            month_end = timezone.now() - timedelta(days=30*(i-1)) if i > 0 else timezone.now()
            
            count = PersonIdentity.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            
            # ✅ APRÈS
            monthly_enrollments.append({
                'month': month_start.strftime('%b'),
                'count': count,  # ✅ Cohérent avec le reste de l'API
                'enrollments': count  # Garder les deux pour compatibilité
            })
        
        # Distribution vulnérabilité
        vulnerability_distribution = [
            {
                'category': 'EXTRÊME',
                'count': VulnerabilityAssessment.objects.filter(
                    vulnerability_score__gte=75
                ).count(),
                'color': '#dc2626'
            },
            {
                'category': 'ÉLEVÉE',
                'count': VulnerabilityAssessment.objects.filter(
                    vulnerability_score__gte=50,
                    vulnerability_score__lt=75
                ).count(),
                'color': '#ea580c'
            },
            {
                'category': 'MODÉRÉE',
                'count': VulnerabilityAssessment.objects.filter(
                    vulnerability_score__gte=25,
                    vulnerability_score__lt=50
                ).count(),
                'color': '#f59e0b'
            },
            {
                'category': 'FAIBLE',
                'count': VulnerabilityAssessment.objects.filter(
                    vulnerability_score__lt=25
                ).count(),
                'color': '#22c55e'
            }
        ]
        
        response_data = {
            'stats': {
                'total_beneficiaries': total_beneficiaries,
                'total_households': total_households,
                'active_programs': active_programs,
                'avg_vulnerability_score': round(avg_vulnerability, 1),
                'beneficiaries_growth': f"+{round(beneficiaries_growth, 1)}% ce mois",
                'households_growth': f"+{round(households_growth, 1)}% ce mois",
            },
            'province_distribution': province_distribution,
            'monthly_enrollments': monthly_enrollments,
            'vulnerability_distribution': vulnerability_distribution,
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'period': '30_days',
                'user': request.user.username
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class ProvinceStatsAPIView(APIView):
    """
    Statistiques par province
    GET /api/v1/analytics/province-stats/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Détails statistiques par province"""
        
        province = request.query_params.get('province', None)
        
        if province:
            # Stats pour une province spécifique
            stats = self._get_province_stats(province)
        else:
            # Stats pour toutes les provinces
            stats = self._get_all_provinces_stats()
        
        return Response(stats, status=status.HTTP_200_OK)
    
    def _get_province_stats(self, province):
        """Statistiques détaillées pour une province"""
        
        beneficiaries = PersonIdentity.objects.filter(province=province)
        households = Household.objects.filter(province=province)
        
        return {
            'province': province,
            'total_beneficiaries': beneficiaries.count(),
            'total_households': households.count(),
            'avg_household_size': households.aggregate(
                avg_size=Avg('household_size')
            )['avg_size'] or 0,
            'gender_distribution': {
                'male': beneficiaries.filter(gender='M').count(),
                'female': beneficiaries.filter(gender='F').count(),
            },
            'vulnerability_avg': VulnerabilityAssessment.objects.filter(
                person__province=province
            ).aggregate(avg=Avg('vulnerability_score'))['avg'] or 0
        }
    
    def _get_all_provinces_stats(self):
        """Vue d'ensemble toutes provinces"""
        
        provinces = PersonIdentity.objects.values_list('province', flat=True).distinct()
        
        return {
            'provinces': [
                self._get_province_stats(province) 
                for province in provinces if province
            ]
        }