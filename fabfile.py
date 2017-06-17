from __future__ import with_statement
from fabric.api import env, run, local, sudo, put, prompt, get
from fabric.contrib.project import rsync_project
from fabric.contrib.files import append, upload_template
from fabric.context_managers import cd
from time import strftime
from getpass import getpass
import os

from fabfiles.db import *
from fabfiles.deploy import *
from fabfiles.migrations import *
from fabfiles.webservers import *


env.PROJECT_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__))).lower()
env.PROJECT_PATH = '/var/www/%s/' % env.PROJECT_NAME
env.HOME_PATH = ('/home/%s/' % env.user)
env.TIME = strftime("%Y-%m-%d_%H:%M")
env.SRC_PATH = os.path.join(env.PROJECT_PATH, 'src')
env.TEMP_SRC_PATH = os.path.join(env.PROJECT_PATH, 'temp')
env.REPO_NAME = 'retribution'
env.GIT_PATH = '/home/git/repositories/{0}.git'.format(env.REPO_NAME)
env.VIRTUALENV_DIR = os.path.join(env.PROJECT_PATH, 'env')
env.PYTHON_BIN = os.path.join(env.VIRTUALENV_DIR, 'bin/python')
env.PIP_BIN = os.path.join(env.VIRTUALENV_DIR, 'bin/pip')
env.REQUIREMENTS_FILE = os.path.join(env.SRC_PATH, "requirements.txt")
env.DEPLOYMENT_KEY = '/var/www/.ssh/id_rsa'
env.MANAGE_PATH = os.path.join(env.SRC_PATH, 'manage.py')
env.MANAGE_BIN = '{0} {1}'.format(env.PYTHON_BIN, env.MANAGE_PATH)


def update_os():
    sudo('apt-get update && apt-get upgrade -y')


def project_cleanup():
    """ Deletes all previous project versions except for the last three """
    with cd(env.PROJECT_PATH):
        old_dirs = run('ls -td project-*/').split('\n')[3:]
        for directory in old_dirs:
            sudo('rm -r %s' % directory)


def deploy():
    setup_os()
    deploy_project()


def backup(db_pass, db_user):
    with cd("/srv"):
        sudo("mkdir -p backup")
    put('backup/automysqlbackup-ui.sh', env.HOME_PATH)
    put('backup/br-apache.sh', env.HOME_PATH)
    o = open("backup/backup2.sh", "a")
    for line in open("backup/backup.sh"):
        line = line.replace("<db_pass>", "%s" % db_pass)
        line = line.replace("<db_user>", "%s" % db_user)
        o.write(line)
    o.close()
    sudo("mv automysqlbackup-ui.sh /srv/backup/")
    sudo("mv br-apache.sh /srv/backup/")
    put('backup/backup2.sh', env.HOME_PATH)
    sudo("mv backup2.sh /srv/backup/")
    sudo("mv /srv/backup/backup2.sh /srv/backup/backup.sh")
    sudo("chmod +x /srv/backup/backup.sh")
    local('rm backup/backup2.sh')
    sudo('echo "00 1    * * *   root    /srv/backup/backup.sh" >> /etc/crontab')
    sudo('echo "00 2    * * *   root    rsync -avz --delete /var/www /srv/backup/data/apache/" >> /etc/crontab')


def setup_backup_client():
    """Sets up target host to do automatic daily Apache and MySQL backup"""
    prompt('Database user for mysql:', 'db_user')
    env.db_pass = getpass('Database password for mysql:')
    sudo("mkdir -p /srv/backup/data")
    sudo("mkdir -p /srv/backup/periodic")
    sudo("mkdir -p /srv/backup-scripts")
    sudo("chown -R ui-backup.ui-backup /srv/backup")
    sudo("sudo chmod -R a+rx backup-scripts")
    sudo("ln -s /var/www/ /srv/backup/data/apache/www")

    # Upload necessary templates and backup scriptsf
    upload_template(
        'backup/backup.sh.tpl',
        env.HOME_PATH,
        context={
            'db_user': env.db_user,
            'db_pass': env.db_pass,
        }
    )

    put('backup/automysqlbackup-ui.sh', env.HOME_PATH)
    put('backup/br-apache.sh', env.HOME_PATH)
    put('backup/last-full/userinspired-full-date', env.HOME_PATH)
    put('backup/periodic.sh', env.HOME_PATH)
    sudo("mv automysqlbackup-ui.sh /srv/backup-scripts/")
    sudo("mv br-apache.sh /srv/backup-scripts/")
    sudo("mv backup.sh.tpl /srv/backup-scripts/backup.sh")
    sudo("mv periodic.sh /srv/backup-scripts/")
    sudo("mkdir -p /srv/backup-scripts/last-full")
    sudo("mv userinspired-full-date /srv/backup-scripts/last-full")
    sudo("chmod +x /srv/backup-scripts/*.sh")

    append('00 1    * * *   ui-backup    /srv/backup-scripts/backup.sh', '/etc/crontab', use_sudo=True)
    # append('30 1    * * *   root    rsync -avz --delete /var/www /srv/backup/data/apache/', '/etc/crontab', use_sudo=True)
    append('00 2    * * *   ui-backup    /srv/backup-scripts/periodic.sh', '/etc/crontab', use_sudo=True)


def setup_backup_server():
    HOST = prompt('Hostname or IP address that you want to backup:', 'HOST')
    SERVER_NAME = prompt('Name of the server:', 'SERVER_NAME')
    time = prompt('Time for backup to be executed (ex: 00 5)', 'time')
    sudo("mkdir -p /srv/backup-server")
    sudo("chown ui-backup /srv/backup-server")
    append('%s * * *     ui-backup     rsync --delete -azvv -e ssh ui-backup@%s:/srv/backup/ /srv/backup-server/%s' % (time, HOST, SERVER_NAME), '/etc/crontab', use_sudo=True)


def transfer_project(remote_dir=env.HOME_PATH, exclude=['.git', '*.pyc', 'settings_local.py'], delete=False):
    rsync_project(env.HOME_PATH, exclude=exclude, delete=delete)


# Minor Varnish utilities
def varnish_stats(port=6082):
    """Executes a stats command on varnish"""
    run('exec 9<>/dev/tcp/localhost/%(port)s ; echo -e "stats\nquit" >&9; cat <&9' % locals())


def varnish_flush(port=6082, expression=".*"):
    """Purge cached items in varnish"""
    run('exec 9<>/dev/tcp/localhost/%(port)s ; echo -e "url.purge %(expression)s\nquit" >&9; cat <&9' % locals())


def varnish_setup():
    sudo('apt-get install varnish -y')
    port_number = prompt('Enter port number[6081]:', 'port_number')
    upload_template(
        'varnish/varnish.tpl',
        env.HOME_PATH,
        context={
            'port_number': port_number,
        }
    )
    sudo('rm /etc/default/varnish')
    sudo('mv varnish.tpl /etc/default/varnish')


def restart_varnish():
    sudo('/etc/init.d/varnish restart')


# Minor memcached utilities
def memcached_stats(port=11211):
    """Executes a stats command on memcached"""
    run('exec 9<>/dev/tcp/localhost/%(port)s ; echo -e "stats\nquit" >&9; cat <&9' % locals())


def memcached_restart():
    sudo('/etc/init.d/memcached stop && sudo /etc/init.d/memcached start')


def memcached_flush(port=11211, seconds=0):
    """ Flushes all memcached items """
    run('exec 9<>/dev/tcp/localhost/%(port)s ; echo -e "flush_all %(seconds)s\nquit" >&9; cat <&9' % locals())


def backup_webserver():
    sudo('./srv/backup/backup.sh')


def rollback():
    get('%srevisions.log', 'revisions.log' % env.PROJECT_PATH)
    get('%scurrent.log', 'current_revision.log' % env.PROJECT_PATH)
    for rev in open("current.log"):
        current_revision = rev
    i = 0
    revision = {}
    for line in open("revisions.log"):
        revision[i] = line
        if current_revision == revision[i]:
            if i == 0:
                print"no previous version"
            else:
                with cd(env.PROJECT_PATH):
                    sudo('rm -R latest')
                    sudo('ln -s %s latest' % revision[i - 1].rstrip('\n'))
                    sudo('cp -R latest/media .')
                    sudo('chown -R www-data.www-data media')
                    sudo('echo "%s" > %scurrent_revision.log' % (revision[i - 1].rstrip('\n'), env.PROJECT_PATH))
        i = i + 1
    local('rm current_revision.log')
    local('rm revisions.log')
