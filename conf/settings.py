import os

DEBUG = True
TEMPLATE_DEBUG = True
GAME = {
    'FPS': 60,
    'CELL_SIZE': 32
}

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SERVER_PATH = os.path.join(PROJECT_PATH, 'server')
CLIENT_PATH = os.path.join(PROJECT_PATH, 'client')

SECRET_KEY = '12ddassdakfji234hf2hfh2iuhfi23hf2'

SITE_ADDRESS = ('0.0.0.0', 8080)
WEBSOCKET_ADDRESS = ('0.0.0.0', 9999)
ZMQ_REP_HOST = os.getenv('ZMQ_REP_HOST', '127.0.0.1')
ZMQ_REP_PORT = 5560

ASSETS_PATH = os.path.join(CLIENT_PATH, 'assets')
ASSETS_URL = '/assets/'

SRC_PATH = os.path.join(CLIENT_PATH, 'src')
SRC_URL = '/src/'

ASSETS_SPRITE_PATH = os.path.join(ASSETS_PATH, 'sprites')
ASSETS_SPRITE_URL = os.path.join(ASSETS_URL, 'sprites/')

ASSETS_SOUND_PATH = os.path.join(ASSETS_PATH, 'sounds')
ASSETS_SOUND_URL = os.path.join(ASSETS_URL, 'sounds/')


DATABASES = {
    'redis': {
        'HOST': os.getenv('REDIS_HOST', '127.0.0.1'),
        'PORT': int(os.getenv('REDIS_PORT', 6379)),
        'NAME': 0,
        'POOL_MAX_SIZE': 100
    },
    'mongo': {
        'HOST': os.getenv('MONGO_HOST', '127.0.0.1'),
        'PORT': int(os.getenv('MONGO_PORT', 27017)),
        'NAME': 'boxer',
        'POOL_MAX_SIZE': 100
    }
}

SESSION_OPTS = {
    'session.cookie_expires': True,
    'session.encrypt_key': SECRET_KEY,
    'session.httponly': True,
    'session.timeout': 3600 * 24,  # 1 day
    'session.type': 'cookie',
    'session.validate_key': True
}

try:
    from .settings_local import *
except ImportError:
    pass
