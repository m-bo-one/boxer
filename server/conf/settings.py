import os

DEBUG = True

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
SERVER_PATH = os.path.join(PROJECT_PATH, 'server')

SECRET_KEY = '12ddassdakfji234hf2hfh2iuhfi23hf2'

WEBSOCKET_ADDRESS = ('0.0.0.0', 9999)
ZMQ_ADDRESS = ('127.0.0.1', 5560)

ASSETS_PATH = os.path.join(PROJECT_PATH, 'client/assets')
ASSETS_URL = '/assets/'

SRC_PATH = os.path.join(PROJECT_PATH, 'client/src')
SRC_URL = '/src/'

ASSETS_SPRITE_PATH = os.path.join(ASSETS_PATH, 'sprites')
ASSETS_SPRITE_URL = os.path.join(ASSETS_URL, 'sprites/')

ASSETS_SOUND_PATH = os.path.join(ASSETS_PATH, 'sounds')
ASSETS_SOUND_URL = os.path.join(ASSETS_URL, 'sounds/')
