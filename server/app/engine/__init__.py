import os

from .tiles import TiledReader

from conf import settings

TiledReader.read_and_add_collision(
    os.path.join(settings.ASSETS_PATH, 'map.tmx'))
