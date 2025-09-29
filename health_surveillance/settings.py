"""
Django settings for Smart Health Surveillance System.
"""

import os
from pathlib import Path
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'django-insecure-change-this-in-production'),
    REDIS_URL=(str, 'redis://localhost:6379/0'),
)

# Read .env file
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# Parse ALLOWED_HOSTS from environment variable
ALLOWED_HOSTS_STR = env('DJANGO_ALLOWED_HOSTS', default='*')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',
    'drf_spectacular',
    'django_celery_beat',
    'django_celery_results',
    'pwa',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.geography',
    'apps.health',
    'apps.water_quality',
    'apps.ml_models',
    'apps.alerts',
    'apps.reports',
    'apps.api',
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

ROOT_URLCONF = 'health_surveillance.urls'

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

WSGI_APPLICATION = 'health_surveillance.wsgi.application'
ASGI_APPLICATION = 'health_surveillance.asgi.application'

# Database
# Use SpatiaLite (SQLite with spatial extensions) to support GIS fields locally.
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': str(BASE_DIR / 'db.sqlite3'),
    }
}

# Path to the SpatiaLite library. On many Linux systems this is 'mod_spatialite'.
# You may need to adjust based on your environment (e.g., 'mod_spatialite.so').
SPATIALITE_LIBRARY_PATH = env('SPATIALITE_LIBRARY_PATH', default='mod_spatialite')

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000", 
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    # Remove the "*" as it's invalid
]

# If you need to allow all origins (not recommended for production),
# use CORS_ALLOW_ALL_ORIGINS instead:
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        }
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Channels Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [env('REDIS_URL')],
        },
    },
}

# Celery Configuration
CELERY_BROKER_URL = env('REDIS_URL')

# CSRF Settings
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://192.168.1.5:8080',
    'http://0.0.0.0:8080',
    'https://*.up.railway.app',
])

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='dhaked.7248@gmail.com')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='ihpd pwrf vldy ntbf')
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'Smart Health Surveillance <dhaked.7248@gmail.com>'

# SMS/WhatsApp Configuration
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID', default='AC04bd70da4acea4bc586b30fd0a06460b')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN', default='6ea6b18f18c43747b6630ea334d81c13')
TWILIO_PHONE_NUMBER = env('TWILIO_PHONE_NUMBER', default='+16812026553')

# ML Model Configuration
ML_MODEL_PATH = BASE_DIR / 'ml_models'
ML_MODEL_UPDATE_INTERVAL = 24  # hours

# Alert Configuration
ALERT_THRESHOLDS = {
    'OUTBREAK_PROBABILITY': 0.7,
    'WATER_CONTAMINATION': 0.8,
    'MULTIPLE_CASES': 5,
    'SEASONAL_HIGH_RISK': 0.6,
}

# User Roles
USER_ROLES = [
    'ASHA_WORKER',
    'CLINIC_STAFF',
    'DISTRICT_OFFICER',
    'STATE_ADMIN',
    'SYSTEM_ADMIN'
]

# Disease Types
DISEASE_TYPES = [
    'CHOLERA',
    'TYPHOID',
    'HEPATITIS_A',
    'DIARRHEA',
    'DYSENTERY',
    'OTHER'
]

# Alert Types
ALERT_TYPES = [
    'OUTBREAK_PREDICTED',
    'WATER_CONTAMINATION',
    'MULTIPLE_CASES',
    'SEASONAL_HIGH_RISK',
    'SYSTEM_FAILURE'
]

# Progressive Web App (PWA) Configuration
# These settings are used by django-pwa to generate the manifest and wire the service worker
PWA_APP_NAME = 'Cloudburst Alert System'
PWA_APP_SHORT_NAME = 'Cloudburst'
PWA_APP_DESCRIPTION = 'Installable web app for real-time cloudburst alerts and health surveillance.'
PWA_APP_THEME_COLOR = '#1976d2'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'  # app-like, hides browser UI
PWA_APP_SCOPE = '/'
PWA_APP_START_URL = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'en-US'

# Offline page template rendered when network is unavailable
PWA_APP_OFFLINE_TEMPLATE = 'pwa_offline.html'

# Icons to be shown on Android/Chrome and Apple devices
PWA_APP_ICONS = [
    {
        'src': '/static/icons/icon-192x192.png',
        'sizes': '192x192'
    },
    {
        'src': '/static/icons/icon-512x512.png',
        'sizes': '512x512'
    },
]

PWA_APP_ICONS_APPLE = [
    {
        'src': '/static/icons/icon-192x192.png',
        'sizes': '192x192'
    },
]

# Explicit path to the service worker in static files
PWA_SERVICE_WORKER_PATH = BASE_DIR / 'static' / 'service-worker.js'

# Optional: turn on extra logging for PWA in development
PWA_APP_DEBUG_MODE = DEBUG