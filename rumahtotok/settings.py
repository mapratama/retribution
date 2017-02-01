"""
Django settings for rumahtotok project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from os import path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(SETTINGS_DIR)
PROJECT_NAME = os.path.basename(PROJECT_ROOT)
BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'static_files/bower')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u)d*3gv-l1o0$6uo9&o-46gzjwxwh28*!8y$obo69ed_o2&kle'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
PREPARE_DURATION = 30
ALLOWED_HOSTS = ['*']
HOST = 'http://rumahtotok.com'
FIXTURE_DIRS = ['fixtures']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'djangobower',
    'django_extensions',
    'compressor',
    'django_rq',
    'thumbnails',

    'rumahtotok.apps.banners',
    'rumahtotok.apps.bookings',
    'rumahtotok.apps.logs',
    'rumahtotok.apps.orders',
    'rumahtotok.apps.payments',
    'rumahtotok.apps.services',
    'rumahtotok.apps.promotions',
    'rumahtotok.apps.stores',
    'rumahtotok.apps.therapists',
    'rumahtotok.apps.treatments',
    'rumahtotok.apps.users',
    'rumahtotok.apps.balance_updates',
]

# Untuk membantu model users
AUTH_USER_MODEL = 'users.User'

# Default
MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Default
ROOT_URLCONF = 'rumahtotok.urls'

# Default
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
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

# Default
WSGI_APPLICATION = 'rumahtotok.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_L10N = True

USE_TZ = True

GOOGLE_API_KEY = "AIzaSyDLqU_kLNjAfKa4Juax-27J1_eoo28kUGg"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
# Example: "http://media.lawrence.com/static/"

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = path.join(PROJECT_ROOT, 'media')

STATIC_ROOT = SETTINGS_DIR + '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    path.join(PROJECT_ROOT, 'static_files'),
)


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',  # add this
    'djangobower.finders.BowerFinder',
)

COMPRESS_ENABLED = True

# untuk minify
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter',
                        'compressor.filters.cssmin.CSSMinFilter']
COMPRESS_URL = STATIC_URL

# Libasas settings for scss
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

BOWER_INSTALLED_APPS = (
    'datetimepicker',
    'typeahead.js',
    'fengyuanchen/viewerjs'
)

JPEGTRAN_COMMAND = "jpegtran -copy none -progressive -optimize -outfile '%(filename)s'.diet "\
                   "'%(filename)s' && mv '%(filename)s.diet' '%(filename)s'"

STANDARD_POST_PROCESSORS = [{'PATH': 'thumbnails.post_processors.optimize',
                             'png_command': 'optipng -force -o3 %(filename)s',
                             'jpg_command': JPEGTRAN_COMMAND}]

THUMBNAILS = {
    'METADATA': {
        'PREFIX': 'thumbs',
        'BACKEND': 'thumbnails.backends.metadata.RedisBackend',
        'db': 2
    },
    'STORAGE': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage'
    },
    'BASE_DIR': 'thumb',
    'SIZES': {
        'size_800': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 800, 'height': 800, 'method': 'fill'},
                {'PATH': 'thumbnails.processors.crop', 'width': 800, 'height': 800},
            ],
            'POST_PROCESSORS': STANDARD_POST_PROCESSORS
        },
        'size_500': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 500, 'height': 500, 'method': 'fill'},
                {'PATH': 'thumbnails.processors.crop', 'width': 500, 'height': 500},
            ],
            'POST_PROCESSORS': STANDARD_POST_PROCESSORS
        },
        'size_400': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 250, 'height': 400, 'method': 'fill'}
            ],
            'POST_PROCESSORS': STANDARD_POST_PROCESSORS
        },
        'size_90': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 90, 'height': 90, 'method': 'fill'},
                {'PATH': 'thumbnails.processors.crop', 'width': 90, 'height': 90},
            ],
            'POST_PROCESSORS': STANDARD_POST_PROCESSORS
        },
        'source_300': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 300, 'height': 300, 'method': 'fill'},
                {'PATH': 'thumbnails.processors.crop', 'width': 300, 'height': 300},
            ],
        },
        'resize_300': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 300, 'height': 300, 'method': 'fill'},
            ],
        },
        'source_3000': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 3000, 'height': 3000, 'method': 'fill'},
                {'PATH': 'thumbnails.processors.crop', 'width': 3000, 'height': 3000},
            ],
        },
    }
}

MINIMUM_PAYMENT = 0.5

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0',
        'TIMEOUT': None,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0
    }
}

RQ = {
    'AUTOCOMMIT': False,
}

# save session to database
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 62208000

if 'test' in os.sys.argv:
    TEST = True
else:
    TEST = False

try:
    from settings_local import *  # noqa
except ImportError:
    pass

