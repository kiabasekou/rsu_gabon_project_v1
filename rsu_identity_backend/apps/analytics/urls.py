"""
URLs pour l'app analytics
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'analytics'

router = DefaultRouter()
# TODO: Ajouter les ViewSets ici

urlpatterns = [
    path('', include(router.urls)),
]
