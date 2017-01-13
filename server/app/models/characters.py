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
from . import RedisModelMixin as ModelMixin
from .weapons import Weapon
from .armors import Armor
from ..assets.sprites import sprite_proto
from ..colliders import CollisionManager


class CharacterModel(ModelMixin):

    fields = ('id', 'name', 'health', 'weapon', 'armor', 'scores', 'inventory')

    collision_pipeline = (
        'map_collision',
        'user_collision',
    )

    AP_stats = {}

    def __init__(self, id, name, health, weapon, armor, scores, inventory):
        self.id = int(id) if id else None
        self.name = name
        self.health = int(health)
        self.weapon = Weapon(weapon, self)
        self.armor = Armor(armor, self)
        self.scores = int(scores)
        self.inventory = inventory
        self.AP = MAX_AP

        self.operations = []
        self.extra_data = {}
        self.max_health = HUMAN_HEALTH
        self.speed = [3, 3]
        if self.id:
            self.cmd = CmdModel.get_last_or_create(self.id)
            self.cm = CollisionManager(self, pipelines=self.collision_pipeline)

    @staticmethod
    def model_key():
        return 'character'

    @classmethod
    def create(cls, name,
               health=100,
               weapon=WeaponType.NO_WEAPON,
               armor=ArmorType.ENCLAVE_POWER_ARMOR):
        char = cls(id=None, name=name, health=health, weapon=weapon,
                   armor=armor, scores=0, inventory=[])
        char.save()
        char.cmd = CmdModel.get_last_or_create(char.id)
        char.cm = CollisionManager(char, pipelines=char.collision_pipeline)
        return char

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'x': self.cmd.x,
            'y': self.cmd.y,
            'width': self.width,
            'height': self.height,
            'speed': self.speed,
            'pivot': self.pivot,
            'action': self.cmd.action,
            'direction': self.cmd.direction,
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
        # print(data)
        return data

    @property
    def size(self):
        _sprite = sprite_proto.get((self.armor.name,
                                    self.weapon.name,
                                    self.cmd.action))
        return _sprite['frames']['width'], _sprite['frames']['height']

    @property
    def pivot(self):
        return {
            "x": self.cmd.x + self.size[0] / 2,
            "y": (self.cmd.y + 2 * self.size[1] / 3 + 10)
        }

    @property
    def animation(self):
        return {
            'way': "_".join([self.cmd.action, self.cmd.direction]),
            'compound': sprite_proto.sp_key_builder(self.armor.name,
                                                    self.weapon.name,
                                                    self.cmd.action),
        }

    def __repr__(self):
        return '<CharacterModel: id - %s>' % self.id

    @property
    def is_dead(self):
        return bool(self.health <= 0)

    def block_operation(self, type):
        self.operations.append({
            'type': type,
            'blocked_at': time.time()
        })

    @property
    def coords(self):
        return (self.x, self.y)

    @property
    def x(self):
        return self.cmd.x

    @property
    def y(self):
        return self.cmd.y

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def is_full_health(self):
        return self.health == HUMAN_HEALTH

    def autosave(func):
        def wrapper(self, *args, **kwargs):
            with self.cm.obj_update():
                result = func(self, *args, **kwargs)
                self.cmd = CmdModel.create(self.id, self.cmd.x, self.cmd.y,
                                           self.cmd.action, self.cmd.direction)
            self.save()
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
            getattr(self, fname)()

        return gevent.spawn_later(delay, _callback)

    @autosave
    def shoot(self):
        if all([
            self.weapon_in_hands,
            not self.operations_blocked,
            self.AP - FIRE_AP >= 0
        ]):
            self.cmd.action = ActionType.FIRE
            self.block_operation('shoot')
            self.use_AP(FIRE_AP)
            self.extra_data['sound_to_play'] = self.weapon.w.SOUNDS['fire']

            detected = [other for other in local_db['characters']
                        if other.id != self.id and not
                        other.is_dead and self.weapon.in_vision(other)]

            if detected:
                logging.info('Found characters: %s', detected)
                self.weapon.shoot(detected)

            self._delayed_command(self.weapon.w.SHOOT_TIME, 'stop')
            self._delayed_command(1, 'restore_AP')

    @property
    def weapon_in_hands(self):
        return self.weapon.name != WeaponType.NO_WEAPON

    @autosave
    def equip(self, type):
        logging.info('Current weapon: %s', self.weapon.name)

        if type == 'weapon' and self.weapon_in_hands:
            self.weapon = Weapon(WeaponType.NO_WEAPON, self)
        elif type == 'weapon':
            self.weapon = Weapon(WeaponType.M60, self)

        if type == 'armor':
            self.armor = Armor(WeaponType.ENCLAVE_POWER_ARMOR, self)

    def use_AP(self, p):
        self.AP -= p
        if self.AP < 0:
            self.AP = 0

    def restore_AP(self):
        x = 0
        CharacterModel._kill_AP_threads(self.id)
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
        self.AP += 1
        if self.AP > MAX_AP:
            self.AP = MAX_AP

        logging.info("ID: %s- AP: %s" % (self.id, self.AP))

    @autosave
    def got_hit(self, weapon, dmg):
        logging.info('Health before hit: %s', self.health)
        rdmg = self.armor.reduce_damage(weapon, dmg)
        self.health -= rdmg
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
                self.health += random.randrange(10, 20, 1)
                logging.info('Health before heal: %s', self.health)

                self.cmd.action = ActionType.HEAL
                self.block_operation('heal')
                self.use_AP(HEAL_AP)

                if self.health > self.max_health:
                    self.health = self.max_health

                self._delayed_command(HEAL_TIME, 'stop')
                self._delayed_command(1, 'restore_AP')

    @autosave
    def kill(self):
        CharacterModel._kill_AP_threads(self.id)
        death_actions = [ActionType.DEATH_FROM_ABOVE]
        self.cmd.action = random.choice(death_actions)
        self.extra_data['resurection_time'] = RESURECTION_TIME

        self._delayed_command(RESURECTION_TIME, 'resurect')

    @autosave
    def update_scores(self):
        self.scores += 1

    @autosave
    def resurect(self):
        self.health = self.max_health
        self.weapon = Weapon(WeaponType.NO_WEAPON, self)
        self.cmd.x = random.randint(0, 1280 - 100)
        self.cmd.y = random.randint(0, 768 - 100)
        self.cmd.action = ActionType.IDLE
        self.cmd.direction = DirectionType.LEFT
        self.AP = MAX_AP

        try:
            del self.extra_data['resurection_time']
        except KeyError:
            pass

    @autosave
    def stop(self):
        self.move('idle', self.cmd.direction)

    @autosave
    def move(self, action, direction):
        way = '_'.join([action, direction])
        logging.info('Current way: %s', way)
        logging.info('Current coords: %s', self.coords)

        x, y = self.coords

        self.cmd.action = action
        self.cmd.direction = direction

        logging.info('\n'
                     'Direction: %s\n'
                     'Action: %s\n'
                     'Weapon: %s\n',
                     self.cmd.direction, self.cmd.action, self.weapon.name)

        if way == 'walk_top':
            self.cmd.y -= self.speed[1]

        elif way == 'walk_bottom':
            self.cmd.y += self.speed[1]

        elif way == 'walk_right':
            self.cmd.x += self.speed[0]

        elif way == 'walk_left':
            self.cmd.x -= self.speed[0]

        if self.cm.is_collide:
            self.cmd.x = x
            self.cmd.y = y


class CmdModel(object):

    fields = ('id', 'x', 'y', 'action', 'direction')

    def __init__(self, id, character_id, x, y, action, direction):
        self.id = int(id) if id else None
        self.character_id = int(character_id)
        self.x = int(x)
        self.y = int(y)
        self.action = action
        self.direction = direction

    @classmethod
    def create(cls, character_id,
               x=0, y=0,
               action=ActionType.IDLE,
               direction=DirectionType.LEFT):
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
        return json.dumps({
            field: getattr(self, field) for field in self.fields})

    def save(self):
        if not self.id:
            self.id = redis_db.incr('cmd:ids')
        return redis_db.lpush('cmd:%s' % self.character_id, self.to_json())

    @classmethod
    def last(cls, character_id):
        try:
            cmd = redis_db.lrange('cmd:%s' % character_id, 0, 0)[0]
            return cls(character_id=character_id, **json.loads(cmd[0]))
        except IndexError:
            pass

    @classmethod
    def delete(cls):
        keys = redis_db.keys('cmd:*')
        for key in keys:
            if key == 'ids':
                continue
            redis_db.delete(key)

    @classmethod
    def get_last_or_create(cls, character_id):
        if character_id is None:
            raise TypeError("Can't be None")
        cmd = CmdModel.last(character_id)
        if not cmd:
            cmd = CmdModel.create(character_id)
        return cmd
