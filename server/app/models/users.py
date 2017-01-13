from __future__ import division

import logging
import random
import json
import time

import gevent

from db import redis_db, local_db
from constants import (
    ActionType, DirectionType, WeaponType, ArmorType,
    RESURECTION_TIME, HEAL_TIME, HUMAN_HEALTH, MAX_AP, FIRE_AP, HEAL_AP)
from utils import generate_temp_password, generate_id, generate_token
from .weapons import Weapon
from .armors import Armor
from ..assets.sprites import sprite_proto
from ..colliders import obj_update, spatial_hash, CollisionManager


class UserModel(object):

    collision_pipeline = (
        'map_collision',
        'user_collision',
    )
    AP_stats = {}

    def __init__(self,
                 id,
                 username,
                 password,
                 token,
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
        self.id = id
        self.username = username
        self.password = password
        self.token = token
        self._update(x, y, speed, action, direction, armor, weapon,
                     health, extra_data, scores, AP, *args, **kwargs)

    def _update(self, x, y, speed, action, direction, armor, weapon,
                health, extra_data, scores, AP, *args, **kwargs):
        self.speed = speed
        self.x = x
        self.y = y
        self.action = action
        self.direction = direction
        self.armor = Armor(armor, self)
        self.weapon = Weapon(weapon, self)
        self.health = health
        self.max_health = HUMAN_HEALTH
        self.scores = scores
        self._armors = [Armor(ArmorType.ENCLAVE_POWER_ARMOR, self)]
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
    def get(cls, id, to_obj=True, **kwargs):
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
        return (json.loads(user) for user in users.itervalues())

    @classmethod
    def get_users_map(cls):
        return redis_db.hgetall('users')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'token': self.token
        }

    def cmd_dict(self):
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
            'armor': self.armor.name,
            'weapon': self.weapon.name,
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
