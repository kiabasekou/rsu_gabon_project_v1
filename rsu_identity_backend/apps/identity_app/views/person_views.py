
# =============================================================================
# FICHIER: apps/identity_app/views/person_views.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Person ViewSets
APIs REST pour gestion des identités personnelles
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from fuzzywuzzy import fuzz

from apps.identity_app.models import PersonIdentity, RBPPSync
from apps.identity_app.serializers import (
    PersonIdentitySerializer, PersonIdentityCreateSerializer,
    PersonIdentityUpdateSerializer, PersonIdentityMinimalSerializer,
    PersonIdentitySearchSerializer
)
from apps.core_app.views.permissions import IsSurveyorOrSupervisor, CanAccessProvince
from apps.core_app.models import AuditLog

class PersonIdentityViewSet(viewsets.ModelViewSet):
    queryset = PersonIdentity.objects.all()
    serializer_class = PersonIdentitySerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # ✅ AJOUT filtrage par employment_status
    filterset_fields = [
        'gender', 'marital_status', 'province', 'department', 'commune',
        'education_level', 'verification_status', 'rbpp_synchronized',
        'has_disability', 'is_household_head',
        'employment_status',  # ✅ Nouveau filtre
    ]
    
    search_fields = [
        'first_name', 'last_name', 'rsu_id', 'nip', 'phone_number',
        'national_id', 'address',
        'occupation', 'employer',  # ✅ Recherche sur profession/employeur
    ]
    
    ordering_fields = [
        'created_at', 'last_name', 'birth_date', 
        'data_completeness_score', 'verification_status',
        'employment_status', 'monthly_income',  # ✅ Tri par statut/revenu
    ]
    
    @action(detail=False, methods=['get'])
    def employment_statistics(self, request):
        """
        Statistiques emploi par province
        GET /api/v1/identity/persons/employment_statistics/
        """
        from django.db.models import Count, Avg
        
        stats = self.get_queryset().values(
            'province', 'employment_status'
        ).annotate(
            count=Count('id'),
            avg_income=Avg('monthly_income')
        ).order_by('province', 'employment_status')
        
        # Restructurer par province
        by_province = {}
        for stat in stats:
            prov = stat['province']
            if prov not in by_province:
                by_province[prov] = {
                    'total': 0,
                    'by_status': {},
                    'avg_income': 0
                }
            
            status = stat['employment_status'] or 'NON_RENSEIGNE'
            by_province[prov]['by_status'][status] = {
                'count': stat['count'],
                'avg_income': float(stat['avg_income'] or 0)
            }
            by_province[prov]['total'] += stat['count']
        
        return Response({
            'success': True,
            'statistics': by_province,
            'generated_at': timezone.now().isoformat()
        })
    
    @action(detail=False, methods=['get'])
    def unemployed_vulnerable(self, request):
        """
        Liste chômeurs vulnérables
        GET /api/v1/identity/persons/unemployed_vulnerable/
        """
        min_household_size = int(request.query_params.get('min_household_size', 4))
        max_income = int(request.query_params.get('max_income', 75000))
        
        queryset = self.get_queryset().filter(
            employment_status='UNEMPLOYED',
            monthly_income__lt=max_income,
            household__household_size__gte=min_household_size
        ).select_related('household')
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'criteria': {
                'employment_status': 'UNEMPLOYED',
                'max_monthly_income': max_income,
                'min_household_size': min_household_size
            },
            'count': queryset.count(),
            'persons': serializer.data
        })

    
    def get_serializer_class(self):
        """Serializer adapté selon l'action"""
        if self.action == 'create':
            return PersonIdentityCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PersonIdentityUpdateSerializer
        elif self.action in ['list_minimal', 'search_duplicates']:
            return PersonIdentitySearchSerializer
        return PersonIdentitySerializer
    
    def get_queryset(self):
        """Filtrage selon les permissions géographiques"""
        user = self.request.user
        queryset = PersonIdentity.objects.select_related(
            'verified_by', 'created_by', 'updated_by'
        ).prefetch_related('rbpp_syncs')
        
        # Admins voient tout
        if user.is_staff or user.user_type == 'ADMIN':
            return queryset
        
        # Filtrage par provinces assignées
        if hasattr(user, 'assigned_provinces') and user.assigned_provinces:
            return queryset.filter(province__in=user.assigned_provinces)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Création avec audit et géolocalisation automatique"""
        person = serializer.save()
        
        # Copier coordonnées du chef de ménage si applicable
        if person.is_household_head and person.latitude and person.longitude:
            # Logique pour ménage sera implémentée
            pass
        
        # Log création
        AuditLog.log_action(
            user=self.request.user,
            action='CREATE',
            description=f"Création identité {person.full_name} ({person.rsu_id})",
            obj=person,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            severity='MEDIUM'
        )
    
    @action(detail=False, methods=['get'])
    def search_duplicates(self, request):
        """
        Recherche de doublons potentiels
        Utilise la correspondance floue sur nom, téléphone, date naissance
        """
        first_name = request.query_params.get('first_name', '').strip()
        last_name = request.query_params.get('last_name', '').strip()
        birth_date = request.query_params.get('birth_date')
        phone = request.query_params.get('phone_number', '').strip()
        
        if not (first_name and last_name):
            return Response(
                {'error': 'first_name et last_name requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Recherche de base
        queryset = self.get_queryset()
        candidates = []
        
        # Correspondance floue sur les noms
        for person in queryset:
            name_score = (
                fuzz.ratio(first_name.lower(), person.first_name.lower()) +
                fuzz.ratio(last_name.lower(), person.last_name.lower())
            ) / 2
            
            # Score téléphone si fourni
            phone_score = 0
            if phone and person.phone_number:
                phone_score = fuzz.ratio(phone, person.phone_number)
            
            # Score date naissance si fournie
            birth_score = 0
            if birth_date and str(person.birth_date) == birth_date:
                birth_score = 100
            
            # Score global pondéré
            global_score = (name_score * 0.6 + phone_score * 0.3 + birth_score * 0.1)
            
            # Seuil de similarité
            if global_score >= 70:
                person.similarity_score = global_score
                candidates.append(person)
        
        # Trier par score de similarité
        candidates.sort(key=lambda x: x.similarity_score, reverse=True)
        
        serializer = PersonIdentitySearchSerializer(
            candidates[:10], many=True, context={'request': request}
        )
        
        return Response({
            'query': {
                'first_name': first_name,
                'last_name': last_name,
                'birth_date': birth_date,
                'phone_number': phone
            },
            'candidates': serializer.data,
            'total_found': len(candidates)
        })
    
    @action(detail=True, methods=['post'])
    def validate_nip(self, request, pk=None):
        """
        Validation NIP avec système RBPP
        Déclenche synchronisation automatique
        """
        person = self.get_object()
        nip = request.data.get('nip')
        
        if not nip:
            return Response(
                {'error': 'NIP requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier format NIP (13 chiffres)
        if not (nip.isdigit() and len(nip) == 13):
            return Response(
                {'error': 'Format NIP invalide (13 chiffres requis)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer demande de synchronisation RBPP
        sync = RBPPSync.objects.create(
            person=person,
            sync_type='VALIDATION',
            nip_requested=nip,
            started_at=timezone.now()
        )
        
        # TODO: Intégration réelle RBPP ici
        # Pour l'instant, simulation
        import time
        import random
        time.sleep(1)  # Simulation délai réseau
        
        if random.choice([True, False]):  # Simulation succès/échec
            sync.mark_success({
                'nip_validated': True,
                'person_data': {
                    'first_name': person.first_name,
                    'last_name': person.last_name,
                    'birth_date': str(person.birth_date)
                }
            })
            
            person.nip = nip
            person.rbpp_synchronized = True
            person.rbpp_last_sync = timezone.now()
            person.save()
            
            return Response({
                'message': 'NIP validé avec succès',
                'nip': nip,
                'rbpp_synchronized': True
            })
        else:
            sync.mark_failed('INVALID_NIP', 'NIP non trouvé dans RBPP')
            return Response(
                {'error': 'NIP non valide ou non trouvé dans RBPP'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def vulnerability_report(self, request):
        """
        Rapport de vulnérabilité par zone géographique
        """
        province = request.query_params.get('province')
        commune = request.query_params.get('commune')
        
        queryset = self.get_queryset()
        
        if province:
            queryset = queryset.filter(province=province)
        if commune:
            queryset = queryset.filter(commune=commune)
        
        # Calculs statistiques
        total = queryset.count()
        
        stats = {
            'total_persons': total,
            'by_gender': dict(queryset.values_list('gender').annotate(Count('gender'))),
            'vulnerable_age': queryset.filter(
                Q(birth_date__gte=timezone.now().date().replace(year=timezone.now().year-5)) |
                Q(birth_date__lt=timezone.now().date().replace(year=timezone.now().year-65))
            ).count(),
            'with_disability': queryset.filter(has_disability=True).count(),
            'female_heads': queryset.filter(gender='F', is_household_head=True).count(),
            'unverified': queryset.filter(verification_status='PENDING').count(),
            'data_quality': {
                'high_completeness': queryset.filter(data_completeness_score__gte=80).count(),
                'low_completeness': queryset.filter(data_completeness_score__lt=50).count(),
            }
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def export_data(self, request):
        """
        Export des données pour rapports gouvernementaux
        """
        if not (request.user.is_staff or request.user.user_type in ['ADMIN', 'SUPERVISOR']):
            return Response(
                {'error': 'Permission refusée'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        format_type = request.query_params.get('format', 'json')
        queryset = self.filter_queryset(self.get_queryset())
        
        # Log export pour audit
        AuditLog.log_action(
            user=request.user,
            action='EXPORT',
            description=f"Export données identités ({queryset.count()} enregistrements)",
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            severity='HIGH'
        )
        
        if format_type == 'csv':
            # TODO: Implémenter export CSV
            return Response({'message': 'Export CSV en développement'})
        else:
            serializer = PersonIdentityMinimalSerializer(
                queryset, many=True, context={'request': request}
            )
            return Response({
                'data': serializer.data,
                'metadata': {
                    'total_records': queryset.count(),
                    'export_date': timezone.now(),
                    'exported_by': request.user.username
                }
            })
