# cassandre

## architecture
- django

in docker
- postgresql
- minio
- redis
- qdrant

## setup (dev mode)

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

Run all:
```
$ ./start_all.sh
```

http://localhost:8000/search

## env vars
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
DJANGO_SUPERUSER_USERNAME=jerome
DJANGO_SUPERUSER_EMAIL=jerome@blondon.fr
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
