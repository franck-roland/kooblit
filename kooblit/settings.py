"""
Django settings for kooblit project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import yaml
from slugify import Slugify
from mongoengine import connect


PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
config = yaml.load(open(os.path.join(PROJECT_ROOT, "config", "config.yml"), "r").read())

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
AMAZON_KEY = config["AMAZON_KEY"]
MONGO_PWD = config["MONGO_PWD"]
MONGO_USER = config["MONGO_USER"]
PAYMILL_PRIVATE_KEY = config["PAYMILL_PRIV"]
PAYMILL_PUBLIC_KEY = config["PAYMILL_PUB"]

connect('docs_db', username=MONGO_USER, password=MONGO_PWD)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SLUGIFY BOOKS TITLE
BOOKS_SLUG = Slugify(to_lower=True)
BOOKS_SLUG.separator = ' '

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

SECRET_KEY = config["SECRET_KEY"]

# Application definition

INSTALLED_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'search_engine',
    'usr_management',
    'achat',
    'south',
    'crispy_forms',
)

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
        'NAME': 'kooblit_db',
        'USER': 'endoderconic',
        'PASSWORD': config['DB_PASSWORD'],
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
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)
STATIC_URL = '/static/'
STATIC_ROOT = '/tmp/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates/'),
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
EMAIL_HOST = config['EMAIL_HOST']
EMAIL_HOST_PASSWORD = config['EMAIL_HOST_PASSWORD']
EMAIL_HOST_USER = config['EMAIL_HOST_USER']
EMAIL_USE_TLS = True
EMAIL_PORT = 587

# INTERNE
MAX_BOOK_TITLE_LEN = 1024

MEDIA_ROOT = '/var/www/media'
