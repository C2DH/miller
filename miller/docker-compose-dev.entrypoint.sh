#!/bin/bash
python manage.py collectstatic --no-input
gunicorn --bind=0.0.0.0:8000 -w 2 -k gthread miller.wsgi
