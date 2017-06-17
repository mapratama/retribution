from fabric.api import env, run, sudo, prompt
from fabric.context_managers import cd, hide, settings


def create_initial_migration():
    with cd(env.SRC_PATH):
        apps = run('%s fabfiles/django_scripts/get_apps_to_migrate.py' %
                   env.PYTHON_BIN).split('\n')
        with settings(warn_only=True):
            for app in apps:
                if app != 'south':
                    sudo("%s manage.py schemamigration %s --initial" %
                         (env.PYTHON_BIN, app.strip()))


def check_migration_type():
    with cd(env.TEMP_SRC_PATH):
        result = run('%s manage.py has_unapplied_migrations' % env.PYTHON_BIN)
        if result != 'no':
            # Prompt user for what they want to do
            print '\nSchema migrations detected. What did the migrations do?'
            print '[1] Adds a field. Perform migration before updating source code.'
            print '[2] Removes a field. Will update source code before migration.'
            print '[3] Other. Perform migration before updating source code.'
            print '[4] Other. Update source code before performing migration.\n'

            while True:
                choice = prompt('Choose [1, 2, 3 or 4]: ', validate=int)
                if choice in range(1, 5):
                    break

            if choice == 1 or choice == 3:
                return "migrate_then_update_source"
            if choice == 2 or choice == 4:
                return "update_source_then_migrate"
        else:
            return None


def migrate(path=None):
    path = env.SRC_PATH if path is None else path
    with cd(path):
        sudo("%s manage.py migrate" % env.PYTHON_BIN)


def create_automatic_migration():
    """
    Runs south schemamigration on all apps returned by "get_apps_to_migrate".
    Each schema migration is run with "--auto" flag
    """
    with cd(env.SRC_PATH):
        apps = run('%s fabfiles/django_scripts/get_apps_to_migrate.py' %
                   env.PYTHON_BIN).split('\n')
        with settings(hide('warnings'), warn_only=True):
            for app in apps:
                output = sudo('%s manage.py schemamigration %s --auto' %
                              (env.PYTHON_BIN, app.strip()))

                # Raise any error other than nothing seems to have changed
                if output.failed:
                    if not 'Nothing seems to have changed' in output:
                        raise Exception('Error when running automated schema migration')


def migrate_new_apps():
    """
    Gets a list of apps that doesn't yet have migration from
    "get_apps_without_migration" script and then initializes migration for each.
    """
    new_apps = run('%s %s/fabfiles/django_scripts/get_apps_without_migration.py'
                   % (env.PYTHON_BIN, env.SRC_PATH))
    # The script denotes the start of its output by "{% output %}" tag so we
    # only take whatever's after that
    new_apps = new_apps.split('{% output %}')[1].split()
    with cd(env.SRC_PATH):
        for app in new_apps:
            sudo("%s manage.py schemamigration %s --initial" %
                 (env.PYTHON_BIN, app.strip()))
            sudo("%s manage.py migrate %s  --no-initial-data" %
                 (env.PYTHON_BIN, app.strip()))
