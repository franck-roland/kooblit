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
import sys
sys.stderr.write('\n'.join(sorted(sys.path)) + '\n')

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

AMAZON_KEY = appConfig.get("amazon_key")
MONGO_PWD = appConfig.get("db__mongo__passwd")
MONGO_USER = appConfig.get("db__mongo__user")
PAYMILL_PRIVATE_KEY = appConfig.get("paymill__private")
PAYMILL_PUBLIC_KEY = appConfig.get("paymill__public")
PAYPLUG_PRIVATE_KEY = open(os.path.join(PROJECT_ROOT, appConfig.get("payplug__private")),'r').read()
PAYPLUG_PUBLIC_KEY = open(os.path.join(PROJECT_ROOT, appConfig.get("payplug__public")),'r').read()
PAYPLUG_URL = appConfig.get("payplug__url")


TMP_DIR = appConfig.get("tmp__kooblit_tmp_root")
connect('docs_db', username=MONGO_USER, password=MONGO_PWD)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
USE_BUCKET = False
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

SECRET_KEY = appConfig.get("secret_key")

# Synthese settings
MIN_NOTE = 3
MIN_MEAN = 3
if DEBUG:
    TIME_TO_WAIT = 1
else:
    TIME_TO_WAIT = 12 * 3600


if not DEBUG:   
    ALLOWED_HOSTS = [
    '.kooblit.com', # Allow domain and subdomains
    '127.0.0.1', # Also allow FQDN and subdomains
    '37.187.66.54',
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
if USE_BUCKET:
    AWS_STORAGE_BUCKET_NAME = appConfig.get("aws__bucket_name")
    # if DO_COLLECT:
    AWS_ACCESS_KEY_ID = appConfig.get("aws__ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = appConfig.get("aws__SECRET_ACCESS_KEY")
    DEFAULT_FILE_STORAGE = 'kooblit.s3utils.MediaRootS3BotoStorage'
#    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    STATICFILES_STORAGE = 'kooblit.s3utils.StaticRootS3BotoStorage'
    S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
    STATIC_URL = S3_URL + 'static/'
    MEDIA_URL = S3_URL + 'media/'
    if not DEBUG:
        MEDIA_URL += 'prod/'
else:
    DEFAULT_FILE_STORAGE = 'usr_management.utils.MyFileStorage'
    STATIC_URL = '/static/'
    MEDIA_ROOT = appConfig.get("path__media_root")
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

# debug_toolbar settings
if DEBUG:
    INTERNAL_IPS = ('0.0.0.0', '90.2.65.14')
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    INSTALLED_APPS += (
        'debug_toolbar',
    )

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
