import json
import os

from .sprite import sprite_proto
from .sound import sound_proto

from conf import settings

with open(
    os.path.join(settings.PROJECT_PATH, 'manifest.json'), 'w+'
) as outfile:
    data = {}
    data.setdefault('path', '')
    data.setdefault('manifest', [])
    for key, obj in sprite_proto._objects.iteritems():
        data['manifest'].append({
            'id': key,
            'src': '%s.json' % os.path.join(settings.ASSETS_SPRITE_URL, key),
            'type': 'spritesheet'
        })
    for key, obj in sound_proto._objects.iteritems():
        data['manifest'].append(obj)
    # HARDCODED REPLACE IN FUTURE
    data['manifest'].append({
        'id': 'active-AP',
        'src': os.path.join(settings.MEDIA_URL, 'active_AP.png'),
        'type': 'image'
    })
    data['manifest'].append({
        'id': 'map',
        'src': os.path.join(settings.MEDIA_URL, 'map.png'),
        'type': 'image'
    })
    json.dump(data, outfile, indent=4)
