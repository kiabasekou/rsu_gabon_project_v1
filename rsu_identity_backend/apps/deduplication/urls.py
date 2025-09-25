"""
URLs pour l'app deduplication
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'deduplication'

router = DefaultRouter()
# TODO: Ajouter les ViewSets ici

urlpatterns = [
    path('', include(router.urls)),
]
