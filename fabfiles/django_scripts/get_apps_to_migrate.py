import os
import sys

FILE_PATH = os.path.abspath(os.path.split(__file__)[0])
PROJECT_PATH = '/'.join(FILE_PATH.split('/')[:-2])
sys.path.append(PROJECT_PATH)

from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.db import models


"""
This script returns apps for which we need to migrate.
"""
apps = models.get_apps()
for app in apps:
    if (not app.__name__.startswith('django.contrib') and
    	not app.__name__.startswith('south.')):
        if models.get_models(app):
            # app.__name__ gives us the full path of models.py
            # e.g emencia.django.newsletter.models . We need to 
            # strip out the "models" to get the full app name
            print '.'.join(app.__name__.split('.')[:-1])