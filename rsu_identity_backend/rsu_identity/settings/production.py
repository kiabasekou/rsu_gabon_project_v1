# =============================================================================
# 🇬🇦 RSU GABON - SETTINGS PRODUCTION (Django 5.0 Compatible)
# Standards Top 1% - Configuration Railway Optimisée
# =============================================================================
import os
import sys
import dj_database_url
from .base import *

# =============================================================================
# 1. SÉCURITÉ & DEBUG
# =============================================================================
DEBUG = False

# Secret Key avec fallback pour collectstatic pendant le build Docker
SECRET_KEY = os.environ.get('SECRET_KEY', 'temp-build-key-for-collectstatic-only')

# Validation stricte uniquement si on n'est PAS en train de faire collectstatic
if 'collectstatic' not in sys.argv:
    if not os.environ.get('SECRET_KEY') or SECRET_KEY == 'temp-build-key-for-collectstatic-only':
        raise ValueError(
            "❌ SECRET_KEY manquante en production!\n"
            "   Définissez la variable d'environnement SECRET_KEY sur Railway."
        )

# =============================================================================
# 2. HOSTS AUTORISÉS
# =============================================================================
ALLOWED_HOSTS = [
    '.railway.app',
    '.up.railway.app',
    'rsu-gabon.railway.app',
    'localhost',
    '127.0.0.1'
]

# Affichage de confirmation
print("✅ RSU Gabon - Mode PRODUCTION activé")
print(f"✅ ALLOWED_HOSTS: {ALLOWED_HOSTS}")

# =============================================================================
# 3. DATABASE - POSTGRESQL (Railway)
# =============================================================================
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    print("✅ DATABASE: PostgreSQL")
else:
    # Fallback pour collectstatic pendant le build (ne sera jamais utilisé en runtime)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/temp-build-db.sqlite3',
        }
    }
    if 'collectstatic' not in sys.argv:
        print("⚠️  WARNING: DATABASE_URL non définie!")

# =============================================================================
# 4. STATIC & MEDIA FILES (Django 5.0 Syntax)
# =============================================================================
# ✅ NOUVELLE SYNTAXE Django 5.0+
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Configuration Whitenoise
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False
WHITENOISE_ALLOW_ALL_ORIGINS = False

print("✅ Static Files: Whitenoise (Compressed)")

# =============================================================================
# 5. CACHE - REDIS (si disponible)
# =============================================================================
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
            },
            'TIMEOUT': 300,
        }
    }
    print("✅ Cache: Redis activé")
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'rsu-production-cache',
        }
    }
    if 'collectstatic' not in sys.argv:
        print("✅ Cache: LocMem (Redis recommandé)")

# =============================================================================
# 6. CORS - CONFIGURATION MOBILE
# =============================================================================
CORS_ALLOWED_ORIGINS = [
    "https://rsu-gabon-backend-production.up.railway.app",
    "http://localhost:19000",
    "http://localhost:8081",
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

if 'collectstatic' not in sys.argv:
    print(f"✅ CORS Origins: {len(CORS_ALLOWED_ORIGINS)} autorisées")

# =============================================================================
# 7. LOGGING - RAILWAY OPTIMISÉ
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} - {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

if 'collectstatic' not in sys.argv:
    print("✅ Logging: Console configuré")

# =============================================================================
# 8. EMAIL - CONFIGURATION (À adapter selon provider)
# =============================================================================
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@rsu-gabon.ga')
    if 'collectstatic' not in sys.argv:
        print("✅ Email: SMTP configuré")
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    if 'collectstatic' not in sys.argv:
        print("✅ Email: Console")

# =============================================================================
# 9. SÉCURITÉ RENFORCÉE
# =============================================================================
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# =============================================================================
# 10. MONITORING & SENTRY (Optionnel)
# =============================================================================
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
    )
    if 'collectstatic' not in sys.argv:
        print("✅ Monitoring: Sentry activé")
else:
    if 'collectstatic' not in sys.argv:
        print("✅ Monitoring: Logs only")

# =============================================================================
# 11. PERFORMANCE
# =============================================================================
# Compression Gzip
if 'django.middleware.gzip.GZipMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(0, 'django.middleware.gzip.GZipMiddleware')

# Connection pooling
CONN_MAX_AGE = 600

# Session engine optimisé
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Message final uniquement si pas collectstatic
if 'collectstatic' not in sys.argv:
    print("\n" + "="*70)
    print("🇬🇦 RSU GABON BACKEND - PRODUCTION MODE READY")
    print("="*70 + "\n")