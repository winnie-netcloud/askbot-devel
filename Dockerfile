# This Dockerifle builds a simple Askbot installation
#
# It makes use of environment variables:
# 1. DATABASE_URL See https://github.com/kennethreitz/dj-database-url for details
# 2. SECRET_KEY for making hashes within Django.
#
# Make sure to *+always* start the container with the same SECRET_KEY.
#
# Start with something like
#
# docker run -it -e 'DATABASE_URL=sqlite:////askbot_site/askbot.db' -e 'SECRET_KEY=<random key>' -p 127.0.0.1:8080:80 askbot/askbot:latest
#
FROM python:3.6

ENV PYTHONUNBUFFERED 1

ADD . /src/
WORKDIR /src/
RUN pip install -r askbot_requirements.txt gunicorn
RUN python setup.py install

RUN mkdir /askbot_site/
WORKDIR /askbot_site/
RUN askbot-setup --dir-name=. --db-engine=2 \
    --db-name=USE_DATABASE_URL_INSTEAD \
    --db-user=USE_DATABASE_URL_INSTEAD \
    --db-password=USE_DATABASE_URL_INSTEAD \
    --logfile-name=stdout \
    --no-secred-key

RUN sed "s/ROOT_URLCONF.*/ROOT_URLCONF = 'urls'/"  settings.py -i

RUN SECRET_KEY=whatever python manage.py collectstatic --noinput

RUN cp django.wsgi wsgi.py

RUN echo 'python manage.py migrate --noinput' > entrypoint.sh && \
  echo 'gunicorn -b 0.0.0.0:80 wsgi' >> entrypoint.sh
ENTRYPOINT bash entrypoint.sh

EXPOSE 80
