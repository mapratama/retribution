from django_extensions.management.base import LoggingBaseCommand

from retribution.apps.retributions.utils import sync


class Command(LoggingBaseCommand):

    def handle(self, *args, **kwargs):
        sync()
