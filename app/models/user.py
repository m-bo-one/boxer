from __future__ import division

import logging
import random
import json
import time

import gevent

from db import redis_db, local_db
from constants import ActionType, DirectionType, WeaponType, ArmorType, \
    RESURECTION_TIME, HEAL_TIME, HUMAN_HEALTH, MAX_AP
from app.assets.sprite import sprite_proto
from .weapon import Weapon


class UserModel(object):

    collision_pipeline = (
        'map_collision',
        # 'user_collision',
    )
    AP_stats = {}

    def __init__(self,
                 id=None,
                 x=0,
                 y=0,
                 speed=(3, 3),
                 action=ActionType.IDLE,
                 direction=DirectionType.LEFT,
                 armor=ArmorType.ENCLAVE_POWER_ARMOR,
                 weapon=WeaponType.NO_WEAPON,
                 health=100,
                 extra_data=None,
                 scores=0,
                 AP=10,
                 *args, **kwargs):

        self.id = id
        self.username = 'Enclave#%s' % id
        self.x = x
        self.y = y
        self.speed = speed
        self.action = action
        self.direction = direction
        self.armor = armor
        self.weapon = Weapon(weapon, self)
        self.health = health
        self.max_health = HUMAN_HEALTH
        self.scores = scores
        self._armors = [ArmorType.ENCLAVE_POWER_ARMOR]
        self._weapons = [Weapon(WeaponType.NO_WEAPON, self),
                         Weapon(WeaponType.M60, self)]

        self.width, self.height = self.size
        self.operations = kwargs.get('operations') or []
        self.AP = AP

        if not extra_data:
            extra_data = {}
        self.extra_data = extra_data

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
            'username': self.username,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'speed': self.speed,
            'action': self.action,
            'direction': self.direction,
            'armor': self.armor,
            'weapon': self.weapon.to_dict(),
            'health': self.health,
            'operations_blocked': self.operations_blocked,
            'animation': self.animation,
            'extra_data': self.extra_data,
            'updated_at': time.time(),
            'scores': self.scores,
            'max_health': self.max_health,
            'operations': self.operations,
            'AP': self.AP
        }

    @property
    def size(self):
        _sprite = sprite_proto.get((self.armor,
                                    self.weapon.name,
                                    self.action))
        return _sprite['frames']['width'], _sprite['frames']['height']

    @property
    def animation(self):
        return {
            'way': "_".join([self.action, self.direction]),
            'compound': sprite_proto.sp_key_builder(self.armor,
                                                    self.weapon.name,
                                                    self.action),
        }

    def __repr__(self):
        return '<UserModel: id - %s>' % self.id

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
            id=cls.generate_id(),
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

    def block_operation(self, type):
        self.operations.append({
            'type': type,
            'blocked_at': time.time()
        })

    def reg_map(self, size):
        local_db['map_size'][self.id] = size

    @property
    def coords(self):
        return (self.x, self.y)

    @property
    def is_full_health(self):
        return self.health == HUMAN_HEALTH

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
        try:
            if self.is_dead:
                return True

            ct = time.time()

            for operation in self.operations:
                if operation['type'] == 'shoot':
                    block_for = self.weapon.w.SHOOT_TIME
                elif operation['type'] == 'heal':
                    block_for = HEAL_TIME
                if ct - operation['blocked_at'] <= block_for:
                    return True
                else:
                    self.extra_data['sound_to_play'] = None
        except KeyError:
            return False
        else:
            return False

    def _delayed_command(self, delay, fname):

        def _callback():
            user = UserModel.get(self.id)
            getattr(user, fname)()

        return gevent.spawn_later(delay, _callback)

    @autosave
    def shoot(self):
        if (not self.weapon_in_hands or self.operations_blocked or
           self.AP - 5 < 0):
            return

        self.action = ActionType.FIRE
        self.block_operation('shoot')
        self.use_AP(5)
        self.extra_data['sound_to_play'] = 'm60-fire'

        detected = [other for other in self.__class__.all()
                    if other.id != self.id and not
                    other.is_dead and self.weapon.in_vision(other)]

        if detected:
            logging.info('Found users: %s', detected)
            self.weapon.shoot(detected)

        self._delayed_command(self.weapon.w.SHOOT_TIME, 'stop')
        self._delayed_command(1, 'restore_AP')

    @property
    def weapon_in_hands(self):
        return self.weapon.name != WeaponType.NO_WEAPON

    def attr_from_db(self, value):
        logging.info('Update attr: %s', value)
        return getattr(UserModel.get(self.id), value)

    @autosave
    def equip(self, type):
        logging.info('Current weapon: %s', self.weapon.name)

        if type == 'weapon' and self.weapon_in_hands:
            self.weapon = self._weapons[0]
        elif type == 'weapon':
            self.weapon = self._weapons[1]

        if type == 'armor':
            self.armor = self._armors[0]

    def use_AP(self, p):
        self.AP = self.attr_from_db('AP') - p
        if self.AP < 0:
            self.AP = 0

    def restore_AP(self):
        x = 0
        self.AP_stats.setdefault(self.id, [])
        if self.AP_stats[self.id]:
            gevent.killall(self.AP_stats[self.id])
        for _ in range(MAX_AP - self.AP):
            thread = self._delayed_command(x, 'incr_AP')
            self.AP_stats[self.id].append(thread)
            x += 1

    @autosave
    def incr_AP(self):
        self.AP = self.attr_from_db('AP') + 1
        if self.AP > MAX_AP:
            self.AP = MAX_AP

        print(self.AP)

    @autosave
    def got_hit(self, dmg):
        logging.info('Health before hit: %s', self.health)
        self.health = self.attr_from_db('health') - dmg
        logging.info('Health after hit: %s', self.health)
        if self.is_dead:
            self.kill()

    @autosave
    def heal(self, target=None):
        if not self.is_full_health and not self.operations_blocked and self.AP - 2 >= 0:
            if target is not None and target != self:
                raise NotImplementedError()
            else:
                # TODO: For future, add inventory and
                # replace heal of inventory stimulators
                logging.info('Health before heal: %s', self.health)
                self.health = random.randrange(10, 20, 1) + \
                    self.attr_from_db('health')
                logging.info('Health before heal: %s', self.health)

                self.action = ActionType.HEAL
                self.block_operation('heal')
                self.use_AP(2)

                if self.health > self.max_health:
                    self.health = self.max_health

                self._delayed_command(HEAL_TIME, 'stop')
                self._delayed_command(1, 'restore_AP')

    @autosave
    def kill(self):
        death_actions = [ActionType.DEATH_FROM_ABOVE]
        self.action = random.choice(death_actions)
        self.extra_data['resurection_time'] = RESURECTION_TIME

        self._delayed_command(RESURECTION_TIME, 'resurect')

    @autosave
    def resurect(self):
        self.health = self.max_health
        self.weapon = self._weapons[0]
        self.x = random.randint(0, local_db['map_size']['width'] - 100)
        self.y = random.randint(0, local_db['map_size']['height'] - 100)
        self.action = ActionType.IDLE
        self.direction = DirectionType.LEFT

        try:
            del self.extra_data['resurection_time']
        except KeyError:
            pass

    @autosave
    def stop(self):
        self.move('idle', self.direction)

    @autosave
    def move(self, action, direction):
        way = '_'.join([action, direction])
        logging.info('Current way: %s', way)
        logging.info('Current coords: %s', self.coords)

        x, y = self.coords

        self.action = action
        self.direction = direction

        logging.info('\n'
                     'Direction: %s\n'
                     'Action: %s\n'
                     'Weapon: %s\n',
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
