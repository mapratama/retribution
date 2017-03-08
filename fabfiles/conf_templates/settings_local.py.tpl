import settings
import os

PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])
MEDIA_ROOT = os.path.join(os.path.dirname(PROJECT_PATH.rstrip('/')), 'media')

#DEBUG = False
#TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

INSTALLED_APPS = list(settings.INSTALLED_APPS) + ['gunicorn']

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '%(db_name)s',                              # Or path to database file if using sqlite3.
        'USER': '%(db_user)s',                              # Not used with sqlite3.
        'PASSWORD': '%(db_pass)s',                          # Not used with sqlite3.
        'HOST': '127.0.0.1',                                # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                                     # Set to empty string for default. Not used with sqlite3.
        'CONN_MAX_AGE': 600,                                # Persistent connections, from django1.6
    }
}


#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.example.com'
#EMAIL_HOST_USER = 'user@example.com'
#EMAIL_HOST_PASSWORD = 'password'
#EMAIL_PORT = 587
#DEFAULT_FROM_EMAIL = 'from@example.com'
