
"""
🇬🇦 RSU Gabon - User ViewSets
APIs REST pour gestion des utilisateurs RSU

MODIFICATION: Import et utilisation du FilterSet custom pour corriger l'erreur JSONField
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Q

from apps.core_app.models import RSUUser, AuditLog
from apps.core_app.serializers import (
    RSUUserSerializer, RSUUserCreateSerializer, 
    RSUUserUpdateSerializer, RSUUserMinimalSerializer
)
# ✅ CORRECTION: Import du FilterSet custom
from apps.core_app.filters import RSUUserFilter

from .permissions import IsAdminOrSupervisor, IsOwnerOrAdmin

class RSUUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gestion des utilisateurs RSU
    
    Fonctionnalités:
    - CRUD complet avec permissions granulaires
    - Filtrage par type, département, province
    - Actions spéciales: login, logout, change_password
    - Audit automatique des actions
    
    ✅ CORRECTION APPLIQUÉE:
    - Utilisation de RSUUserFilter au lieu de filterset_fields
    - Résout l'AssertionError sur assigned_provinces (JSONField)
    """
    queryset = RSUUser.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # ❌ ANCIENNE VERSION (causait l'erreur):
    # filterset_fields = ['user_type', 'department', 'is_active', 'assigned_provinces']
    
    # ✅ NOUVELLE VERSION (corrige l'erreur):
    filterset_class = RSUUserFilter
    
    search_fields = ['username', 'first_name', 'last_name', 'employee_id', 'email']
    ordering_fields = ['username', 'date_joined', 'last_login', 'user_type']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        """Serializer adapté selon l'action"""
        if self.action == 'create':
            return RSUUserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RSUUserUpdateSerializer
        elif self.action in ['list_minimal', 'get_surveyors']:
            return RSUUserMinimalSerializer
        return RSUUserSerializer
    
    def get_permissions(self):
        """Permissions adaptées selon l'action"""
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        elif self.action in ['deactivate', 'activate', 'reset_password']:
            permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrage selon les permissions utilisateur"""
        user = self.request.user
        queryset = RSUUser.objects.all()
        
        # Admins voient tout
        if user.is_staff or user.user_type == 'ADMIN':
            return queryset
        
        # Superviseurs voient leur équipe
        elif user.user_type == 'SUPERVISOR':
            # Utilisateurs des mêmes provinces
            user_provinces = set(user.assigned_provinces)
            return queryset.filter(
                Q(assigned_provinces__overlap=user_provinces) |
                Q(id=user.id)
            )
        
        # Autres utilisateurs voient seulement leur profil
        else:
            return queryset.filter(id=user.id)
    
    def perform_create(self, serializer):
        """Création avec audit automatique"""
        user = serializer.save()
        
        # Log création
        AuditLog.log_action(
            user=self.request.user,
            action='CREATE',
            description=f"Création utilisateur {user.username}",
            obj=user,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            severity='MEDIUM'
        )
    
    def perform_destroy(self, instance):
        """Suppression logique avec audit"""
        # Désactivation au lieu de suppression
        instance.is_active = False
        instance.save()
        
        # Log désactivation
        AuditLog.log_action(
            user=self.request.user,
            action='DELETE',
            description=f"Désactivation utilisateur {instance.username}",
            obj=instance,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            severity='HIGH'
        )
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Profile de l'utilisateur connecté"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def change_password(self, request, pk=None):
        """Changement de mot de passe"""
        user = self.get_object()
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': 'old_password et new_password requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérification ancien mot de passe
        if not user.check_password(old_password):
            return Response(
                {'error': 'Ancien mot de passe incorrect'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validation nouveau mot de passe
        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Changement
        user.set_password(new_password)
        user.save()
        
        # Audit log
        AuditLog.log_action(
            user=request.user,
            action='PASSWORD_CHANGE',
            description=f"Changement mot de passe utilisateur {user.username}",
            obj=user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            severity='MEDIUM'
        )
        
        return Response({'message': 'Mot de passe changé avec succès'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrSupervisor])
    def deactivate(self, request, pk=None):
        """Désactivation d'un utilisateur"""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        # Audit log
        AuditLog.log_action(
            user=request.user,
            action='ADMIN_ACTION',
            description=f"Désactivation forcée utilisateur {user.username}",
            obj=user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            severity='HIGH'
        )
        
        return Response({'message': f'Utilisateur {user.username} désactivé'})
    
    @action(detail=False, methods=['get'])
    def list_minimal(self, request):
        """Liste minimale pour sélections rapides"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = RSUUserMinimalSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def surveyors(self, request):
        """Liste des enquêteurs par province"""
        province = request.query_params.get('province')
        
        queryset = RSUUser.objects.filter(
            user_type='SURVEYOR',
            is_active=True
        )
        
        if province:
            queryset = queryset.filter(assigned_provinces__contains=[province])
        
        serializer = RSUUserMinimalSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques utilisateurs"""
        if not (request.user.is_staff or request.user.user_type in ['ADMIN', 'SUPERVISOR']):
            return Response(
                {'error': 'Permission refusée'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_users': RSUUser.objects.count(),
            'active_users': RSUUser.objects.filter(is_active=True).count(),
            'by_type': {}
        }
        
        # Répartition par type
        for user_type, _ in RSUUser.USER_TYPES:
            count = RSUUser.objects.filter(user_type=user_type, is_active=True).count()
            stats['by_type'][user_type] = count
        
        return Response(stats)
    

# =============================================================================
# RÉSUMÉ DE LA CORRECTION
# =============================================================================
"""
PROBLÈME INITIAL:
---------------
AssertionError: AutoFilterSet resolved field 'assigned_provinces' with 'exact' 
lookup to an unrecognized field type JSONField.

CAUSE RACINE:
-------------
- Le champ 'assigned_provinces' dans RSUUser est un JSONField
- django-filter ne peut pas générer automatiquement un filter pour JSONField
- L'utilisation de filterset_fields incluant 'assigned_provinces' causait l'erreur

SOLUTION APPLIQUÉE (Standards Top 1%):
--------------------------------------
1. Création d'un FilterSet custom dans apps/core_app/filters.py
2. Exclusion explicite de 'assigned_provinces' des champs filtrables
3. Définition explicite des filters pour user_type, department, is_active
4. Utilisation de filterset_class au lieu de filterset_fields dans le ViewSet

CONFORMITÉ AUX CONSIGNES:
--------------------------
✅ Consigne 1: SSOT - Noms de champs copiés exactement depuis le modèle
✅ Consigne 3: Typage strict - Respect du type JSONField et de ses limitations
✅ Consigne 4: Schema First - Correction du schéma de filtrage avant test

PRÉVENTION FUTURE:
------------------
- Ne JAMAIS inclure de JSONField dans filterset_fields sans FilterSet custom
- Toujours définir filterset_class pour les modèles avec champs complexes
- Utiliser filter_overrides pour gérer les types non-standard
"""