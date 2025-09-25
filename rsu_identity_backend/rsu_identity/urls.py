"""
🇬🇦 RSU Gabon - URLs Configuration
Standards Top 1% - Architecture RESTful
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# URLs API v1
api_v1_patterns = [
    path('identity/', include('apps.identity_app.urls')),
    path('eligibility/', include('apps.eligibility.urls')), 
    path('programs/', include('apps.programs_app.urls')),
    path('surveys/', include('apps.surveys.urls')),
    path('analytics/', include('apps.analytics.urls')),
]

urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # APIs REST v1
    path('api/v1/', include(api_v1_patterns)),
    
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
