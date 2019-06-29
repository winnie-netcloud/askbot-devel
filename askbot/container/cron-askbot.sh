#!/usr/bin/env bash
cd /askbot_site
export PYTHONPATH="/usr/local/lib/python36.zip:/usr/local/lib/python3.6:/usr/local/lib/python3.6/lib-dynload:/usr/local/lib/python3.6/site-packages:/src/src/django-followit:/src/src/django-livesettings3"
export $(cat cron_environ | xargs)
/usr/local/bin/python manage.py send_email_alerts > /proc/1/fd/1 2>/proc/1/fd/2
