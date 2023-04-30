from .base_settings import *

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = ['cassandre.services.jbl2024.com']

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

QDRANT_URL = os.environ.get('QDRANT_URL', 'http://localhost:6334')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True