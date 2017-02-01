from django.core.management.base import BaseCommand

from libraries.migration_utils import migrations


class Command(BaseCommand):
    """A simple management command that returns "yes" if there are
    some migrations that are not yet applied."""

    def handle(self, *args, **options):
        unapplied_migrations = migrations.unapplied()
        if unapplied_migrations:
            print unapplied_migrations
        else:
            print "no"
