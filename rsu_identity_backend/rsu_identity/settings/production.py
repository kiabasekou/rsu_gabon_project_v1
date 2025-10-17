# rsu_identity/settings/production.py
from .development import *
import os
import dj_database_url

# Production overrides
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret')

ALLOWED_HOSTS = [
    '.railway.app',
    'localhost',
    '127.0.0.1'
]

# Database PostgreSQL Railway
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get('DATABASE_URL'),
            conn_max_age=600,
        )
    }

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://rsu-gabon-backend-production.railway.app",
    "http://localhost:19000",
    "http://192.168.1.69:19000",
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}