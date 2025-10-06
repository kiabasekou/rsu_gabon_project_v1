"""
🇬🇦 RSU Gabon - Analytics URLs
Routes pour module Analytics
"""
from django.urls import path
from .views import DashboardStatsAPIView, ProvinceStatsAPIView

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),
    path('province-stats/', ProvinceStatsAPIView.as_view(), name='province-stats'),
]