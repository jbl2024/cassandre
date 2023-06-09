from .base_settings import *

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = ['cassandre.services2.jbl2024.com']
CSRF_TRUSTED_ORIGINS = ['https://cassandre.services2.jbl2024.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'cassandre_prod'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

QDRANT_URL = os.environ.get('QDRANT_URL', 'http://localhost:6333')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

MEDIA_ROOT = '/media'
MEDIA_URL = '/media/'

CELERY_BROKER_URL= os.environ.get('CELERY_BROKER_URL')

# Index settings
SPLIT_CHUNK_SIZE = int(os.environ.get('SPLIT_CHUNK_SIZE', 1000))
SPLIT_CHUNK_OVERLAP = int(os.environ.get('SPLIT_CHUNK_OVERLAP', 100))

WEBSOCKET_URL = os.environ.get('WEBSOCKET_URL')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('CHANNEL_REDIS')],
        },
    },
}