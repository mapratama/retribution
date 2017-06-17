import os
import sys

FILE_PATH = os.path.abspath(os.path.split(__file__)[0])
PROJECT_PATH = '/'.join(FILE_PATH.split('/')[:-2])
sys.path.append(PROJECT_PATH)

from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.db import models
from south.models import MigrationHistory


"""
This script checks for apps which does not currently have migrations
(usually occurs when a new app is added after initial deployment).
"""

apps_with_models = []
for app in models.get_apps():
    name = app.__name__
    if (not name.startswith('django.contrib') and not name.startswith('south')):
        if models.get_models(app):
            apps_with_models.append(name.split('.')[-2])


apps_with_migrations = MigrationHistory.objects \
                           .values_list('app_name', flat=True).annotate()

print '{% output %}'
for app in apps_with_models:
    if app not in apps_with_migrations:
        print app
