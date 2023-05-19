#!/bin/sh

# Change to the app directory
cd /app

# Start Nginx in the background
nginx -g "daemon on;"

# Run migrations
python manage.py migrate

# Create superuser if it does not exist
python manage.py create_superuser

# Start Celery worker in the background
celery -A cassandre worker --loglevel=info &

# Start Daphne
daphne cassandre.asgi:application
