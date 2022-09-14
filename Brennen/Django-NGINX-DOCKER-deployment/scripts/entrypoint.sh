#!/bin/sh

set -e

python manage.py collectstatic --noinput

# command that runs the application using uWSGI
# like a TCP socket on port 8000
# run this as the master service or the master thread on the application
# basically run you whiskey in the foreground instead of running it as a background task
uwsgi --socket :8000 --master --enable-threads --module Production_Project.wsgi
