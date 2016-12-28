# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import copy
from conf import settings
from constants import ActionType, WeaponType


sd_key_builder = (lambda tname, aname: "%s-%s" % (tname, aname))


class SoundPrototype(object):

    def __init__(self):
        self._objects = {}

    def register_object(self, name, obj):
        """Register an object"""
        self._objects[sd_key_builder(*name)] = obj

    def unregister_object(self, name):
        """Unregister an object"""
        del self._objects[sd_key_builder(*name)]

    def clone(self, name, **attr):
        """Clone a registered object and update inner attributes dictionary"""
        obj = copy.deepcopy(self._objects[sd_key_builder(*name)])
        obj.update(attr)
        return obj


class Sound(object):
    """Compile sound obj.
    """

    sound_pattern = 'sounds/{type}/{tname}/{aname}.ogg'

    def __init__(self, type, tname, aname):
        self.sound_name = self.sound_pattern.format(
            type=type, tname=tname, aname=aname)
        self.type = 'weapons'
        self.tname = tname
        self.aname = aname

        self.sound_url = os.path.join(settings.MEDIA_URL, self.sound_name)

    @classmethod
    def prepare_easeljs_data(cls, sound_info):
        sound = cls(**sound_info[0])
        resp_data = {}
        resp_data['id'] = sd_key_builder(sound.tname, sound.aname)
        resp_data['src'] = sound.sound_url
        resp_data['type'] = 'sound'
        return resp_data


sound_proto = SoundPrototype()

sound_proto.register_object(

    (WeaponType.M60, ActionType.FIRE),

    Sound.prepare_easeljs_data([
        {
            "type": "weapons",
            "tname": WeaponType.M60,
            "aname": ActionType.FIRE
        }
    ]))
