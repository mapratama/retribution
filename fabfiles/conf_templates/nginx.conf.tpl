server {
  listen 80;
  server_name www.%(server_name)s;
  rewrite ^/(.*) http://%(server_name)s/$1 permanent;
}

server {
  listen 80;
  server_name %(server_name)s;

  #access_log %(project_path)slogs/access.log;
  #error_log %(project_path)slogs/error.log;

  gzip  on;
  gzip_http_version 1.1;
  gzip_vary on;
  gzip_comp_level 6;
  gzip_proxied any;
  gzip_types text/plain text/css application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript;

  location /media {
    root %(project_path)s;
    expires max;
  }
  
  location /static {
    root %(project_path)ssrc/%(project_name)s/;
    expires max;
  }

  location / {
    proxy_pass http://127.0.0.1:%(port)s;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header Host $host;
    proxy_intercept_errors off;
  }
}

