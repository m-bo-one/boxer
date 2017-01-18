import json
from enum import IntEnum, Enum

from ..weapons import Weapon
from ..armors import Armor

from conf import settings
from db import redis_db
import constants as const


def field_extractor(inst):
    data = {}
    for field in inst.fields:
        value = getattr(inst, field)
        if isinstance(value, (Enum, IntEnum)):
            value = value.value
        elif isinstance(value, (Weapon, Armor)):
            value = value.name.value
        data[field] = value
    return data


class CmdModel(object):

    fields = ('id', 'x', 'y', 'action', 'direction')

    def __init__(self, id, character_id, x, y, action, direction):
        self.id = id
        self.character_id = int(character_id)
        self.x = x
        self.y = y
        self.action = const.Action(action)
        self.direction = const.Direction(direction)

    def __repr__(self):
        return '<CmdModel: id - %s>' % self.id

    @classmethod
    def create(cls, character_id,
               x=settings.GAME['CELL_SIZE'] / 2,
               y=settings.GAME['CELL_SIZE'] / 2,
               action=const.Action.Breathe,
               direction=const.Direction.W):
        cmd = cls(id=None, character_id=character_id, x=x, y=y,
                  action=action, direction=direction)
        cmd.save()
        return cmd

    def to_dict(self):
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'action': self.action,
            'direction': self.direction,
        }

    def to_json(self):
        return json.dumps(field_extractor(self))

    def save(self):
        if not self.id:
            self.id = redis_db.incr('cmds:ids')
        return redis_db.rpush('cmds:%s' % self.character_id, self.to_json())

    @classmethod
    def last(cls, character_id):
        try:
            cmd = redis_db.lrange('cmds:%s' % character_id, -1, -1)[0]
            return cls(character_id=character_id, **json.loads(cmd))
        except IndexError:
            pass

    @classmethod
    def delete(cls):
        keys = redis_db.keys('cmds:*')
        if keys:
            return redis_db.delete(*[key for key in keys if key != 'ids'])
        return 0

    @classmethod
    def get_last_or_create(cls, character_id):
        if character_id is None:
            raise TypeError("Can't be None")
        cmd = CmdModel.last(character_id)
        if not cmd:
            cmd = CmdModel.create(character_id)
        return cmd
