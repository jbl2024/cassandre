# Use the official Python image as the base image
FROM python:3.9-slim as build

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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the Django project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Set up Nginx
FROM nginx:1.21-alpine

# Copy Nginx configuration
COPY caprover/nginx.conf /etc/nginx/conf.d/default.conf

# Copy the static files from the build stage
COPY --from=build /app/static /static/

# Copy the Django project files from the build stage
COPY --from=build /app/ /app/

# Copy the entrypoint script
COPY caprover/entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose the Nginx service port
EXPOSE 80

# Run the entrypoint script
CMD ["/entrypoint.sh"]