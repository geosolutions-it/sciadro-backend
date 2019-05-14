#!/bin/bash

/wait

celery -A api worker -l info &

python manage.py migrate
python manage.py collectstatic --no-input --clear
gunicorn api.wsgi:application --bind 0.0.0.0:8000
