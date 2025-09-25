# 🇬🇦 RSU GABON - CORE APP URLS
# Standards Top 1% - Routing APIs REST

# =============================================================================
# FICHIER: apps/core_app/urls.py
# =============================================================================

"""
🇬🇦 RSU Gabon - Core URLs
Routing des APIs Core App avec versioning
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RSUUserViewSet, AuditLogViewSet

app_name = 'core_app'

# Router principal pour les ViewSets
router = DefaultRouter()
router.register(r'users', RSUUserViewSet, basename='users')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-logs')

urlpatterns = [
    # APIs REST avec router
    path('', include(router.urls)),
    
    # URLs personnalisées si nécessaire
    # path('auth/', include('core_app.auth_urls')),
]