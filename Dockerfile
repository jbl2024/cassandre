# Use the official Python image as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
RUN mkdir /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    nginx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt /app/requirements/base.txt
COPY requirements/prod.txt /app/requirements/prod.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements/base.txt && pip install --no-cache-dir -r /app/requirements/prod.txt

# Install necessary dependencies
RUN apt-get install -y curl gnupg build-essential

# Install Node.js and npm
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs

# Copy the Django project files
COPY . /app/

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