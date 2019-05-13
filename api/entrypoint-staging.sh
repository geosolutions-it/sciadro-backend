#!/bin/bash

/wait

celery -A api worker -l info &

python manage.py migrate
python manage.py collectstatic -c --noinput
gunicorn api.wsgi:application --bind 0.0.0.0:8000
#python manage.py runserver 0.0.0.0:8000
