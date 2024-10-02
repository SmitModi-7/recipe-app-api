#!/bin/sh

# If any command fails then fail the whole script
set -e

# Running this commands when this script is executed
python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

# Run a Django application with uWSGI.
# socket :9000: This tells uWSGI to listen on port 9000 for incoming requests.
# workers 4: Run with 4 worker processes, which can handle multiple requests in parallel.
# master: Enables the master process to manage the worker processes.
# enable-threads: Allows the use of threads within the workers
# module app.wsgi: Entry point for the WSGI server.
uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi
