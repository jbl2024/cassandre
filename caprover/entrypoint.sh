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

# Start Gunicorn
gunicorn cassandre.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 600 \
    --access-logfile '-' \
    --error-logfile '-'
