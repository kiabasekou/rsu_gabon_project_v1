"""
🇬🇦 RSU Gabon - Programs App URLs
Fichier: apps/programs_app/urls.py
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProgramCategoryViewSet,
    SocialProgramViewSet,
    ProgramEnrollmentViewSet,
    PaymentViewSet
)

app_name = 'programs'

router = DefaultRouter()
router.register(r'categories', ProgramCategoryViewSet, basename='category')
router.register(r'programs', SocialProgramViewSet, basename='program')
router.register(r'enrollments', ProgramEnrollmentViewSet, basename='enrollment')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]