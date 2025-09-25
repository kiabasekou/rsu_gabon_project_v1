"""
URLs pour l'app family_graph
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'family_graph'

router = DefaultRouter()
# TODO: Ajouter les ViewSets ici

urlpatterns = [
    path('', include(router.urls)),
]
