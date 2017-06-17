start on runlevel [2345]
stop on runlevel [!2345]
kill timeout 5
respawn

env LANG=en_US.UTF-8
env LC_ALL=en_US.UTF-8
env LC_LANG=en_US.UTF-8

script

   cd %(project_path)ssrc
   exec %(project_path)senv/bin/gunicorn %(project_name)s.wsgi:application \
       --log-file=/var/log/nginx/%(project_name)s_gunicorn.log \
       --bind=127.0.0.1:%(port)s \
       --user=www-data \
       --group=www-data \
       --max-requests=100 \
       --workers=4 \
       --name=%(project_name)s
end script
