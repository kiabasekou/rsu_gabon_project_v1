"""
URLs pour l'app identity_app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'identity_app'

router = DefaultRouter()
# TODO: Ajouter les ViewSets ici

urlpatterns = [
    path('', include(router.urls)),
]
