description "Start and stop djutils' queue consumer"
author "Selwin Ong (selwin@ui.co.id)"
version "0.1"

start on runlevel [2345]
stop on runlevel [!2345]

respawn

script
    # prepare environment
    cd %(project_path)ssrc
    %(project_path)senv/bin/python manage.py queue_consumer -l %(project_path)slogs/queue.log
end script
