# rsu_identity/settings/production.py
import os
import dj_database_url
from .base import *

# Production overrides
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')

# Hosts Railway
ALLOWED_HOSTS = [
    '.railway.app',
    'rsu-gabon-backend-production.up.railway.app',
    'localhost',
    '127.0.0.1'
]

# Database Railway PostgreSQL
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get('DATABASE_URL'),
            conn_max_age=600,
        )
    }

# CORS pour mobile
CORS_ALLOWED_ORIGINS = [
    "https://rsu-gabon-backend-production.up.railway.app",
    "http://localhost:19000",
    "http://192.168.1.69:19000",
]

# Désactiver collectstatic si problème
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging simple pour Railway
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}