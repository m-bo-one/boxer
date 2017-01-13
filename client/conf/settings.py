import os

DEBUG = True
TEMPLATE_DEBUG = True

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

SITE_ADDRESS = ('0.0.0.0', 8080)
ZMQ_ADDRESS = ('127.0.0.1', 5560)

CLIENT_PATH = os.path.join(PROJECT_PATH, 'client')

ASSETS_PATH = os.path.join(CLIENT_PATH, 'assets')
ASSETS_URL = '/assets/'

SRC_PATH = os.path.join(CLIENT_PATH, 'src')
SRC_URL = '/src/'

FPS = 60
