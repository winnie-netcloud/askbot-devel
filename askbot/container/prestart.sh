#!/usr/bin/env bash

python ${ASKBOT_SITE}/askbot_app/prestart.py

if [ -z "$NO_CRON" ]; then
    crond || cron
fi

