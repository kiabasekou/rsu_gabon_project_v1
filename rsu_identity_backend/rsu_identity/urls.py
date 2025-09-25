
# =============================================================================
# MISE À JOUR: rsu_identity/urls.py (PRINCIPAL)
# =============================================================================

"""
🇬🇦 RSU Gabon - URLs Configuration Principale
Standards Top 1% - Architecture RESTful Complète
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView, 
    SpectacularRedocView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

@api_view(['GET'])
@permission_classes([AllowAny])  # Permettre l'accès sans authentification
def api_root(request):
    """
    Point d'entrée principal des APIs RSU Gabon
    Accessible sans authentification pour documentation
    """
    return Response({
        'message': '🇬🇦 Bienvenue sur les APIs RSU Gabon',
        'version': 'v1.0.0',
        'description': 'Registre Social Unifié - APIs Gouvernementales',
        'status': 'Opérationnel',
        'documentation': {
            'swagger': request.build_absolute_uri('/api/docs/'),
            'redoc': request.build_absolute_uri('/api/redoc/'),
            'schema': request.build_absolute_uri('/api/schema/')
        },
        'authentication': {
            'description': 'JWT Token requis pour la plupart des endpoints',
            'token_endpoint': request.build_absolute_uri('/api/v1/auth/token/'),
            'refresh_endpoint': request.build_absolute_uri('/api/v1/auth/token/refresh/'),
            'example': {
                'curl': 'curl -X POST /api/v1/auth/token/ -H "Content-Type: application/json" -d \'{"username": "your_username", "password": "your_password"}\''
            }
        },
        'endpoints': {
            'core': {
                'users': request.build_absolute_uri('/api/v1/core/users/'),
                'audit_logs': request.build_absolute_uri('/api/v1/core/audit-logs/'),
                'me': request.build_absolute_uri('/api/v1/core/users/me/'),
                'surveyors': request.build_absolute_uri('/api/v1/core/users/surveyors/')
            },
            'identity': {
                'description': 'En développement - Prochaine étape',
                'persons': request.build_absolute_uri('/api/v1/identity/persons/'),
                'households': request.build_absolute_uri('/api/v1/identity/households/')
            }
        }
    }, status=status.HTTP_200_OK)

# URLs API v1
api_v1_patterns = [
    # Core App - Utilisateurs et audit
    path('core/', include('apps.core_app.urls')),
    
    # Identity App - Identités et ménages (à venir)
    path('identity/', include('apps.identity_app.urls')),
    
    # Autres apps (à développer)
    # path('eligibility/', include('apps.eligibility.urls')),
    # path('programs/', include('apps.programs_app.urls')),
    # path('surveys/', include('apps.surveys.urls')),
    # path('analytics/', include('apps.analytics.urls')),
]

# URLs principales
urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),
    
    # Point d'entrée API
    path('api/', api_root, name='api-root'),
    
    # Documentation API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # APIs REST v1
    path('api/v1/', include(api_v1_patterns)),
    
    # Authentification JWT
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Health Checks & Monitoring
    path('health/', include('health_check.urls')),
]

# Servir les fichiers statiques en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns


