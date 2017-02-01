import sys

import django
from django.core.management.base import BaseCommand
from django.utils.log import getLogger


if django.VERSION[:2] == (1, 4):

    class LoggingBaseCommand(BaseCommand):
        # A subclass of BaseCommand that logs errors to django.commands

        def __init__(self):
            super(LoggingBaseCommand, self).__init__()
            self._logger = getLogger('django.commands')

        def run_from_argv(self, argv):
            try:
                super(LoggingBaseCommand, self).run_from_argv(argv)
            except Exception, e:
                self._logger.error(e,
                    exc_info=sys.exc_info(),
                    extra={
                        'status_code': 500,
                    }
                )
                raise


else:
    class LoggingBaseCommand(BaseCommand):

        def run_from_argv(self, argv):
            raise NotImplementedError
