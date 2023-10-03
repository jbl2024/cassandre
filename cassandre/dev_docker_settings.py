from .base_settings import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cassandre_dev',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}

QDRANT_URL = "http://qdrant:6333"

INSTALLED_APPS.append('django_browser_reload')
MIDDLEWARE.append('django_browser_reload.middleware.BrowserReloadMiddleware')
MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}
CELERY_BROKER_URL = "redis://redis:6379"
WEBSOCKET_URL = 'ws://0.0.0.0:8000'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
