# rsu_identity/settings/production.py
from .development import *
import os
import dj_database_url

# Override settings for production
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key-change-me')

# Hosts Railway
ALLOWED_HOSTS = [
    '.railway.app',
    'rsu-gabon-backend.railway.app',
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
    "https://rsu-gabon-backend.railway.app",
    "http://localhost:19000",
    "http://192.168.1.69:19000",
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')