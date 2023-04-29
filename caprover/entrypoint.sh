#!/bin/sh

# Change to the app directory
cd /app

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn cassandre.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile '-' \
    --error-logfile '-'
