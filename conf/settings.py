import os

DEBUG = False
TEMPLATE_DEBUG = False

SITE_ADDRESS = ('127.0.0.1', 8080)
WEBSOCKET_ADDRESS = ('127.0.0.1', 9999)

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

MEDIA_PATH = os.path.join(PROJECT_PATH, 'media')
MEDIA_URL = '/media/'

STATIC_PATH = os.path.join(PROJECT_PATH, 'static')
STATIC_URL = '/static/'

ASSETS_PATH = os.path.join(STATIC_PATH, 'assets')
ASSETS_URL = os.path.join(STATIC_URL, 'assets/')

TEMPLATES_PATH = os.path.join(PROJECT_PATH, 'templates')

FPS = 60

DATABASES = {
    'default': {
        'DB': 'boxer',
        'HOST': '',
        'PORT': 27017,
        'POOL_MAX_SIZE': 100
    }
}
