# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import copy
from conf import settings
from utils import await_greenlet, get_image


sp_key_builder = lambda armor, weapon, action: "%s:%s:%s" % (armor, weapon, action)


class SpritePrototype(object):

    def __init__(self):
        self._objects = {}

    def register_object(self, name, obj):
        """Register an object"""
        self._objects[sp_key_builder(*name)] = obj

    def unregister_object(self, name):
        """Unregister an object"""
        del self._objects[sp_key_builder(*name)]

    def clone(self, name, **attr):
        """Clone a registered object and update inner attributes dictionary"""
        obj = copy.deepcopy(self._objects[sp_key_builder(*name)])
        obj.update(attr)
        return obj


class AnimatedSprite(object):
    """Created animated sprite.
    Init params:
        [
            {
                'direction': 'rigth',
                'action': 'walk',
                'armor': 'power_armor',
                'weapon': 'knife',
                'count': 4,
                'speed': 0.5
            },

            ...
        ]
    """

    image_pattern = 'equipment/{armor}/{weapon}/{action}/{direction}.png'

    def __init__(self, action, direction, armor, weapon, count, speed):
        self.image_name = self.image_pattern.format(
            armor=armor, weapon=weapon, action=action, direction=direction)
        self.action = action
        self.direction = direction
        self.count = count
        self.speed = speed

        self.image = await_greenlet(get_image, self.image_name)
        self.image_url = os.path.join(settings.MEDIA_URL, self.image_name)
        self.height = self.image.height
        # width calculated dynamicaly through count
        self.width = self.image.width / float(count)
        self.size = (self.width, self.height)

    @property
    def way(self):
        return "_".join([self.action, self.direction])

    @classmethod
    def prepare_easeljs_data(cls, images_info):
        prev_count = 0
        resp_data = {}

        resp_data.setdefault('images', [])
        resp_data.setdefault('frames', {})
        resp_data.setdefault('animations', {})

        for image_info in images_info:
            sprite = cls(**image_info)
            prev_count += sprite.count
            resp_data['images'].append(sprite.image_url)
            resp_data['frames'] = {
                'height': sprite.height,
                'width': sprite.width,
                'count': prev_count
            }
            resp_data['animations'][sprite.way] = {
                'frames': list(range(prev_count - sprite.count, prev_count)),
                'speed': sprite.speed
            }
        return resp_data


sprite_proto = SpritePrototype()

sprite_proto.register_object(('enclave_power_armor', 'no_weapon', 'walk'), AnimatedSprite.prepare_easeljs_data([
    {
        'direction': 'left',
        'action': 'walk',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 8,
        'speed': 0.3
    },
    {
        'direction': 'right',
        'action': 'walk',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 8,
        'speed': 0.3
    },
    {
        'direction': 'top',
        'action': 'walk',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 8,
        'speed': 0.3
    },
    {
        'direction': 'bottom',
        'action': 'walk',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 8,
        'speed': 0.3
    }
]))

sprite_proto.register_object(('enclave_power_armor', 'no_weapon', 'idle'), AnimatedSprite.prepare_easeljs_data([
    {
        'direction': 'left',
        'action': 'idle',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 12,
        'speed': 0.3
    },
    {
        'direction': 'right',
        'action': 'idle',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 12,
        'speed': 0.3
    },
    {
        'direction': 'top',
        'action': 'idle',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 12,
        'speed': 0.3
    },
    {
        'direction': 'bottom',
        'action': 'idle',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 12,
        'speed': 0.3
    }
]))

sprite_proto.register_object(('enclave_power_armor', 'flamer', 'walk'), AnimatedSprite.prepare_easeljs_data([
    {
        'direction': 'left',
        'action': 'walk',
        'armor': 'enclave_power_armor',
        'weapon': 'flamer',
        'count': 8,
        'speed': 0.3
    },
    {
        'direction': 'right',
        'action': 'walk',
        'armor': 'enclave_power_armor',
        'weapon': 'flamer',
        'count': 8,
        'speed': 0.3
    },
    {
        'direction': 'top',
        'action': 'walk',
        'armor': 'enclave_power_armor',
        'weapon': 'flamer',
        'count': 8,
        'speed': 0.3
    },
    {
        'direction': 'bottom',
        'action': 'walk',
        'armor': 'enclave_power_armor',
        'weapon': 'flamer',
        'count': 8,
        'speed': 0.3
    }
]))

sprite_proto.register_object(('enclave_power_armor', 'flamer', 'idle'), AnimatedSprite.prepare_easeljs_data([
    {
        'direction': 'left',
        'action': 'idle',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 12,
        'speed': 0.3
    },
    {
        'direction': 'right',
        'action': 'idle',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 12,
        'speed': 0.3
    },
    {
        'direction': 'top',
        'action': 'idle',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 12,
        'speed': 0.3
    },
    {
        'direction': 'bottom',
        'action': 'idle',
        'armor': 'enclave_power_armor',
        'weapon': 'no_weapon',
        'count': 12,
        'speed': 0.3
    }
]))


sprite_proto.register_object(('enclave_power_armor', 'flamer', 'fire'), AnimatedSprite.prepare_easeljs_data([
    {
        'direction': 'left',
        'action': 'fire',
        'armor': 'enclave_power_armor',
        'weapon': 'flamer',
        'count': 3,
        'speed': 1
    },
    {
        'direction': 'right',
        'action': 'fire',
        'armor': 'enclave_power_armor',
        'weapon': 'flamer',
        'count': 3,
        'speed': 1
    }
]))
