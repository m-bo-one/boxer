from __future__ import division

import logging
import random
import json
import time

import gevent

from db import redis_db, local_db
from constants import (
    ActionType, DirectionType, WeaponType, ArmorType,
    RESURECTION_TIME, HEAL_TIME, HUMAN_HEALTH, MAX_AP, FIRE_AP, HEAL_AP,
    HUMAN_SIZE)
from app.assets.sprite import sprite_proto
from .weapon import Weapon
from ..collider import obj_update, spatial_hash, CollisionManager


class UserModel(object):

    collision_pipeline = (
        'map_collision',
        'user_collision',
    )
    AP_stats = {}

    def __init__(self,
                 id=None,
                 x=16,
                 y=16,
                 speed=(2, 2),
                 action=ActionType.IDLE,
                 direction=DirectionType.LEFT,
                 armor=ArmorType.ENCLAVE_POWER_ARMOR,
                 weapon=WeaponType.NO_WEAPON,
                 health=100,
                 extra_data=None,
                 scores=0,
                 AP=10,
                 *args, **kwargs):
        self._update(id, x, y, speed, action, direction, armor, weapon,
                     health, extra_data, scores, AP, *args, **kwargs)

    def _update(self, id, x, y, speed, action, direction, armor, weapon,
                health, extra_data, scores, AP, *args, **kwargs):
        self.id = id
        self.username = 'Enclave#%s' % id
        self.speed = speed
        self.x = x
        self.y = y
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
        self.cm = CollisionManager(self, pipelines=self.collision_pipeline)

    def save(self):
        return redis_db.hset('users', self.id, self.to_json())

    def update(self):
        with obj_update(self):
            self._update(**json.loads(redis_db.hget('users', self.id)))

    @classmethod
    def get(cls, id, to_obj=True):
        if to_obj:
            return cls(**json.loads(redis_db.hget('users', id)))
        return json.loads(redis_db.hget('users', id))

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
            'pivot': self.pivot,
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
    def pivot(self):
        return {
            "x": self.x + self.width / 2,
            "y": (self.y + 2 * self.height / 3 + 10)
        }

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
    def create(cls, **kwargs):
        user = cls(id=cls.generate_id())
        spatial_hash.insert_object_for_point(user.pivot, user)
        user.save()
        print('Init %s' % user.id)
        return user

    def remove(self):
        try:
            user_id = self.id
            UserModel._kill_AP_threads(user_id)
            self.update()
            spatial_hash.remove_obj_by_point(self.pivot, self)
            del self
            UserModel.delete(user_id)
        except KeyError:
            user_id = None

        return user_id

    def block_operation(self, type):
        self.operations.append({
            'type': type,
            'blocked_at': time.time()
        })

    @property
    def coords(self):
        return (self.x, self.y)

    @property
    def is_full_health(self):
        return self.health == HUMAN_HEALTH

    def autosave(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.save()
            self.update()
            return result
        return wrapper

    @property
    def operations_blocked(self):
        try:
            if self.is_dead:
                return True

            ct = time.time()

            for i, operation in enumerate(self.operations[:]):
                if operation['type'] == 'shoot':
                    block_for = self.weapon.w.SHOOT_TIME
                elif operation['type'] == 'heal':
                    block_for = HEAL_TIME
                if ct - operation['blocked_at'] <= block_for:
                    return True
                else:
                    del self.operations[i]
                    self.extra_data['sound_to_play'] = None
        except KeyError:
            return False
        else:
            return False

    def _delayed_command(self, delay, fname):

        def _callback():
            self.update()
            getattr(self, fname)()

        return gevent.spawn_later(delay, _callback)

    @autosave
    def shoot(self):
        if all([
            self.weapon_in_hands,
            not self.operations_blocked,
            self.AP - FIRE_AP >= 0
        ]):
            self.action = ActionType.FIRE
            self.block_operation('shoot')
            self.use_AP(FIRE_AP)
            self.extra_data['sound_to_play'] = self.weapon.w.SOUNDS['fire']

            detected = [other for other in local_db['users']
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
        user_dict = UserModel.get(self.id, False)
        return user_dict.get(value)

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
        UserModel._kill_AP_threads(self.id)
        for _ in range(MAX_AP - self.AP):
            thread = self._delayed_command(x, 'incr_AP')
            self.AP_stats[self.id].append(thread)
            x += 1

    @classmethod
    def _kill_AP_threads(cls, id):
        cls.AP_stats.setdefault(id, [])
        if cls.AP_stats[id]:
            gevent.killall(cls.AP_stats[id])
            cls.AP_stats[id] = []

    @autosave
    def incr_AP(self):
        self.AP = self.attr_from_db('AP') + 1
        if self.AP > MAX_AP:
            self.AP = MAX_AP

        logging.info("ID: %s- AP: %s" % (self.id, self.AP))

    @autosave
    def got_hit(self, dmg):
        logging.info('Health before hit: %s', self.health)
        self.health = self.attr_from_db('health') - dmg
        logging.info('Health after hit: %s', self.health)
        if self.is_dead:
            self.kill()
            return 1
        return 0

    @autosave
    def heal(self, target=None):
        if all([
            not self.is_full_health,
            not self.operations_blocked,
            self.AP - HEAL_AP >= 0
        ]):
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
                self.use_AP(HEAL_AP)

                if self.health > self.max_health:
                    self.health = self.max_health

                self._delayed_command(HEAL_TIME, 'stop')
                self._delayed_command(1, 'restore_AP')

    @autosave
    def kill(self):
        UserModel._kill_AP_threads(self.id)
        death_actions = [ActionType.DEATH_FROM_ABOVE]
        self.action = random.choice(death_actions)
        self.extra_data['resurection_time'] = RESURECTION_TIME

        self._delayed_command(RESURECTION_TIME, 'resurect')

    @autosave
    def update_scores(self):
        self.scores = self.attr_from_db('scores') + 1

    @autosave
    def resurect(self):
        self.health = self.max_health
        self.weapon = self._weapons[0]
        self.x = random.randint(0, local_db['map_size']['width'] - 100)
        self.y = random.randint(0, local_db['map_size']['height'] - 100)
        self.action = ActionType.IDLE
        self.direction = DirectionType.LEFT
        self.AP = MAX_AP

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

        if self.cm.is_collide:
            self.x = x
            self.y = y
