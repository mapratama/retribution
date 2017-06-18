import os

from fabric.api import env, run, local, sudo, prompt
from fabric.context_managers import cd, settings
from fabric.contrib.files import exists
from fabric.utils import abort

from migrations import migrate, check_migration_type
from webservers import setup_webserver

from fabtools import require, service, systemd


def setup_env(target_dir='retribution'):
    env.PROJECT_NAME = target_dir
    env.PROJECT_PATH = '/var/www/%s/' % env.PROJECT_NAME
    env.SRC_PATH = os.path.join(env.PROJECT_PATH, 'src')
    env.TEMP_SRC_PATH = os.path.join(env.PROJECT_PATH, 'temp')
    env.VIRTUALENV_DIR = os.path.join(env.PROJECT_PATH, 'env')
    env.PYTHON_BIN = os.path.join(env.VIRTUALENV_DIR, 'bin/python')
    env.PIP_BIN = os.path.join(env.VIRTUALENV_DIR, 'bin/pip')
    env.REQUIREMENTS_FILE = os.path.join(env.SRC_PATH, "requirements.txt")
    env.MANAGE_PATH = os.path.join(env.SRC_PATH, 'manage.py')
    env.MANAGE_BIN = '{0} {1}'.format(env.PYTHON_BIN, env.MANAGE_PATH)


def install_project_requirements(path_to_file=None):
    path_to_file = path_to_file or env.REQUIREMENTS_FILE
    if exists(path_to_file):
        sudo('{0} install -q -r {1}'.format(env.PIP_BIN, path_to_file))


def install_front_end_requirements():
    with cd(env.SRC_PATH):
        sudo('bower install --allow-root')


def copy_email_templates():
    with cd(env.SRC_PATH):
        sudo("%s manage.py copy_email_templates" % env.PYTHON_BIN)


def create_deployment_key():
    """
    Create a private key for deployment purposes in /var/www/.ssh
    """
    if not exists(env.DEPLOYMENT_KEY):
        require.users.user(name='www-data')
        require.files.directory('/var/www/.ssh', use_sudo=True,
                                owner='www-data', group='www-data')
        sudo('ssh-keygen -f {0}'.format(env.DEPLOYMENT_KEY), user='www-data')


def deploy_project(target_dir='retribution'):
    """ Deploys a project for the first time """
    # setup_env(target_dir)

    # if exists("%s" % env.PROJECT_PATH):
    #     abort('Project already deployed. Run "fab update_project -H <host>" instead')

    # setup_os()
    # require.files.directory(env.PROJECT_PATH, use_sudo=True,
    #                         owner='www-data', group='www-data')
    update_source_code()
    # setup_virtualenv()
    # log_dir = os.path.join(env.PROJECT_PATH, 'logs')
    # require.files.directory(log_dir, use_sudo=True,
    #                         owner='www-data', group='www-data')
    # setup_webserver()

    # TODO: Create DB is broken
    # create_db()

    # TODO: Settings_local preparation is broken
    # context = {
        # 'db_name': env.db_name,
        # 'db_user': env.db_user,
        # 'db_pass': env.db_pass,
    # }
    # sudo('mv %ssettings_local.py.tpl %s/%s/settings_local.py' %
        # (env.HOME_PATH, env.SRC_PATH, env.PROJECT_NAME))
    # install_project_requirements()
    # install_front_end_requirements()
    # collect_static()
    # compress_static()
    # sudo('chown -R www-data.www-data %s' % env.PROJECT_PATH)
    migrate()


def check_django_shell():
    output = sudo('ps aux | grep "manage.py shell" | grep -v grep | awk \'{ print $1" "$11" "$12" "$13}\'')
    if output:
        abort("""There is one or more django shell running on the system, please kill them first""")


def run_test():
    """
    Test application for error before deploying, abort deployment on failing test
    """
    local("python manage.py test --failfast")


def update_project(skip_test="true", target_dir='retribution', init_module='systemd'):
    """ Updates the source directory with most recent code, create migration
    and then restarts the webserver """
    setup_env(target_dir)
    if skip_test != "true":
        run_test()

    # Determine which init system to use
    if init_module == 'systemd':
        init_module = systemd
    else:
        init_module = service

    check_django_shell()

    # update temporary source code first, so we can know whether migration has addition
    # or deletion
    update_source_code(path=env.TEMP_SRC_PATH)
    symlink_settings_local()
    install_project_requirements(os.path.join(env.TEMP_SRC_PATH, 'requirements.txt'))

    # migration_type = check_migration_type()
    # if migration_type == "update_source_then_migrate":
    update_source_code()
        # Update & Reload all before migrating code
        # install_front_end_requirements()
    collect_static()
        # compress_static()
        # copy_email_templates()
        # init_module.restart("retribution")
        # if target_dir == 'retribution':
        #     init_module.restart('rqworker')
        #     init_module.restart('rqworker-elastic')
        #     with settings(warn_only=True):
        #         init_module.restart('rqworker2')
    migrate()
    #     return
    # elif migration_type == "migrate_then_update_source":
    #     # Migrate from temporary first
    #     migrate(env.TEMP_SRC_PATH)
    #     #  then normal stuff without migration again
    #     update_source_code()
    # elif migration_type is None:
    #     update_source_code()

    # install_front_end_requirements()
    collect_static()
    # compress_static()
    # copy_email_templates()

    init_module.restart("retribution")
    # if target_dir == 'retribution':
    #     init_module.restart('rqworker')
        # init_module.restart('rqworker-elastic')
        # with settings(warn_only=True):
        #     init_module.restart('rqworker2')


def update_au_project(skip_test="false"):
    update_project(skip_test=skip_test, target_dir='stamps_au')


def update_all_project(skip_test="false"):
    update_project(skip_test=skip_test, target_dir="stamps_au")
    update_project(skip_test="true", target_dir="retribution")


def setup_os():
    """ Prepare OS with necessary packages to host a django project """
    sudo('apt-get update')
    require.deb.packages([
        'python-setuptools',
        'python-dev',
        'build-essential',
        'libjpeg-dev',
        'python-imaging',
        'git-core',
        'libmysqlclient-dev',
        'libpq-dev',
        'python-mysqldb',
        'python-psycopg2',
        'python-pylibmc',
        'python-lxml',
        'libxml2-dev',
        'libxslt-dev',
        'rubygems',
        'ruby-dev',
        'gdal-bin',
        'redis-server',
        'npm',
        'software-properties-common',
        'python-software-properties',
    ])
    require.python.packages(['fabtools', 'pip'], use_sudo=True)
    # Link nodejs to node, https://github.com/nodejs/node-v0.x-archive/issues/3911#issuecomment-8956154
    sudo('ln -s /usr/bin/nodejs /usr/bin/node', warn_only=True)

    sudo('add-apt-repository ppa:webupd8team/java -y')
    sudo('apt-get update')

    # install sass and less compiler
    sudo('npm install -g less')
    sudo('npm install -g bower')
    sudo('gem install sass --no-ri --no-rdoc')
    sudo('gem install backup --no-ri --no-rdoc')

    # You need to install this manually, EULA form will make fabric stuck
    # sudo('sudo apt-get install oracle-java8-installer -y')


def update_git_repo():
    """ Creates or update user's git repository for this project """
    if not exists('%s%s' % (env.HOME_PATH, env.PROJECT_NAME)):
        git_cmd = 'git clone git@github.com:mapratama/retribution.git {}'.format(env.SRC_PATH)
        print """Your git repository for this project doesn't exist.
                 Now running "%s" in %s.""" % (git_cmd, env.HOME_PATH)
        with settings(warn_only=True):
            result = run(git_cmd)
        if result.failed:
            abort("""Failed to clone git repository. Please make sure that you
                  have access to the git repository and your public/private keys
                  are properly setup. You can try to manually setup the repo
                  by running "%s" from %s""" % (git_cmd, env.HOME_PATH))
    else:
        with cd(env.HOME_PATH + env.PROJECT_NAME):
            run('git pull')


def symlink_settings_local():
    temp_settings_local = os.path.join(env.TEMP_SRC_PATH, env.REPO_NAME, "settings_local.py")
    if not exists(temp_settings_local):
        main_settings_local = os.path.join(env.SRC_PATH, env.REPO_NAME, "settings_local.py")
        sudo('ln -s {0} {1}'.format(main_settings_local, temp_settings_local), user='www-data')


def update_source_code(path=None):
    """ Update project's source dir from git repo"""
    # If no repo is present, clone from localhost
    path = env.SRC_PATH if path is None else path

    if not exists(path):
        # Make a new deployment key if not already there
        if not exists(env.DEPLOYMENT_KEY, use_sudo=True):
            create_deployment_key()

        git_cmd = 'git clone git@github.com:mapratama/retribution.git {}'.format(path)
        require.files.directory(env.PROJECT_PATH, use_sudo=True)
        sudo('chown -R www-data {0}'.format(env.PROJECT_PATH))
        with cd(env.PROJECT_PATH):
            with settings(warn_only=True):
                result = sudo(git_cmd, user='www-data')
            if result.failed:
                abort("""Failed to clone git repository. Make sure that www-data
                    is allowed to clone repository by running this
                    on the server:
                    sudo -u www-data git clone gitolite@localhost:{0}""".format(env.REPO_NAME))

    # Get current git hash on the local machine
    git_hash = local('git rev-parse HEAD', capture=True)
    with cd(path):
        sudo('git fetch', user='www-data')
        sudo('git checkout {0}'.format(git_hash), user='www-data')
    if path == env.SRC_PATH:
        with cd(env.PROJECT_PATH):
            sudo('echo "{0}:{1}:{2}" >> revisions.log'.format(env.TIME, git_hash, env.user))


def setup_virtualenv():
    """ Setup virtualenv for a project """
    require.python.package('virtualenv', use_sudo=True)
    django_version = prompt('Django version to install [None]:')
    with cd(env.PROJECT_PATH):
        sudo('virtualenv env --system-site-packages')
    install_cmd = '{0} install -U django'.format(env.PIP_BIN)
    if django_version:
        install_cmd = install_cmd + '=={0}'.format(django_version)
    sudo(install_cmd)
    sudo('{0} install -U south'.format(env.PIP_BIN))


def collect_static():
    """ Runs django.contrib.staticfiles collectstatic command"""
    static_folder = os.path.join(env.SRC_PATH, env.PROJECT_NAME, 'static')
    require.files.directory(static_folder, use_sudo=True)
    sudo('chown -R www-data {0}'.format(static_folder))
    sudo('{0} collectstatic -l --noinput'.format(env.MANAGE_BIN), user='www-data')


def compress_static():
    """ Runs django_compressor's compress command"""
    with cd(env.SRC_PATH):
        sudo('{0} compress --force'.format(env.MANAGE_BIN), user='www-data')


def cleanup_removed_directories():
    dirs = run(
        '%s %s/fabfiles/scripts/get_dirs_to_remove.py --source_dir=%s%s --target_dir=%s --exclude=migrations,static' %
            (env.PYTHON_BIN, env.SRC_PATH, env.HOME_PATH, env.PROJECT_NAME,
             env.SRC_PATH))

    dirs = sorted(dirs.strip().split())
    for directory in dirs:
        if exists(directory):
            answer = prompt('Sure you want to delete %s [y/N]?' % directory)
            if answer == 'y':
                sudo('rm -r %s' % directory)
