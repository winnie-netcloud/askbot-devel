#!/usr/bin/env bash

python manage.py migrate --noinput
if [ ! -z "$ADMIN_PASSWORD" ]
then
  python manage.py askbot_add_user --user-name admin --email admin@localhost --password "$ADMIN_PASSWORD" --status d
  yes | python manage.py add_admin 1
fi
