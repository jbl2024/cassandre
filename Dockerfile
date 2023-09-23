# Use the official Python image as the base image
FROM python:3.11.3-slim

ARG SECRET_KEY
# Set environment variables
ENV SECRET_KEY=$SECRET_KEY
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE cassandre.prod_settings

# Create and set the working directory
RUN mkdir /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    build-essential \
    libpq-dev \
    git \
    nginx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Generate fr_FR.UTF-8 locale
RUN sed -i '/fr_FR.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

# Set fr_FR.UTF-8 as the default locale
ENV LANG fr_FR.UTF-8  
ENV LANGUAGE fr_FR:fr  
ENV LC_ALL fr_FR.UTF-8  

# Install Python dependencies
COPY requirements/base.txt /app/requirements/base.txt
COPY requirements/prod.txt /app/requirements/prod.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements/base.txt && pip install --no-cache-dir -r /app/requirements/prod.txt

# Install necessary dependencies
RUN apt-get update && apt-get install -y curl gnupg build-essential

# Install Node.js and npm
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs

# Copy the Django project files
COPY . /app/

# Build tailwind
RUN python manage.py tailwind install
RUN python manage.py tailwind build

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy ML models
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
RUN transformers-cli download "Jean-Baptiste/camembert-ner-with-dates"

# Copy Nginx configuration
COPY caprover/nginx.conf /etc/nginx/conf.d/default.conf

# Copy the entrypoint script
COPY caprover/entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose the Nginx service port
EXPOSE 80

# Run the entrypoint script
CMD ["/entrypoint.sh"]