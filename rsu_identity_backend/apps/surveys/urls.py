"""
URLs pour l'app surveys
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'surveys'

router = DefaultRouter()
# TODO: Ajouter les ViewSets ici

urlpatterns = [
    path('', include(router.urls)),
]
