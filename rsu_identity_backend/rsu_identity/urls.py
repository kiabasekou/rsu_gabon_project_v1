# =============================================================================
# FICHIER: rsu_identity/urls.py (PRINCIPAL CORRIGÉ)
# CORRECTION: Éliminer duplications et structure claire
# =============================================================================

"""
🇬🇦 RSU Gabon - URLs Configuration Principale
Standards Top 1% - Architecture RESTful Optimisée
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
@permission_classes([AllowAny])
def api_root(request):
    """
    Point d'entrée principal des APIs RSU Gabon
    Documentation et navigation des endpoints
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
        'endpoints': {
            'core': {
                'users': request.build_absolute_uri('/api/v1/core/users/'),
                'audit_logs': request.build_absolute_uri('/api/v1/core/audit-logs/')
            },
            'identity': {
                'persons': request.build_absolute_uri('/api/v1/identity/persons/'),
                'households': request.build_absolute_uri('/api/v1/identity/households/'),
                'geographic_data': request.build_absolute_uri('/api/v1/identity/geographic-data/')
            }
        },
        'authentication': {
            'token_endpoint': request.build_absolute_uri('/api/v1/auth/token/'),
            'refresh_endpoint': request.build_absolute_uri('/api/v1/auth/token/refresh/')
        }
    }, status=status.HTTP_200_OK)

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
    
    # Authentification JWT
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # APIs REST v1 - STRUCTURE CLAIRE SANS DUPLICATION
    path('api/v1/core/', include('apps.core_app.urls')),
    path('api/v1/identity/', include('apps.identity_app.urls')),
    
    # Health Checks & Monitoring
    path('health/', include('health_check.urls')),

    #SERVICES APP
    path('api/v1/services/', include('apps.services_app.urls')),

]

# Servir les fichiers statiques en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar si activé
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns