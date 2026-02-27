"""
Django settings for SafePulseUg project.
"""

import environ
import os
import dj_database_url
from pathlib import Path
from datetime import timedelta

# ─────────────────────────────────────────────────────────────
# BASE DIRECTORY
# ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────────────────────
# LOAD ENVIRONMENT VARIABLES FROM .env
# ─────────────────────────────────────────────────────────────
env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / '.env')


# ─────────────────────────────────────────────────────────────
# CORE SECURITY SETTINGS
# ─────────────────────────────────────────────────────────────
SECRET_KEY    = env('SECRET_KEY')
DEBUG         = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])


# ─────────────────────────────────────────────────────────────
# INSTALLED APPS
# ─────────────────────────────────────────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_celery_results',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.crimes',
    'apps.analysis',
    'apps.reports',
    'apps.dashboard',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ─────────────────────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────
# URL & WSGI
# ─────────────────────────────────────────────────────────────
ROOT_URLCONF     = 'SafePulseUg.urls'
WSGI_APPLICATION = 'SafePulseUg.wsgi.application'


# ─────────────────────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────
# DATABASE — Supabase PostgreSQL
# ─────────────────────────────────────────────────────────────
DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    )
}


# ─────────────────────────────────────────────────────────────
# CUSTOM USER MODEL
# ─────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.OfficerUser'


# ─────────────────────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':    'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ─────────────────────────────────────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Africa/Kampala'
USE_I18N      = True
USE_TZ        = True


# ─────────────────────────────────────────────────────────────
# STATIC & MEDIA FILES
# ─────────────────────────────────────────────────────────────
STATIC_URL       = '/static/'
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ─────────────────────────────────────────────────────────────
# DEFAULT PRIMARY KEY
# ─────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ─────────────────────────────────────────────────────────────
# DJANGO REST FRAMEWORK
# ─────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


# ─────────────────────────────────────────────────────────────
# JWT CONFIGURATION
# ─────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(
        minutes=env.int('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=env.int('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7)
    ),
    'ROTATE_REFRESH_TOKENS':    True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN':        True,
    'AUTH_HEADER_TYPES':        ('Bearer',),
    'AUTH_TOKEN_CLASSES':       ('rest_framework_simplejwt.tokens.AccessToken',),
}


# ─────────────────────────────────────────────────────────────
# CORS CONFIGURATION
# ─────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
])

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

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


# ─────────────────────────────────────────────────────────────
# CELERY CONFIGURATION
# ─────────────────────────────────────────────────────────────
CELERY_BROKER_URL         = env('CELERY_BROKER_URL',     default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND     = env('CELERY_RESULT_BACKEND', default='django-db')
CELERY_ACCEPT_CONTENT     = ['json']
CELERY_TASK_SERIALIZER    = 'json'
CELERY_RESULT_SERIALIZER  = 'json'
CELERY_TIMEZONE           = 'Africa/Kampala'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT    = 30 * 60


# ─────────────────────────────────────────────────────────────
# GROQ AI — PRIMARY (Free, Fast, Llama 3.3)
# ─────────────────────────────────────────────────────────────
GROQ_API_KEY = env('GROQ_API_KEY', default='')
GROQ_MODEL   = env('GROQ_MODEL',   default='llama-3.3-70b-versatile')

# ─────────────────────────────────────────────────────────────
# GOOGLE GEMINI AI — BACKUP
# ─────────────────────────────────────────────────────────────
# GEMINI_API_KEY = env('GEMINI_API_KEY', default='')
# GEMINI_MODEL   = env('GEMINI_MODEL',   default='gemini-2.0-flash-lite')


# ─────────────────────────────────────────────────────────────
# DRF SPECTACULAR — API DOCUMENTATION
# ─────────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE':       'SafePulse UG API',
    'DESCRIPTION': '''
## 🛡️ SafePulse UG — AI-Powered Crime Analysis System
**Uganda Police Force Crime Analysis & Reporting API**

### Features:
- 🔐 Officer Authentication (JWT)
- 🚔 Crime Reporting & Management
- 🤖 AI Agent Crime Analysis (Groq — Llama 3.3 70B)
- 📄 PDF & Excel Report Generation
- 📊 Dashboard Statistics & Charts

### Authentication:
All endpoints (except login/register) require a **Bearer JWT token**.
Use `/api/auth/login/` to get your token, then click **Authorize 🔒**
and enter: `Bearer <your_access_token>`
    ''',
    'VERSION':              '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX':   '/api/',
    'CONTACT': {
        'name':  'SafePulse UG Dev Team',
        'email': 'dev@safepulse.ug',
    },
    'LICENSE': {
        'name': 'Uganda Police Force — Internal Use Only',
    },
    'SWAGGER_UI_SETTINGS': {
        'deepLinking':              True,
        'persistAuthorization':     True,
        'displayOperationId':       False,
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth':  2,
        'docExpansion':             'list',
        'filter':                   True,
        'showExtensions':           True,
    },
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
        'expandResponses':    '200,201',
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS':         False,
}


# ─────────────────────────────────────────────────────────────
# LOGGING — Console only (works on Render & locally)
# ─────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} | {module} | {message}',
            'style':  '{',
        },
    },

    'handlers': {
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },

    'loggers': {
        'django': {
            'handlers':  ['console'],
            'level':     'INFO',
            'propagate': True,
        },
        'apps.accounts': {
            'handlers':  ['console'],
            'level':     'DEBUG',
            'propagate': False,
        },
        'apps.crimes': {
            'handlers':  ['console'],
            'level':     'DEBUG',
            'propagate': False,
        },
        'apps.analysis': {
            'handlers':  ['console'],
            'level':     'DEBUG',
            'propagate': False,
        },
        'apps.reports': {
            'handlers':  ['console'],
            'level':     'DEBUG',
            'propagate': False,
        },
        'apps.dashboard': {
            'handlers':  ['console'],
            'level':     'DEBUG',
            'propagate': False,
        },
    },
}