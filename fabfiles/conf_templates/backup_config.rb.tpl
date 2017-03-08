Backup::Model.new(:local_backup, 'Nuansa musik nightly backup') do
  
  # Backup MySQL
  database MySQL do |db|
    db.name               = :all
    db.username           = "root"
    db.password           = "%(password)s"
    db.host               = "localhost"
    db.port               = 3306
    db.socket             = "/var/run/mysqld/mysqld.sock"
    #db.skip_tables        = []
    db.additional_options = ['--quick', '--single-transaction']
  end

  sync_with RSync::Local do |rsync|
    rsync.path               = "/srv/backup/data"
    rsync.mirror             = true
    #rsync.compress           = true
    rsync.additional_options = ['--exclude "*.pyc" --exclude "thumbs"']

    # Rsync /var/www, nginx and apache2 configs
    rsync.directories do |directory|
      directory.add "/var/www"
      directory.add "/etc/nginx"
      directory.add "/etc/apache2"
    end
  end

  compress_with Gzip do |compression|
    compression.best = false
    compression.fast = true
  end

  store_with Local do |local|
    local.path = '/srv/backup/data/'
    local.keep = 1
  end  

  notify_by Mail do |mail|
    mail.on_success           = true
    mail.on_failure           = true
    mail.from                 = 'backup@ui.co.id'
    mail.to                   = ['selwin@ui.co.id', 'joe@ui.co.id']
    mail.address              = 'smtp.gmail.com'
    mail.port                 = 587
    mail.domain               = 'gmail.com'
    mail.user_name            = 'backup@ui.co.id'
    mail.password             = 'backup-important'
    mail.authentication       = 'plain'
    mail.enable_starttls_auto = true
  end

end

Backup::Model.new(:rotate, 'Nuansa musik backup rotation') do


  archive :data do |archive|
    archive.add '/srv/backup/data/'
  end

  compress_with Gzip do |compression|
    compression.best = false
    compression.fast = true
  end

  # Keep 5 daily copies of backup data
  store_with Local do |local|
    local.path = '/srv/backup/'
    local.keep = 5
  end

  notify_by Mail do |mail|
    mail.on_success           = true
    mail.on_failure           = true
    mail.from                 = 'backup@ui.co.id'
    mail.to                   = ['selwin@ui.co.id', 'joe@ui.co.id']
    mail.address              = 'smtp.gmail.com'
    mail.port                 = 587
    mail.domain               = 'gmail.com'
    mail.user_name            = 'backup@ui.co.id'
    mail.password             = 'backup-important'
    mail.authentication       = 'plain'
    mail.enable_starttls_auto = true
  end

end