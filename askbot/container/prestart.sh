#!/usr/bin/env bash

python manage.py migrate --noinput || true
if [ -n "$ADMIN_PASSWORD" ]
then
  python manage.py askbot_add_user --user-name admin --email admin@localhost --password "$ADMIN_PASSWORD" --status d ||
true
   { yes yes | python manage.py add_admin 1; } || true
fi

if [ -z "$NO_CRON" ]
then
    set | grep -e 'PATH' -e 'DATABASE_URL' -e 'SECRET_KEY' -e 'PYTHONUNBUFFERED' -e 'ASKBOT_SITE' > /cron_environ
    echo 'PYTHONPATH="/usr/local/lib/python36.zip:/usr/local/lib/python3.6:/usr/local/lib/python3.6/lib-dynload:/usr/local/lib/python3.6/site-packages:/src/src/django-followit:/src/src/django-livesettings3"' >> /cron_environ
    crond || cron
fi

