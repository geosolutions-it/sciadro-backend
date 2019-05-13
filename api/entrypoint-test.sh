#!/bin/bash

/wait

celery -A api worker -l info &
coverage run --source='.' manage.py test
script_result=0

if [ $? -ne 0 ]; then
    $script_result=$?
fi
coverage html
coverage report
exit $script_result
