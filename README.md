# Django Knowledge Base

## Best Practices

Try to follow best practices when creating and maintaining projects, specifically around structure/architecture and naming conventions


### Project Structure
```
<repository_root>/
├── config/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── <django_project_root>/
│   ├── <name_of_the_app>/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── __init__.py
│   └── ...
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
├── manage.py
├── README.md
└── ...
```

### Naming Conventions

#### App Names
Choose descriptive and concise names for your apps. Use lowercase letters, avoid spaces, and separate words with underscores (e.g., blog_app).

#### Model Names
Use singular nouns for model names, capitalizing the first letter of each word (e.g., BlogPost).

#### Field Names:
Follow lowercase and underscores for field names (e.g., created_at).

#### URL Patterns
Use lowercase, hyphen-separated words for URL patterns (e.g., /blog-posts/).

## Deployment

Partially based on [DigitalOcean's](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu) deployment guide

- Copy/Upload/Clone folder to remote DO Droplet
- Install required Packages
```
sudo apt update
sudo apt install python3-venv python3-dev nginx curl
```
- Create [virtual environment](https://docs.python.org/3/library/venv.html) for the Django project
``` (in project dir)
python3 -m venv .venv
```

- Access virtual environment
```bash
source myprojectenv/bin/activate
```
- Install necessary dependencies
```bash
pip install gunicorn
```

#### Django Project Settings

Remember to correctly set the ALLOWED_HOSTS variable in the django project settings file, pointing to the remote IP and Domains


### Gunicorn Setup
```bash
cd ~/myprojectdir
gunicorn --bind 0.0.0.0:8000 myproject.wsgi
```

#### Create Socket and Service
Socket
```bash
sudo nano /etc/systemd/system/gunicorn.socket
```
Socket example contents
```bash
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Service
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Service example contents
```bash
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/home/root/myprojectdir
ExecStart=/home/root/myprojectdir/myprojectenv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          myproject.wsgi:application

[Install]
WantedBy=multi-user.target
```
Start and check service and socket

```bash
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

sudo systemctl status gunicorn.socket
file /run/gunicorn.sock

sudo journalctl -u gunicorn.socket

sudo systemctl status gunicorn

curl --unix-socket /run/gunicorn.sock localhost

sudo systemctl status gunicorn

sudo journalctl -u gunicorn

gunicorn --workers 3 myproject.wsgi:application --daemon
```

Restart commands

```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

### Nginx Configuration

Create Nginx available sites config
```bash
sudo nano /etc/nginx/sites-available/myproject
```

Example available site config
```bash
server {
    listen 80;
    server_name server_domain_or_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/root;
    }
    location /media/ {
        root /home/root/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

Link the file to the ln

```bash
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled

sudo nginx -t
```

Restart
```bash
sudo systemctl restart nginx
```

Configure port forwarding

```bash
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'
```

### File Permissions

Check that file permissions for the project folders are assigned to ```root```, else

```bash
sudo chmod 755 ~/
```

### Error Checking

Nginx Error tail
```bash
sudo tail -F /var/log/nginx/error.log
```

### Resets

```
sudo systemctl restart gunicorn
sudo systemctl daemon-reload
sudo systemctl restart gunicorn.socket gunicorn.service
sudo nginx -t && sudo systemctl restart nginx
```