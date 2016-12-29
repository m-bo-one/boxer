from __future__ import division

import logging
import random
import json
import time

from db import redis_db, local_db
from constants import ActionType, DirectionType, WeaponType, ArmorType, \
    SHOOT_DELAY
from app.assets.sprite import sprite_proto
from .weapon import Weapon


class UserModel(object):

    collision_pipeline = (
        'map_collision',
        # 'user_collision',
    )

    def __init__(self,
                 id=None,
                 x=0,
                 y=0,
                 speed=(4, 4),
                 action=ActionType.IDLE,
                 direction=DirectionType.LEFT,
                 armor=ArmorType.ENCLAVE_POWER_ARMOR,
                 weapon=WeaponType.NO_WEAPON,
                 health=100,
                 extra_data=None,
                 *args, **kwargs):

        self.id = id or self.generate_id()
        self.x = x
        self.y = y
        self.speed = speed
        self.action = action
        self.direction = direction
        self.armor = armor
        self.weapon = Weapon(weapon)
        self.health = health
        self._armors = [ArmorType.ENCLAVE_POWER_ARMOR]
        self._weapons = [Weapon(WeaponType.NO_WEAPON), Weapon(WeaponType.M60)]

        _sprite = sprite_proto.clone((self.armor,
                                      self.weapon.name,
                                      self.action))
        self.width = _sprite['frames']['width']
        self.height = _sprite['frames']['height']

        if not extra_data:
            extra_data = {}
        self.extra_data = extra_data

    def switchWeapon(self, weapon):
        self.weapon = weapon

    def save(self):
        return redis_db.hset('users', self.id, self.to_json())

    @classmethod
    def get(cls, id):
        return cls(**json.loads(redis_db.hget('users', id)))

    @classmethod
    def delete(cls, id=None):
        if not id:
            return redis_db.delete('users')
        return redis_db.hdel('users', id)

    @classmethod
    def all(cls, to_obj=True):
        users = redis_db.hgetall('users')
        if to_obj:
            return (cls(**json.loads(user)) for user in users.itervalues())
        return users

    @classmethod
    def get_users_map(cls):
        return cls.all(False)

    def to_dict(self):
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'speed': self.speed,
            'action': self.action,
            'direction': self.direction,
            'armor': self.armor,
            'weapon': {
                'name': self.weapon.name,
                'vision': self.weapon.get_vision_params(self.direction)
            },
            'health': self.health,
            'operations_blocked': self.operations_blocked,
            'extra_data': self.extra_data
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @property
    def is_dead(self):
        return bool(self.health <= 0)

    @staticmethod
    def generate_id():
        return redis_db.incr('users:uids')

    @classmethod
    def register_user(cls, socket, **kwargs):
        user = cls(
            x=random.randint(0, local_db['map_size']['width'] - 100),
            y=random.randint(0, local_db['map_size']['height'] - 100),
        )
        user.save()
        local_db['socket2uid'][socket] = user.id
        local_db['uid2socket'][user.id] = socket
        return user

    @classmethod
    def unregister_user(cls, socket):
        try:
            user_id = local_db['socket2uid'][socket]
            del local_db['socket2uid'][socket]
            del local_db['uid2socket'][user_id]
            cls.delete(user_id)
        except KeyError:
            user_id = None

        return user_id

    @property
    def coords(self):
        return (self.x, self.y)

    @property
    def is_collide(self):
        result = False
        for col_func in self.collision_pipeline:
            coll_func = getattr(self, col_func, None)
            if callable(coll_func):
                result = coll_func()
                if result:
                    break

        return result

    def map_collision(self):
        if (self.x > local_db['map_size']['width'] - 100 or self.x < 0 or
           self.y > local_db['map_size']['height'] - 100 or self.y < 0):
            return True
        return False

    def user_collision(self):
        for other in self.__class__.all():
            if (self.id != other.id and self.x < other.x + other.width and
               self.x + self.width > other.x and
               self.y < other.y + other.height and
               self.height + self.y > other.y):
                return True
        return False

    def autosave(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.save()
            return result
        return wrapper

    @property
    def operations_blocked(self):
        if self.extra_data.get('shoot_timestamp'):
            ts = self.extra_data['shoot_timestamp']
            if (time.time() - ts) <= SHOOT_DELAY:
                return True
            else:
                self.extra_data['sound_to_play'] = None
        return False

    @autosave
    def shoot(self):
        # FIXME: This section very hardcoded, need to refactor here:
        # ~~1) Damage remove from here, make it in weapon class or
        # something similar;
        # 2) Detection change on section finding (note for future);
        # ~~3) Logic of damage distribution remove from here;

        detected = []

        if self.weapon_in_hands:

            self.action = ActionType.FIRE
            self.extra_data['shoot_timestamp'] = time.time()
            self.extra_data['sound_to_play'] = 'm60-fire'

            detected = [other for other in self.__class__.all()
                        if other.id != self.id and
                        self.weapon.in_vision(self, other)]

            if detected:
                self.weapon.shoot(detected)

        return detected

    @property
    def weapon_in_hands(self):
        return self.weapon.name != WeaponType.NO_WEAPON

    @autosave
    def equip(self, type):
        logging.info('Current weapon: %s', self.weapon.name)

        if type == 'weapon' and self.weapon_in_hands:
            self.weapon = self._weapons[0]
        elif type == 'weapon':
            self.weapon = self._weapons[1]

        if type == 'armor':
            self.armor = self._armors[0]

    @autosave
    def move(self, action, direction):
        way = '_'.join([action, direction])
        logging.info('Current way: %s', way)
        logging.info('Current coords: %s', self.coords)

        x, y = self.coords

        self.action = action
        self.direction = direction

        logging.info('Direction %s, action %s, weapon %s',
                     self.direction, self.action, self.weapon.name)

        if way == 'walk_top':
            self.y -= self.speed[1]

        elif way == 'walk_bottom':
            self.y += self.speed[1]

        elif way == 'walk_right':
            self.x += self.speed[0]

        elif way == 'walk_left':
            self.x -= self.speed[0]

        if self.is_collide:
            self.x = x
            self.y = y
