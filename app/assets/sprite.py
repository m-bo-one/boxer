# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import copy
import json
from conf import settings
from utils import await_greenlet, get_image, clear_dir
from constants import ActionType, DirectionType, WeaponType, ArmorType, \
    StatusType


class SpritePrototype(object):

    sp_key_builder = staticmethod(lambda armor, weapon, action: "%s-%s-%s" %
                                  (armor, weapon, action))

    def __init__(self):
        self._objects = {}
        if not os.path.exists(settings.ASSETS_SPRITE_PATH):
            os.mkdir(settings.ASSETS_PATH)
            os.mkdir(settings.ASSETS_SPRITE_PATH)
        clear_dir(settings.ASSETS_SPRITE_PATH)

    def register_object(self, name, obj):
        """Register an object"""
        self._objects[self.sp_key_builder(*name)] = obj
        with open(
            os.path.join(settings.ASSETS_SPRITE_PATH,
                         '%s.json' % self.sp_key_builder(*name)), 'w+'
        ) as outfile:
            json.dump(obj, outfile, indent=4)

    def get(self, name):
        return self._objects[self.sp_key_builder(*name)]

    def unregister_object(self, name):
        """Unregister an object"""
        del self._objects[self.sp_key_builder(*name)]

    def clone(self, name, **attr):
        """Clone a registered object and update inner attributes dictionary"""
        obj = copy.deepcopy(self._objects[self.sp_key_builder(*name)])
        obj.update(attr)
        return obj


class AnimatedSprite(object):
    """Compile animated sprite obj.
    Init params:
        [
            {
                'direction': 'rigth',
                'action': 'walk',
                'armor': 'power_armor',
                'weapon': 'knife',
                'count': 4,
                'speed': 0.3
            },

            ...
        ]
    """

    image_patterns = {
        'default': 'equipment/{armor}/{weapon}/{action}/{direction}.png',
        'death': 'equipment/{armor}/{action}/{direction}.png'
    }

    def __init__(self, action, direction, armor, weapon=None, count=0,
                 speed=0.2):
        if weapon:
            self.image_name = self.image_patterns['default'].format(
                armor=armor, weapon=weapon, action=action, direction=direction)
        else:
            self.image_name = self.image_patterns['default'].format(
                armor=armor, action=action, direction=direction)
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

sprite_proto.register_object(

    (ArmorType.ENCLAVE_POWER_ARMOR, WeaponType.NO_WEAPON, ActionType.WALK),

    AnimatedSprite.prepare_easeljs_data([
        {
            'direction': DirectionType.LEFT,
            'action': ActionType.WALK,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.NO_WEAPON,
            'count': 8,
        },
        {
            'direction': DirectionType.RIGHT,
            'action': ActionType.WALK,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.NO_WEAPON,
            'count': 8,
        },
        {
            'direction': DirectionType.TOP,
            'action': ActionType.WALK,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.NO_WEAPON,
            'count': 8,
        },
        {
            'direction': DirectionType.BOTTOM,
            'action': ActionType.WALK,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.NO_WEAPON,
            'count': 8,
        }

    ]))

sprite_proto.register_object(

    (ArmorType.ENCLAVE_POWER_ARMOR, WeaponType.NO_WEAPON, ActionType.IDLE),

    AnimatedSprite.prepare_easeljs_data([
        {
            'direction': DirectionType.LEFT,
            'action': ActionType.IDLE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.NO_WEAPON,
            'count': 12,
        },
        {
            'direction': DirectionType.RIGHT,
            'action': ActionType.IDLE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.NO_WEAPON,
            'count': 12,
        },
        {
            'direction': DirectionType.TOP,
            'action': ActionType.IDLE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.NO_WEAPON,
            'count': 12,
        },
        {
            'direction': DirectionType.BOTTOM,
            'action': ActionType.IDLE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.NO_WEAPON,
            'count': 12,
        }

    ]))

sprite_proto.register_object(

    (ArmorType.ENCLAVE_POWER_ARMOR, WeaponType.M60, ActionType.WALK),

    AnimatedSprite.prepare_easeljs_data([
        {
            'direction': DirectionType.LEFT,
            'action': ActionType.WALK,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 8,
        },
        {
            'direction': DirectionType.RIGHT,
            'action': ActionType.WALK,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 8,
        },
        {
            'direction': DirectionType.TOP,
            'action': ActionType.WALK,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 8,
        },
        {
            'direction': DirectionType.BOTTOM,
            'action': ActionType.WALK,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 8,
        }

    ]))

sprite_proto.register_object(

    (ArmorType.ENCLAVE_POWER_ARMOR, WeaponType.M60, ActionType.IDLE),

    AnimatedSprite.prepare_easeljs_data([
        {
            'direction': DirectionType.LEFT,
            'action': ActionType.IDLE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 10,
        },
        {
            'direction': DirectionType.RIGHT,
            'action': ActionType.IDLE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 10,
        },
        {
            'direction': DirectionType.TOP,
            'action': ActionType.IDLE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 10,
        },
        {
            'direction': DirectionType.BOTTOM,
            'action': ActionType.IDLE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 10,
        }

    ]))

sprite_proto.register_object(

    (ArmorType.ENCLAVE_POWER_ARMOR, WeaponType.M60, ActionType.FIRE),

    AnimatedSprite.prepare_easeljs_data([
        {
            'direction': DirectionType.LEFT,
            'action': ActionType.FIRE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 8,
        },
        {
            'direction': DirectionType.RIGHT,
            'action': ActionType.FIRE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 8,
        },
        {
            'direction': DirectionType.TOP,
            'action': ActionType.FIRE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 8,
        },
        {
            'direction': DirectionType.BOTTOM,
            'action': ActionType.FIRE,
            'armor': ArmorType.ENCLAVE_POWER_ARMOR,
            'weapon': WeaponType.M60,
            'count': 8,
        }

    ]))


for wp_type in WeaponType.__slots__:

    sprite_proto.register_object(

        (ArmorType.ENCLAVE_POWER_ARMOR, wp_type, ActionType.DEATH_FROM_ABOVE),

        AnimatedSprite.prepare_easeljs_data([
            {
                'direction': DirectionType.LEFT,
                'action': ActionType.DEATH_FROM_ABOVE,
                'armor': ArmorType.ENCLAVE_POWER_ARMOR,
                'weapon': WeaponType.NO_WEAPON,
                'count': 19,
            },
            {
                'direction': DirectionType.RIGHT,
                'action': ActionType.DEATH_FROM_ABOVE,
                'armor': ArmorType.ENCLAVE_POWER_ARMOR,
                'weapon': WeaponType.NO_WEAPON,
                'count': 19,
            },
            {
                'direction': DirectionType.TOP,
                'action': ActionType.DEATH_FROM_ABOVE,
                'armor': ArmorType.ENCLAVE_POWER_ARMOR,
                'weapon': WeaponType.NO_WEAPON,
                'count': 19,
            },
            {
                'direction': DirectionType.BOTTOM,
                'action': ActionType.DEATH_FROM_ABOVE,
                'armor': ArmorType.ENCLAVE_POWER_ARMOR,
                'weapon': WeaponType.NO_WEAPON,
                'count': 19,
            }

        ]))


for wp_type in WeaponType.__slots__:

    sprite_proto.register_object(

        (ArmorType.ENCLAVE_POWER_ARMOR, wp_type, ActionType.HEAL),

        AnimatedSprite.prepare_easeljs_data([
            {
                'direction': DirectionType.LEFT,
                'action': ActionType.HEAL,
                'armor': ArmorType.ENCLAVE_POWER_ARMOR,
                'weapon': WeaponType.NO_WEAPON,
                'count': 11,
                'speed': 0.2
            },
            {
                'direction': DirectionType.RIGHT,
                'action': ActionType.HEAL,
                'armor': ArmorType.ENCLAVE_POWER_ARMOR,
                'weapon': WeaponType.NO_WEAPON,
                'count': 11,
                'speed': 0.2
            },
            {
                'direction': DirectionType.TOP,
                'action': ActionType.HEAL,
                'armor': ArmorType.ENCLAVE_POWER_ARMOR,
                'weapon': WeaponType.NO_WEAPON,
                'count': 11,
                'speed': 0.2
            },
            {
                'direction': DirectionType.BOTTOM,
                'action': ActionType.HEAL,
                'armor': ArmorType.ENCLAVE_POWER_ARMOR,
                'weapon': WeaponType.NO_WEAPON,
                'count': 11,
                'speed': 0.2
            }

        ]))
