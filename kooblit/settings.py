"""
Django settings for kooblit project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
from mongoengine import connect
from kooblit_lib.config import appConfig
# import djcelery

# djcelery.setup_loader()

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

AMAZON_KEY = appConfig.get("amazon_key")
MONGO_PWD = appConfig.get("db__mongo__passwd")
MONGO_USER = appConfig.get("db__mongo__user")
PAYMILL_PRIVATE_KEY = appConfig.get("paymill__private")
PAYMILL_PUBLIC_KEY = appConfig.get("paymill__public")
TMP_DIR = appConfig.get("tmp__kooblit_tmp_root")
connect('docs_db', username=MONGO_USER, password=MONGO_PWD)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

SECRET_KEY = appConfig.get("secret_key")

# Synthese settings
MIN_NOTE = 3
MIN_MEAN = 3

if not DEBUG:   
    ALLOWED_HOSTS = [
    '.kooblit.com', # Allow domain and subdomains
    '127.0.0.1', # Also allow FQDN and subdomains
    ]



# Application definition
INSTALLED_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'search_engine',
    'usr_management',
    'achat',
    'manage_books_synth',
    'south',
    'crispy_forms',
)
INSTALLED_APPS += ('storages',)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'achat.middleware.CartMiddleware',
)


ROOT_URLCONF = 'kooblit.urls'

WSGI_APPLICATION = 'kooblit.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': appConfig.get("db__psql__name"),
        'USER': appConfig.get("db__psql__user"),
        'PASSWORD': appConfig.get("db__psql__passwd"),
        'HOST': appConfig.get("db__psql__HOST"),
        'PORT': appConfig.get("db__psql__PORT"),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
AUTH_PROFILE_MODULE = "usr_management.UserKooblit"

LANGUAGE_CODE = 'fr-FR'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
DO_COLLECT = False
if not DEBUG:
    AWS_STORAGE_BUCKET_NAME = appConfig.get("aws__bucket_name")
    # if DO_COLLECT:
    AWS_ACCESS_KEY_ID = appConfig.get("aws__ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = appConfig.get("aws__SECRET_ACCESS_KEY")
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
    STATIC_URL = S3_URL
else:
    STATIC_URL = '/static/'

STATIC_ROOT = appConfig.get("path__static_root")

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates/'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages"
)

AUTHENTICATION_BACKENDS = (
    'usr_management.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend'
)
EMAIL_HOST = appConfig.get("email__host")
EMAIL_HOST_PASSWORD = appConfig.get("email__passwd")
EMAIL_HOST_USER = appConfig.get("email__user")
EMAIL_USE_TLS = True
EMAIL_PORT = 587

# INTERNE
MAX_BOOK_TITLE_LEN = 1024

MEDIA_ROOT = appConfig.get("path__media_root")
