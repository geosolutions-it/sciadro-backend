#!/bin/bash

/wait
script_result=0
celery -A api worker -l info &
coverage run --source='.' manage.py test

if [ $? -ne 0 ]; then
    script_result=1
fi

coverage html
coverage report
exit $script_result
