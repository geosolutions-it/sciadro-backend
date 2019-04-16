#!/bin/bash

/wait
python manage.py migrate
coverage run --source='.' manage.py test
coverage html
