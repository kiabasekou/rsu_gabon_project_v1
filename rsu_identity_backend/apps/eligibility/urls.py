"""
URLs pour l'app eligibility
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'eligibility'

router = DefaultRouter()
# TODO: Ajouter les ViewSets ici

urlpatterns = [
    path('', include(router.urls)),
]
