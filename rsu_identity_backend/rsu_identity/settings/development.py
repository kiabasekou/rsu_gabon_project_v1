"""
🇬🇦 RSU Gabon - Configuration Développement
Standards Top 1% - Debug & Développement
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Base de données SQLite pour développement local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Debug Toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]

# CORS permissif pour développement  
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React Native Metro
    "http://localhost:8081",  # Expo
    "http://127.0.0.1:3000",
]

CORS_ALLOW_ALL_ORIGINS = True  # Uniquement en développement

# Email backend pour tests
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuration logs Windows-friendly
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'rsu_backend.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Cache simple en mémoire pour développement
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'rsu-dev-cache',
    }
}