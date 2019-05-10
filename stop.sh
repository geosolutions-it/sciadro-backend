#!/usr/bin/env bash

nohup docker-compose down &> /dev/null &
nohup docker-compose -f docker-compose-test.yml down &> /dev/null &
