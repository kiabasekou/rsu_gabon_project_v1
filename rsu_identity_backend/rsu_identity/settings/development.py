"""
🇬🇦 RSU Gabon - Configuration Développement
Standards Top 1% - Debug & Développement
MISE À JOUR: CORS optimisé pour Dashboard React
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', '0.0.0.0']

# Base de données SQLite pour développement local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ✅ CORS CONFIGURATION OPTIMISÉE POUR DASHBOARD REACT
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # React Development Server
    "http://127.0.0.1:3000",      # Alternative localhost
    "http://localhost:8081",      # Expo (Mobile)
    "http://localhost:19000",     # Expo Dev Tools
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Debug Toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]

# Email backend pour tests
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuration logs optimisée
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
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console'],
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

print("✅ RSU Gabon - Mode DÉVELOPPEMENT activé")
print(f"✅ CORS configuré pour: {', '.join(CORS_ALLOWED_ORIGINS)}")