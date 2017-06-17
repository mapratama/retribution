import os

from fabric.api import env, run, local, sudo, put, prompt, get
from fabric.context_managers import cd
from fabric.contrib.files import append, upload_template, exists
from fabric.operations import local

from fabtools import require


def setup_webserver():
    """ Setups nginx or Apache """
    """
    string = 'Webserver\n1. Apache mod_wsgi\n2. NginX + gunicorn:'
    webserver = int(prompt(string, 'webserver'))
    if webserver not in [1, 2]:
        abort("You must enter 1 or 2")
    elif webserver == 1:
        setup_apache()
        restart_apache()
    """
    setup_nginx()
    install_gunicorn()


def setup_apache():
	""" Setup apache with mod_wsgi to run django """
	sudo('apt-get install libapache2-mod-wsgi phpmyadmin')
	server_name = prompt('Enter server name (e.g example.com):', 'server_name')
	upload_template('fabfiles/conf_templates/apache.conf.tpl', env.HOME_PATH,
		context = {
			'server_name': server_name,
			'project_path': env.PROJECT_PATH,
			'project_name': env.PROJECT_NAME,
		}
	)
	with cd(env.HOME_PATH):
	    sudo('mv apache.conf.tpl /etc/apache2/sites-available/%s' %
	         env.PROJECT_NAME)
	sudo('a2ensite %s' % env.PROJECT_NAME)


def setup_nginx(TEMPLATE="nginx.conf.tpl"):
    """ Setup and install nginx """
    require.deb.package('nginx')
    server_name = prompt('Enter server name (e.g example.com):', 'server_name')
    prompt('Port number your application to run on [81]:', 'server_port')
    if not env.server_port:
        env.server_port = 81
    upload_template('fabfiles/conf_templates/%s' % TEMPLATE, env.HOME_PATH,
	    context = {
		    'server_name': server_name,
		    'project_path': env.PROJECT_PATH,
		    'project_name': env.PROJECT_NAME,
            'port': env.server_port,
	    }
    )
    sudo('mv %s /etc/nginx/sites-available/%s' % (TEMPLATE, env.PROJECT_NAME))
    sudo('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' %
         (env.PROJECT_NAME, env.PROJECT_NAME))
    setup_upstart()


def setup_upstart(TEMPLATE="upstart.conf.tpl"):
    """ Setup and install upstart to monitor and run gunicorn"""
    upload_template(
	    'fabfiles/conf_templates/%s' % TEMPLATE, env.HOME_PATH,
	    context = {
		    'project_path': env.PROJECT_PATH,
		    'project_name': env.PROJECT_NAME,
		    'port': env.server_port,
	    }
    )
    sudo('mv %s /etc/init/%s.conf' % (TEMPLATE, env.PROJECT_NAME))


def install_gunicorn():
    """ Installs gunicorn in project's virtualenv """
    sudo('{0} install gunicorn -U'.format(env.PIP_BIN))


def restart_webserver():
    """ Restarts gunicorn"""
    restart_gunicorn()


def restart_gunicorn():
    '''
    Usage: fab restart_gunicorn -H <HOSTNAME>
    For example: fab restart_gunicorn -H nuansa.ui.co.id

    To restart gunicorn, we need to send "kill -HUP masterpid" command.
    http://gunicorn.org/faq.html
    '''
    output = sudo('status %s' % env.PROJECT_NAME)
    if 'running' in output:
        sudo('restart %s' % env.PROJECT_NAME)


def reload_gunicorn():
    '''
    Usage: fab restart_gunicorn -H <HOSTNAME>
    For example: fab reload_gunicorn -H nuansa.ui.co.id

    To restart gunicorn, we need to send "kill -HUP masterpid" command.
    http://gunicorn.org/faq.html
    '''
    output = sudo('status %s' % env.PROJECT_NAME)
    if 'running' in output:
        sudo('reload %s' % env.PROJECT_NAME)


def restart_apache():
	sudo('/etc/init.d/apache2 restart')

