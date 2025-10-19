"""
🇬🇦 RSU Gabon - URLs Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, JsonResponse

# =============================================================================
# HEALTH CHECK ULTRA-SIMPLE - Ne vérifie RIEN
# =============================================================================
def health_check(request):
    """
    Health check ultra-simple pour Railway
    Retourne toujours 200 OK sans vérifier DB/Cache
    """
    return HttpResponse("OK", status=200, content_type="text/plain")


# =============================================================================
# API ROOT SIMPLE
# =============================================================================
def api_root(request):
    """Root API endpoint"""
    return JsonResponse({
        "message": "🇬🇦 RSU Gabon API",
        "status": "operational"
    })


# =============================================================================
# URL PATTERNS
# =============================================================================
urlpatterns = [
    # Health Check (DOIT ÊTRE EN PREMIER)
    path('health/', health_check, name='health'),
    
    # Root
    path('', api_root, name='root'),
    path('api/', api_root, name='api-root'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Apps (ajoutez vos apps ici après que le healthcheck fonctionne)
    # path('api/v1/core/', include('apps.core_app.urls')),
    # path('api/v1/identity/', include('apps.identity_app.urls')),
    # ... etc
]