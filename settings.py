import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-facility-key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'rest_framework', 'rest_framework_simplejwt', 'corsheaders', 'drf_spectacular', 'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'common.auth.JWTStubMiddleware',
]

ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True,
              'OPTIONS': {'context_processors': ['django.template.context_processors.request',
                          'django.contrib.auth.context_processors.auth',
                          'django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'config.wsgi.application'

# Use PostgreSQL (RDS) whenever a DB host is provided (the ECS task def sets DB_HOST);
# otherwise fall back to SQLite for local dev. Previously postgres required
# DB_ENGINE=postgresql, which the ECS task def never set — so the catalog ran on ephemeral
# SQLite and was wiped on every redeploy.
_USE_POSTGRES = os.getenv('DB_ENGINE') == 'postgresql' or bool(os.getenv('DB_HOST'))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql' if _USE_POSTGRES else 'django.db.backends.sqlite3',
        'NAME': os.getenv('DB_NAME', 'facility_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
if not _USE_POSTGRES:
    DATABASES['default']['NAME'] = BASE_DIR / 'db.sqlite3'

LANGUAGE_CODE, TIME_ZONE, USE_I18N, USE_TZ = 'en-us', 'UTC', True, True
STATIC_URL, DEFAULT_AUTO_FIELD = 'static/', 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10, 'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {'ACCESS_TOKEN_LIFETIME': timedelta(hours=1), 'ALGORITHM': 'HS256', 'SIGNING_KEY': SECRET_KEY}
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS_ALLOW_ALL_ORIGINS = True

# ── AWS / LocalStack (S3 for doctor photos) ───────────────────────────────────
# All AWS calls go through common.aws.aws_client() which injects endpoint_url
# from AWS_ENDPOINT_URL, so traffic hits the local emulation, never real AWS.
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ENDPOINT_URL = os.getenv('AWS_ENDPOINT_URL') or None
STAFF_PHOTO_BUCKET = os.getenv('STAFF_PHOTO_BUCKET', 'isi-files')
# Host-reachable base used to build browser-renderable photo URLs.
S3_PUBLIC_URL = os.getenv('S3_PUBLIC_URL', 'http://localhost:4566')

# Shared secret for trusted inter-service calls (X-Internal-Token).
INTERNAL_SHARED_TOKEN = os.getenv('INTERNAL_SHARED_TOKEN', 'dev-internal-token')
