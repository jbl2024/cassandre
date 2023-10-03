# Cassandre

## Architecture

Cassandre is a Django-based application that uses Celery for task queues and ASGI for websockets. It's designed to run in a Docker environment with several services including PostgreSQL, Minio, Redis, and Qdrant.

- **Django + Celery + ASGI**: The main application is built with Django. Celery is used for managing asynchronous tasks and ASGI for handling websockets.

- **Docker Services**: The application runs in a Docker environment with several services:
  - **PostgreSQL**: Used as the main database.
  - **Minio**: An object storage server used for storing files.
  - **Redis**: Used as a message broker for Celery.
  - **Qdrant**: A vector similarity search engine used for document indexing.

## Setup (dev mode)

### Option 1: local python, dockerized services

Install dependencies

```sh
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements/dev.txt
```

Run services:
```
$ make docker
```

Apply migrations:
```
$ python manage.py migrate
```

Run all:
```
$ ./start_all.sh
```

Front:
http://localhost:8000/search

Backoffice:
http://localhost:8000/admin

### Option 2: all docker

Run dev container:
```
$ docker-compose --profile dev up
```

Rebuild dev container:
```
$ docker-compose --profile dev build
```

Execute any commands:
```
$ docker-compose exec web python manage.py createsuperuser
```
```
$ docker-compose exec web python manage.py makemigrations
```

## Environment Variables
```
DB_USER=
DB_HOST=
DB_NAME=
DB_PASSWORD=
DB_PORT=5432
QDRANT_URL=
DJANGO_SETTINGS_MODULE=cassandre.prod_settings
MINIO_ACCESS_KEY_ID=
MINIO_SECRET_ACCESS_KEY=
MINIO_STORAGE_BUCKET_NAME=
MINIO_URL=
DJANGO_SUPERUSER_USERNAME=
DJANGO_SUPERUSER_EMAIL=
DJANGO_SUPERUSER_PASSWORD=
OPENAI_API_KEY=
SECRET_KEY=
CELERY_BROKER_URL=
SPLIT_CHUNK_SIZE=1000
SPLIT_CHUNK_OVERLAP=100
PARADIGM_API_KEY=
PARADIGM_HOST=
WEBSOCKET_URL=
CHANNEL_REDIS=
```

## Makefile

The `Makefile` contains several commands for running the application and managing its dependencies. It includes commands for running the server in development mode, stopping the server, running Celery, applying migrations, and others.

## Application Modules

The application is divided into several modules, each with its own responsibilities. These include:

- **Documents**: Handles operations related to documents.
- **AI**: Handles AI-related operations.
- **Chat**: Handles operations related to chat functionality.
- **Backoffice**: Handles operations related to the backoffice functionality.
- **Common**: Contains common functionalities used across the application.

Each module is represented by a Django app with its own `models.py`, `views.py`, `tests.py`, and `apps.py` files.

## Frontend

The frontend of the application is built with Tailwind CSS. The configuration for Tailwind CSS is defined in the `tailwind.config.js` file.

## Tests

Tests for the application are written using Django's testing framework and are located in the `tests.py` files of each module.

## Other Files

There are several other files in the codebase that are used for various purposes. These include:

- **`manage.py`**: The main entry point for Django command-line utility.
- **[requirements](file:///Users/jbl2024/rectorat/cassandre/README.md#19%2C18-19%2C18)**: Contains the Python dependencies required by the application.
- **`docker-compose.yml`**: Defines the services that make up the application in a Docker environment.
- **`nginx.conf`**: The configuration file for Nginx, which is used as a reverse proxy for the application.
