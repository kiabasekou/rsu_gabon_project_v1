"""
🇬🇦 RSU Gabon - Programs App Config
Fichier: apps/programs_app/apps.py
"""

from django.apps import AppConfig


class ProgramsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.programs_app'
    verbose_name = 'Gestion des Programmes Sociaux'