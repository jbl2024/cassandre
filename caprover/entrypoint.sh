#!/bin/sh

# Change to the app directory
cd /app

# Run migrations
python3 manage.py migrate

# Create superuser if it does not exist
python3 manage.py create_superuser

# Collect static files
python3 manage.py collectstatic --noinput

# Start Gunicorn
gunicorn cassandre.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile '-' \
    --error-logfile '-'
