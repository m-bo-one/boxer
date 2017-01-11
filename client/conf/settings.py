import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SITE_ADDRESS = ('0.0.0.0', 8080)

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

ASSETS_PATH = os.path.join(PROJECT_PATH, 'assets')
ASSETS_URL = '/assets/'

SRC_PATH = os.path.join(PROJECT_PATH, 'src')
SRC_URL = '/src/'

FPS = 60
