import json
import os

from .sprites import sprite_proto
from .sounds import sound_proto
from .tiles import TiledReader

from conf import settings

# with open(
#     os.path.join(settings.ASSETS_PATH, 'manifest.json'), 'w+'
# ) as outfile:
#     data = {}
#     data.setdefault('path', '')
#     data.setdefault('manifest', [])
#     for key, obj in sprite_proto._objects.iteritems():
#         data['manifest'].append({
#             'id': key,
#             'src': '%s.json' % os.path.join(settings.ASSETS_SPRITE_URL, key),
#             'type': 'spritesheet'
#         })
#     for key, obj in sound_proto._objects.iteritems():
#         data['manifest'].append(obj)
#     # HARDCODED REPLACE IN FUTURE
#     data['manifest'].append({
#         'id': 'active-AP',
#         'src': os.path.join(settings.ASSETS_URL, 'active_AP.png'),
#         'type': 'image'
#     })
#     data['manifest'].append({
#         'id': 'map',
#         'src': os.path.join(settings.ASSETS_URL, 'map.png'),
#         'type': 'image'
#     })
#     json.dump(data, outfile, indent=4)

TiledReader.read_and_add_collision(
    os.path.join(settings.SERVER_PATH, 'map.tmx'))
