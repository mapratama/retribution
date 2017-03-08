from __future__ import with_statement
from fabric.api import env, run, local, sudo, put, prompt, settings, get
from fabric.contrib.project import rsync_project, upload_project
from fabric.contrib.files import append, upload_template, sed, exists
from fabric.utils import abort
from fabric.context_managers import cd
from fabric.operations import local, get, prompt
from time import strftime
from getpass import getpass
import os, site, sys

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
env.REPO_NAME = 'rumahtotok'
env.GIT_PATH = '/srv/gitolite/repositories/{0}.git'.format(env.REPO_NAME)
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

    #Upload necessary templates and backup scriptsf
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
    #append('30 1    * * *   root    rsync -avz --delete /var/www /srv/backup/data/apache/', '/etc/crontab', use_sudo=True)
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


#Minor Varnish utilities
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


#Minor memcached utilities
def memcached_stats(port=11211):
    """Executes a stats command on memcached"""
    run('exec 9<>/dev/tcp/localhost/%(port)s ; echo -e "stats\nquit" >&9; cat <&9' % locals())


def memcached_restart():
    sudo('/etc/init.d/memcached stop && sudo /etc/init.d/memcached start')


def memcached_flush(port=11211, seconds=0):
    """ Flushes all memcached items """
    run('exec 9<>/dev/tcp/localhost/%(port)s ; echo -e "flush_all %(seconds)s\nquit" >&9; cat <&9' % locals())


# deploy word press project

def deploy_wp_project(remote_dir=env.HOME_PATH, exclude=['.git', 'apache', 'fabfile.py', 'fabfile.pyc'], delete=False):
    if not os.path.exists("%s" % env.PROJECT_PATH):
        rsync_project(env.HOME_PATH, exclude=exclude, delete=delete)
        db_name = prompt('Enter db name:', 'db_name')
        db_user = prompt('Enter db user[root]:', 'db_user')
        db_pass = getpass('Database password:')
        run('sed -i "s/define(\'DB_NAME\',.*);/define(\'DB_NAME\', \'%s\');/" %sqi/wp-config.php' % (db_name, env.HOME_PATH))
        run('sed -i "s/define(\'DB_USER\',.*);/define(\'DB_USER\', \'%s\');/" %sqi/wp-config.php' % (db_user, env.HOME_PATH))
        run('sed -i "s/define(\'DB_PASSWORD\',.*);/define(\'DB_PASSWORD\', \'%s\');/" %sqi/wp-config.php' % (db_pass, env.HOME_PATH))
        sudo('cp -R %s /var/www/%s' % (env.PROJECT_NAME, env.PROJECT_NAME))
        sudo('a2enmod rewrite')
        sudo('chown -R www-data.www-data %swp-content/uploads ' % env.PROJECT_PATH)
        setup_apache("sitewp.tpl")
        print "Anda harus melakukan import database anda sebelum mengakses ke website"
    else:
        print "Project ini telah dibuat sebelumnya"

    #upload_template(
    #   'apache/sitewp.tpl',
    #   env.HOME_PATH,
    #   context = {
    #       'server_name' : server_name,
    #       'project_name' : PROJECT_NAME,
    #   }
    #)
    #sudo('mv sitewp.tpl /etc/apache2/sites-available/%s' % PROJECT_NAME)
    #sudo('a2ensite %s' %PROJECT_NAME)

    #sudo('mkdir -p /var/log/www')


def upgrade_wordpress(upload_file="y"):
    upload_file = prompt('Do you want to download latest.tar.gz (y/n):', 'upload_file')
    if upload_file == "y":
        sudo('rm -f latest.tar.gz')
        run('wget http://wordpress.org/latest.tar.gz')
    run('mkdir -p ~/wpupgrade/%s' % env.TIME)
    run('mkdir -p ~/wpupgrade/bac/%s' % env.TIME)
    run('cp ~/latest.tar.gz ~/wpupgrade/%s' % env.TIME)
    run('tar -C ~/wpupgrade/%s -xzf ~/wpupgrade/%s/latest.tar.gz' % (env.TIME, env.TIME))
    run('cp -R %s \
    ~/wpupgrade/bac/%s/' % (env.PROJECT_PATH, env.TIME))
    sudo('cp -R ~/wpupgrade/%s/wordpress/* \
    %s' % (env.TIME, env.PROJECT_PATH))
    sudo('chown -R  www-data %s' % env.PROJECT_PATH)
    sudo('rm -R ~/wpupgrade/%s' % env.TIME)
    print("\nNow visit http://%s/wp-admin to complete upgrade" % env.host)


def update_wp_project(remote_dir=env.HOME_PATH, exclude=['.git', 'apache', 'fabfile.py', 'fabfile.pyc', 'wp-config.php'], delete=False):
    rsync_project(env.HOME_PATH, exclude=exclude, delete=delete)
    with cd(env.PROJECT_PATH):
        sudo('mv /wp-content/themes/%s %s-%s.bak' % (env.PROJECT_NAME, env.PROJECT_NAME, env.TIME))
        sudo('cp ~/%s/wp-content/themes/%s /wp-content/themes/' % (env.PROJECT_NAME, env.PROJECT_NAME))
        apache_restart()


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


def get_report(type=None, start_date=None, end_date=None, slug=None):
    type_names = ['transaction', 'redemption', 'new_user',
                  'transaction_log', 'transaction_by_store']
    if type:
        if type not in type_names and type != 'all':
            abort('incorrect type argument')

    # show report choices promt if report type is None
    if type is None:
        print '\nPlease choose the reports you want to download:'
        print '1. Transaction'
        print '2. Redemption'
        print '3. New User'
        print '4. Transaction Log'
        print '5. Transaction by Store\n'

        while True:
            report_choice = prompt('Choose 1, 2, 3, 4 or 5: ', validate=int)
            if report_choice in [1, 2, 3, 4, 5]:
                break

        type = type_names[report_choice - 1]

    stamps_cache_dir = '~/.rumahtotok/cache'

    if type != 'all':
        report_cache_dir = '{0}/{1}_report'.format(stamps_cache_dir, type)
        generate_report(stamps_cache_dir, type, start_date, end_date, slug)
        get(report_cache_dir, '.')

        # cleanup cache directory after the process has finished
        run('rm -rf {0}'.format(report_cache_dir))

    else:
        for type in type_names:
            generate_report(stamps_cache_dir, type, start_date, end_date, slug)

        run('tar -zcvf {0}/report.tar.gz *'.format(stamps_cache_dir))
        get('{0}/report.tar.gz'.format(stamps_cache_dir), '.')
        run('rm -rf {0}/*'.format(stamps_cache_dir))


def generate_report(stamps_cache_dir, type, start_date, end_date, slug):
    report_cache_dir = '{0}/{1}_report'.format(stamps_cache_dir, type)

    if exists(report_cache_dir):
        run('rm -rf {0}'.format(report_cache_dir))

    run('mkdir -p {0}'.format(report_cache_dir))

    cmd = '{0} generate_{1}_report'.format(env.MANAGE_BIN, type)

    if start_date:
        cmd += ' --start-date {0}'.format(start_date)
    if end_date:
        cmd += ' --end-date {0}'.format(end_date)
    if slug:
        cmd += ' --slug {0}'.format(slug)

    with cd(report_cache_dir):
        run(cmd)
