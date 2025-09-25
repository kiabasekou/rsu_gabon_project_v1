"""
URLs pour l'app programs_app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'programs_app'

router = DefaultRouter()
# TODO: Ajouter les ViewSets ici

urlpatterns = [
    path('', include(router.urls)),
]
