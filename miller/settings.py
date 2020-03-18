"""
Django settings for miller project.

Generated by 'django-admin startproject' using Django 3.0.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from .base import get_env_variable

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('SECRET_KEY', 'secret key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env_variable('DEBUG', True) == 'True'

ALLOWED_HOSTS = get_env_variable('ALLOWED_HOSTS', 'localhost').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'miller',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'miller.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'miller.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_variable('MILLER_DATABASE_NAME'),
        'USER': get_env_variable('MILLER_DATABASE_USER'),
        'PASSWORD': get_env_variable('MILLER_DATABASE_PASSWORD'),
        'HOST': get_env_variable('MILLER_DATABASE_HOST', 'localhost'),
        'PORT': get_env_variable('MILLER_DATABASE_PORT', '54320'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'formatters': {
        'verbose': {
            # 'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            'format': '{levelname} {asctime} - {name:s} L{lineno:d}: {message}',
            'style': '{',
        },
    },
}

# MILLER
# Additional type choices for Document Model: must be a tuple
MILLER_DOCUMENT_TYPE_CHOICES = tuple()
# Additional category choices for Tag Model: must be a tuple
MILLER_TAG_CATEGORY_CHOICES = tuple()
# search vectors fileds in JSON data, with weight
MILLER_VECTORS_MULTILANGUAGE_FIELDS = (('title', 'A'), ('description', 'B'))
MILLER_VECTORS_INITIAL_FIELDS = (('title', 'A', 'simple'),) # ('slug', 'A', 'simple'))
# JSON Schema
MILLER_SCHEMA_ROOT = get_env_variable('MILLER_SCHEMA_ROOT', '/schema')
MILLER_SCHEMA_ENABLE_VALIDATION = get_env_variable('MILLER_SCHEMA_ENABLE_VALIDATION', True)
# Current version
MILLER_GIT_BRANCH = get_env_variable('MILLER_GIT_BRANCH', 'nd')
MILLER_GIT_REVISION = get_env_variable('MILLER_GIT_REVISION', 'nd')


# Celery
REDIS_HOST=get_env_variable('REDIS_HOST', 'localhost')
REDIS_PORT=get_env_variable('REDIS_PORT', '63790')
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/4'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/5'
CELERYD_PREFETCH_MULTIPLIER = 2
CELERYD_CONCURRENCY = 2

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = get_env_variable('STATIC_URL', '/static/')
STATIC_ROOT = get_env_variable('STATIC_ROOT', '/static')
STATICFILES_DIRS = [
    # ...
    ('schema', MILLER_SCHEMA_ROOT),
]

MEDIA_URL = get_env_variable('MEDIA_URL', '/media/')
MEDIA_ROOT = get_env_variable('MEDIA_ROOT', '/static')
