"""
URLs pour l'app core_app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'core_app'

router = DefaultRouter()
# TODO: Ajouter les ViewSets ici

urlpatterns = [
    path('', include(router.urls)),
]
