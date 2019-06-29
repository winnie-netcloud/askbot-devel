#!/usr/bin/env bash

python manage.py migrate --noinput
if [ -n "$ADMIN_PASSWORD" ]
then
  python manage.py askbot_add_user --user-name admin --email admin@localhost --password "$ADMIN_PASSWORD" --status d
  yes yes | python manage.py add_admin 1
fi

if [ -z "$NO_CRON" ]
then
    set | grep -e 'PATH' -e 'DATABASE_URL' -e 'SECRET_KEY' -e 'PYTHONUNBUFFERED' > cron_environ
    cron
fi

