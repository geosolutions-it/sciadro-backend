#!/bin/bash

/wait
celery -A api worker -l info &
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
