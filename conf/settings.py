import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
FPS = 60

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SERVER_PATH = os.path.join(PROJECT_PATH, 'server')
CLIENT_PATH = os.path.join(PROJECT_PATH, 'client')

SECRET_KEY = '12ddassdakfji234hf2hfh2iuhfi23hf2'

SITE_ADDRESS = ('127.0.0.1', 8080)
WEBSOCKET_ADDRESS = ('127.0.0.1', 9999)
ZMQ_ADDRESS = ('127.0.0.1', 5560)

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
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'NAME': 0
    },
    'mongo': {
        'HOST': '127.0.0.1',
        'PORT': 27017,
        'NAME': 'boxer'
    }
}
