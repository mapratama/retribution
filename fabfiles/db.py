from getpass import getpass

from fabric.api import env, run, local, sudo, put, prompt, get
from fabric.context_managers import cd, settings
from fabric.contrib.files import upload_template, exists
from fabric.utils import abort

from fabtools import require


def backup_db(db_user='root', db_pass=None, database='--all-databases'):
    ''' Backup MySQL database(s) '''
    db_user = prompt('Database user to connect with [root]:') or 'root'
    env.db_pass = getpass('Database password to connect with []:')
    databases = prompt('Databases to backup [all]:') or '--all-databases'
    db_pass = '-p%s' % env.db_pass if env.db_pass else ''
    outfile = '%s-%s-%s.sql.gz' % (env.host, env.TIME,
                                   databases.lstrip('--').replace(' ', '_'))
    run('mysqldump --opt -u %(db_user)s %(db_pass)s --databases %(databases)s | gzip > /tmp/%(outfile)s' % locals())
    get('/tmp/%(outfile)s' % locals(), '%(outfile)s' %locals())
    run('rm /tmp/%(outfile)s' % locals())


def create_db():
    """ Create a PostgreSQL database """
    env.db_user = prompt('Database user to connect with [postgres]:') or 'postgres'
    env.db_pass = getpass('Database password to connect with []:')
    env.db_name = prompt('New database name:')
    require.postgres.database(name=env.db_name, owner=env.db_user)


def optimize_db():
    """
    A command to optimize all databases
    """
    db_user = prompt('Server database user to connect with [root]:') or 'root'
    env.db_pass = getpass('Server database password to connect with []:')
    db_pass = '-p%s' % env.db_pass if env.db_pass else ''
    run('mysqlcheck -u %s %s --auto-repair --check --optimize --all-databases' %
        (db_user, db_pass))


def move_tables(db_user='root', db_pass=None, database='--all-databases'):
    """
    Move MySQL tables from local database to another.
    Steps to move tables:
    1. Dump tables from source database
    2. Rename tables to table_name_new
    3. Transfer tables to destination database host
    4. Import the tables
    5. Rename original tables to table_name_old in destination database
    6. Rename the new tables from table_name_new to table_name
    """
    db_user = prompt('Source database user to connect with [root]:') or 'root'
    env.db_pass = getpass('Source database password to connect with []:')
    db_pass = '-p%s' % env.db_pass if env.db_pass else ''
    db = prompt('Database name []:').strip()
    tables = prompt('Tables to move (separated by spaces) []:').strip().split()
    outfile = '/tmp/%s-%s.sql' % (db, '__'.join(tables))

    #All of this is done on localhost
    local('mysqldump --opt -u %s %s %s %s > %s' % (db_user, db_pass, db, ' '.join(tables), outfile))
    for table in tables:
        #Now we need to replace these lines
        local("sed -i.bak -r -e 's/DROP TABLE IF EXISTS `%s`/DROP TABLE IF EXISTS `%s`/g' %s" % (table, (table + '_new'), outfile))
        local("sed -i.bak -r -e 's/CREATE TABLE `%s`/CREATE TABLE `%s`/g' %s" % (table, (table + '_new'), outfile))
        local("sed -i.bak -r -e 's/LOCK TABLES `%s` WRITE/LOCK TABLES `%s` WRITE/g' %s" % (table, (table + '_new'), outfile))
        local("sed -i.bak -r -e 's/ALTER TABLE `%s`/ALTER TABLE `%s`/g' %s" % (table, (table + '_new'), outfile))
        local("sed -i.bak -r -e 's/INSERT INTO `%s` VALUES/INSERT INTO `%s` VALUES/g' %s" % (table, (table + '_new'), outfile))
    local('cat %(outfile)s | gzip > %(outfile)s.gz' % locals())
    put('%s.gz' % outfile, '%s.gz' % outfile)

    db_user = prompt('Destination database user to connect with [root]:') or 'root'
    env.db_pass = getpass('Destination database password to connect with []:')
    db_pass = '-p%s' % env.db_pass if env.db_pass else ''

    #Now import the tables on destination host and rename
    run('gunzip < %s.gz | mysql -u %s %s %s' % (outfile, db_user, db_pass, db))
    rename_commands = ['ALTER TABLE %s RENAME %s_old;' % (table, table) for table in tables]
    rename_commands += ['ALTER TABLE %s_new RENAME %s;' % (table, table) for table in tables]
    rename_commands = ''.join(rename_commands)
    run('echo "use %s;%s" | mysql -u %s %s' % (db, rename_commands, db_user, db_pass))


def restart_db():
	sudo('/etc/init.d/mysql restart')
