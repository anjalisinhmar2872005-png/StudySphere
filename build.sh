#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); u, created=User.objects.get_or_create(username='$DJANGO_SUPERUSER_USERNAME', defaults={'email':'$DJANGO_SUPERUSER_EMAIL'}); u.email='$DJANGO_SUPERUSER_EMAIL'; u.set_password('$DJANGO_SUPERUSER_PASSWORD'); u.is_staff=True; u.is_superuser=True; u.save()"