#!/bin/bash

/wait
python manage.py migrate
python manage.py test
