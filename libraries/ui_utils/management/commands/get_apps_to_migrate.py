from django.conf import settings
from django.core.management.base import BaseCommand

from django.db import models

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        apps = models.get_apps()
        for app in apps:
            
            if not app.__name__.startswith('django.contrib'):
                if models.get_models(app):
                    print app.__name__.split('.')[0]
                    