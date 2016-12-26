from __future__ import division

import logging
import random
import json
import math

from db import redis_db, local_db
from constants import ActionType, DirectionType, WeaponType, ArmorType
from .sprite import sprite_proto, sp_key_builder


class WeaponVision(object):

    def __init__(self, user, R=200, alpha=30):
        self.user = user
        self.R = R
        self.alpha = alpha

    def to_dict(self):
        return {
            'alphas': self.alphas,
            'alphae': self.alphae,
            'R': self.R
        }

    def distance(self, p1, p2):
        result = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        print('distance: %s' % result)
        return result

    def is_inside_sector(self, other):
        point = other._vision._sector_center
        return bool(
            self.distance(self._sector_start, point) +
            self.distance(point, self._sector_end) ==
            self.distance(self._sector_start, self._sector_end))

    # def _are_clockwise(self, p1, p2):
    #     return -p1[0] * p2[1] + p1[1] * p2[0] > 0

    # def _is_within_radius(self, p):
    #     return p[0] ** 2 + p[1] ** 2 <= self.R

    # def is_inside_sector(self, other):
    #     point = other._vision._sector_center
    #     sector_start = self._sector_start
    #     sector_end = self._sector_end
    #     center = self._sector_center
    #     rel_point = (point[0] - center[0], point[1] - center[1])
    #     print('Check sector!')
    #     print('Sector start (x: %s, y: %s)' % sector_start)
    #     print('Sector end (x: %s, y: %s)' % sector_end)
    #     print('Sector center (x: %s, y: %s)' % center)
    #     is_in = bool(
    #         not self._are_clockwise(sector_start, rel_point) and
    #         self._are_clockwise(sector_end, rel_point) and
    #         self._is_within_radius(rel_point)
    #     )
    #     print('STATUS %s' % is_in)
    #     return is_in

    @property
    def alphas(self):
        if self.user.direction == 'left':
            return 180 - self.alpha
        elif self.user.direction == 'right':
            return -self.alpha
        elif self.user.direction == 'top':
            return -90 - self.alpha
        elif self.user.direction == 'bottom':
            return 90 - self.alpha

    @property
    def alphae(self):
        if self.user.direction == 'left':
            return 180 + self.alpha
        elif self.user.direction == 'right':
            return self.alpha
        elif self.user.direction == 'top':
            return -90 + self.alpha
        elif self.user.direction == 'bottom':
            return 90 + self.alpha

    @property
    def _sector_center(self):
        result = ((self.user.x + self.user.width) / 2,
                  (self.user.y + self.user.height) / 2)
        logging.info('Sector start coords: (%s, %s)' % result)
        return result

    @property
    def _sector_start(self):
        horde = 2 * self.R * math.sin(math.radians(self.alpha / 2))
        distance_to_horde = math.sqrt(self.R ** 2 - (horde / 2) ** 2)
        center = self._sector_center

        if self.user.direction == 'left':
            return (center[0] - distance_to_horde, center[1] + (horde / 2))
        elif self.user.direction == 'right':
            return (center[0] + distance_to_horde, center[1] - (horde / 2))
        elif self.user.direction == 'top':
            return (center[0] - (horde / 2), center[1] - distance_to_horde)
        elif self.user.direction == 'bottom':
            return (center[0] + (horde / 2), center[1] + distance_to_horde)

    @property
    def _sector_end(self):
        horde = 2 * self.R * math.sin(math.radians(self.alpha / 2))
        distance_to_horde = math.sqrt(self.R ** 2 - (horde / 2) ** 2)
        center = self._sector_center

        if self.user.direction == 'left':
            return (center[0] - distance_to_horde, center[1] - (horde / 2))
        elif self.user.direction == 'right':
            return (center[0] + distance_to_horde, center[1] + (horde / 2))
        elif self.user.direction == 'top':
            return (center[0] + (horde / 2), center[1] - distance_to_horde)
        elif self.user.direction == 'bottom':
            return (center[0] - (horde / 2), center[1] + distance_to_horde)

    @classmethod
    def patch_user(cls, user):
        user._vision = cls(user)


class UserModel(object):

    collision_pipeline = (
        'map_collision',
        'user_collision',
    )

    def __init__(self,
                 id=None,
                 x=0,
                 y=0,
                 speed=5,
                 action=ActionType.IDLE,
                 direction=DirectionType.LEFT,
                 armor=ArmorType.ENCLAVE_POWER_ARMOR,
                 weapon=WeaponType.NO_WEAPON,
                 armors=None,
                 weapons=None,
                 health=100,
                 sprites=None,
                 *args, **kwargs):

        self.id = id or self.generate_id()
        self.x = x
        self.y = y
        self.speed = speed
        self.action = action
        self.direction = direction
        self.armor = armor
        self.weapon = weapon
        self.health = health
        self.armors = [ArmorType.ENCLAVE_POWER_ARMOR] if not armors else armors
        self.weapons = [WeaponType.NO_WEAPON, WeaponType.M60] \
            if not weapons else weapons

        if not sprites:
            self.load_sprites()
        else:
            self.sprites = sprites

        self._current_sprite = self.sprites[sp_key_builder(self.armor,
                                                           self.weapon,
                                                           self.action)]
        self.width = self._current_sprite['frames']['width']
        self.height = self._current_sprite['frames']['height']

        WeaponVision.patch_user(self)

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
            'weapon': self.weapon,
            'health': self.health,
            'weapons': self.weapons,
            'armors': self.armors,
            'sprites': self.sprites,
            'vision': self._vision.to_dict()
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def load_sprites(self):
        self.sprites = {
            sp_key_builder(
                armor, weapon, action): (sprite_proto
                                         .clone((armor, weapon, action)))
            for armor in self.armors
            for weapon in self.weapons
            for action in [ActionType.IDLE, ActionType.WALK]}

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

    @autosave
    def shoot(self):
        self.health -= 1
        return self

    @autosave
    def equip(self, type):
        # FIXME: Hardcoded, need to fix in future
        logging.info('Current weapon: %s', self.weapon)

        if type == 'weapon' and self.weapon != WeaponType.NO_WEAPON:
            self.weapon = WeaponType.NO_WEAPON
        elif type == 'weapon':
            self.weapon = self.weapons[1]

        if type == 'armor':
            self.armor = self.armors[0]

    @autosave
    def move(self, action, direction):
        way = '_'.join([action, direction])
        logging.info('Current way: %s', way)
        logging.info('Current coords: %s', self.coords)

        x, y = self.coords

        self.action = action
        self.direction = direction

        logging.info('Direction %s, action %s, weapon %s',
                     self.direction, self.action, self.weapon)

        if way == 'walk_top':
            self.y -= self.speed

        elif way == 'walk_bottom':
            self.y += self.speed

        elif way == 'walk_right':
            self.x += self.speed

        elif way == 'walk_left':
            self.x -= self.speed

        if self.is_collide:
            self.x = x
            self.y = y

        for other in self.__class__.all():
            if self._vision.is_inside_sector(other):
                print('FOUND!')
