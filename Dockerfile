# This Dockerifle builds a simple Askbot installation
#
# It makes use of environment variables:
# 1. DATABASE_URL See https://github.com/kennethreitz/dj-database-url for details
# 2. SECRET_KEY for making hashes within Django.
# 3. ADMIN_PASSWORD used for creating a user named "admin"
#
# Make sure to *+always* start the container with the same SECRET_KEY.
#
# Start with something like
#
# docker run -e 'DATABASE_URL=sqlite:////askbot_site/askbot.db' -e "SECRET_KEY=$(openssl rand 14 | base64)" -e ADMIN_PASSWORD=admin -p 8080:80 askbot/askbot:latest
#
FROM tiangolo/uwsgi-nginx:python3.6

ENV PYTHONUNBUFFERED 1
ENV UWSGI_INI /askbot_site/uwsgi.ini
ENV PRE_START_PATH /askbot_site/prestart.sh

# TODO: changing this requires another cache backend
ENV NGINX_WORKER_PROCESSES 1

ADD . /src/
WORKDIR /src/
RUN pip install -r askbot_requirements.txt
RUN python setup.py install

RUN mkdir /askbot_site/
RUN cp askbot/container/* /askbot_site
RUN cp /askbot_site/prestart.sh /app

WORKDIR /askbot_site/
RUN askbot-setup --dir-name=. --db-engine=2 \
    --db-name=USE_DATABASE_URL_INSTEAD \
    --db-user=USE_DATABASE_URL_INSTEAD \
    --db-password=USE_DATABASE_URL_INSTEAD \
    --logfile-name=stdout \
    --no-secred-key

RUN sed -i "s/ROOT_URLCONF.*/ROOT_URLCONF = 'urls'/"  settings.py
RUN sed -i 's!PROJECT_ROOT = .*!PROJECT_ROOT = "/askbot_site"!g' settings.py

RUN SECRET_KEY=whatever python manage.py collectstatic --noinput
