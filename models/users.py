from __future__ import division

import logging
import random
import json
import math
import time

import gevent

from db import redis_db, local_db
from constants import ActionType, DirectionType, WeaponType, ArmorType, \
    SHOOT_DELAY
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

    def is_inside_sector(self, other):
        def are_clockwise(center, radius, angle, point2):
            point1 = (
                (center[0] + radius) * math.cos(math.radians(angle)),
                (center[1] + radius) * math.sin(math.radians(angle))
            )
            return bool(-point1[0] * point2[1] + point1[1] * point2[0] > 0)

        points = [
            other._vision._sector_center,
            # other.coords,
            (other.x + (other.width / 2), other.y),
            # (other.x + other.width, other.y),
            # (other.x, other.y + (other.height / 2)),
            # (other.x, other.y + other.height),
            (other.x + (other.width / 2), other.y + other.height),
            # (other.x + other.width, other.y + other.height),
            # (other.x + other.width, other.y + (other.height / 2)),
        ]
        center = self.user._vision._sector_center
        radius = self.R
        angle1 = self.alphas
        angle2 = self.alphae

        logging.debug('Points: %s', points)
        logging.debug('Width: %s', other.width)
        logging.debug('Height: %s', other.height)

        for point in points:
            rel_point = (point[0] - center[0], point[1] - center[1])

            logging.debug('--------------')
            logging.debug('Search point - x:%s, y:%s' % point)
            logging.debug('Radius center - x:%s, y:%s' % center)
            logging.debug('Radius length - %s' % radius)
            logging.debug('Angle start - %s' % self.alphas)
            logging.debug('Angle end - %s' % self.alphae)
            logging.debug('Point diff - x:%s, y:%s' % rel_point)
            logging.debug('--------------')

            is_detected = bool(
                not are_clockwise(center, radius, angle1, rel_point) and
                are_clockwise(center, radius, angle2, rel_point) and
                (rel_point[0] ** 2 + rel_point[1] ** 2 <= radius ** 2))
            if is_detected:
                return True
        else:
            return False

    @property
    def alphas(self):
        alpha = self.alpha / 2
        if self.user.direction == 'left':
            return 180 - alpha
        elif self.user.direction == 'right':
            return -alpha
        elif self.user.direction == 'top':
            return -90 - alpha
        elif self.user.direction == 'bottom':
            return 90 - alpha

    @property
    def alphae(self):
        alpha = self.alpha / 2
        if self.user.direction == 'left':
            return 180 + alpha
        elif self.user.direction == 'right':
            return alpha
        elif self.user.direction == 'top':
            return -90 + alpha
        elif self.user.direction == 'bottom':
            return 90 + alpha

    @property
    def _sector_center(self):
        result = (self.user.x + (self.user.width / 2),
                  self.user.y + (self.user.height / 2))
        logging.info('Sector start coords: (%s, %s)' % result)
        return result

    @classmethod
    def patch_user(cls, user):
        user._vision = cls(user)


class UserModel(object):

    collision_pipeline = (
        'map_collision',
        # 'user_collision',
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
                 extra_data=None,
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

        if not extra_data:
            extra_data = {}
        self.extra_data = extra_data

        # FIXME: This need to be removed and changed in something appropriate
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
        data = {
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
            'vision': self._vision.to_dict(),
            'operations_blocked': self.operations_blocked,
            'extra_data': self.extra_data
        }
        return data

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
        self.sprites[sp_key_builder(
            ArmorType.ENCLAVE_POWER_ARMOR,
            WeaponType.M60,
            ActionType.FIRE)] = sprite_proto.clone(
            (ArmorType.ENCLAVE_POWER_ARMOR, WeaponType.M60, ActionType.FIRE))

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
            return bool(
                (time.time() - self.extra_data['shoot_timestamp']) <=
                SHOOT_DELAY)
        return False

    @autosave
    def shoot(self):
        # FIXME: This section very hardcoded, need to refactor here:
        # 1) Damage remove from here, make it in weapon class or
        # something similar;
        # 2) Detection change on section finding (note for future);
        # 3) Logic of damage distribution remove from here;
        detected = []
        if not self.weapon_in_hands:
            return detected

        self.action = ActionType.FIRE
        self.extra_data['shoot_timestamp'] = time.time()

        logging.info('Direction %s, action %s, weapon %s',
                     self.direction, self.action, self.weapon)
        dmg = 40  # hardcoded
        for other in self.__class__.all():
            if other.id != self.id:
                if self._vision.is_inside_sector(other):
                    detected.append(other)

        def _det_update(user, calc_damage):
            user.health -= calc_damage
            user.save()

        if detected:
            calc_damage = int(dmg / len(detected))
            gevent.joinall([
                gevent.spawn(_det_update(user, calc_damage))
                for user in detected])

        return detected

    @property
    def weapon_in_hands(self):
        return self.weapon != WeaponType.NO_WEAPON

    @autosave
    def equip(self, type):
        # FIXME: Hardcoded, need to fix in future
        logging.info('Current weapon: %s', self.weapon)

        if type == 'weapon' and self.weapon_in_hands:
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
