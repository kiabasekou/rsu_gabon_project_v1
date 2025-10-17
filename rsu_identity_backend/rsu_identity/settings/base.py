"""
🇬🇦 RSU Gabon - Configuration Django Base (Windows Compatible)
Standards Top 1% - Sécurité & Performance
"""
import os
from pathlib import Path

DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-rsu-gabon-secret-key-windows-2024')

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent



# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
]

LOCAL_APPS = [
    'apps.core_app',
    'apps.identity_app', 
    'apps.programs_app',
    'apps.surveys',
    'apps.family_graph',
    'apps.deduplication', 
    'apps.analytics',
    'apps.services_app',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rsu_identity.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rsu_identity.wsgi.application'

# Database par défaut (sera surchargée dans development.py)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'  # Français pour le Gabon
TIME_ZONE = 'Africa/Libreville'  # Fuseau horaire Gabon
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'rsu_identity' / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': '🇬🇦 RSU Gabon API',
    'DESCRIPTION': 'Registre Social Unifié - APIs Gouvernementales',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Cache par défaut (sera surchargée dans chaque environnement)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'rsu-cache',
    }
}

# Logging Configuration Windows-friendly
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
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

# Données spécifiques Gabon
GABON_PROVINCES = [
    'ESTUAIRE', 'HAUT_OGOOUE', 'MOYEN_OGOOUE', 'NGOUNIE',
    'NYANGA', 'OGOOUE_IVINDO', 'OGOOUE_LOLO', 'OGOOUE_MARITIME', 
    'WOLEU_NTEM'
]

GABON_PHONE_REGEX = r'^\+241[0-9]{8}$'
RSU_ID_PREFIX = 'RSU-GA-'
# Modèle utilisateur personnalisé

AUTH_USER_MODEL = 'core_app.RSUUser'


# Ajout à la fin du fichier base.py

# API Documentation avec Spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': '🇬🇦 RSU Gabon API',
    'DESCRIPTION': 'Registre Social Unifié - APIs Gouvernementales\n\n'
                  'Système de gestion des identités et programmes sociaux du Gabon.\n'
                  'Financé par la Banque Mondiale dans le cadre du Projet Digital Gabon.\n\n'
                  '**Authentification requise** : JWT Token\n'
                  '**Permissions** : Basées sur le type d\'utilisateur (ADMIN, SUPERVISOR, SURVEYOR, etc.)',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'DEFAULT_GENERATOR_CLASS': 'drf_spectacular.generators.SchemaGenerator',
    
    # Personnalisation interface
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'defaultModelsExpandDepth': 2,
    },
    
    # Métadonnées projet
    'CONTACT': {
        'name': 'Équipe RSU Gabon',
        'email': 'support@rsu.gouv.ga'
    },
    'LICENSE': {
        'name': 'Gouvernement du Gabon',
    },
    
    # Tags pour organisation
    'TAGS': [
        {
            'name': 'Core',
            'description': 'Gestion des utilisateurs et audit system'
        },
        {
            'name': 'Identity', 
            'description': 'Identités personnelles et ménages'
        },
        {
            'name': 'Programs',
            'description': 'Programmes sociaux et bénéficiaires'
        }
    ]
}

# CORS pour développement mobile
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",  # React Native Metro
        "http://localhost:8081",  # Expo Dev
        "http://127.0.0.1:3000",
        "exp://localhost:19000",  # Expo
    ]
else:
    CORS_ALLOWED_ORIGINS = [
        "https://rsu-mobile.gouv.ga",
        "https://dashboard.rsu.gouv.ga",
    ]

# Pagination par défaut
REST_FRAMEWORK['PAGE_SIZE'] = 50

# Rate limiting pour production
if not DEBUG:
    REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ]
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
        'anon': '100/hour',
        'user': '1000/hour'
    }
