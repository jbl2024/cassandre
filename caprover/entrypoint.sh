#!/bin/sh

# Change to the app directory
cd /app

# Start Nginx in the background
nginx -g "daemon on;"

# Run migrations
python manage.py migrate

# Create superuser if it does not exist
python manage.py create_superuser

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn cassandre.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile '-' \
    --error-logfile '-'
