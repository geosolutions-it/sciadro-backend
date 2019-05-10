#!/bin/bash

/wait

celery -A api worker -l info &
python manage.py migrate
coverage run --source='.' manage.py test
coverage html
