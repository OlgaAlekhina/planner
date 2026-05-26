#!/bin/bash

python manage.py migrate

python manage.py collectstatic --noinput

gunicorn -b 0.0.0.0:8000 --workers 4 planner.wsgi