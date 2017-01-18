from __future__ import division

import math
import logging
import random
import json
import time

import gevent
from gevent.pool import Pool

from utils import lookahead
from db import redis_db
import constants as const
from .commands import CmdModel, field_extractor
from ..weapons import Weapon
from ..armors import Armor
from ...engine import Pathfinder, CollisionManager


def autosave(func):
    def wrapper(self, *args, **kwargs):
        # with self.cm.obj_update():
        logging.info('GREENLETS: %s' % self.AP_stats)
        result = func(self, *args, **kwargs)
        self.cmd = CmdModel.create(self.id, self.cmd.x, self.cmd.y,
                                   self.cmd.action, self.cmd.direction)
        self.save()
        return result
    return wrapper


class CharacterModel(object):

    max_pool_size = 100

    fields = ('id', 'user_id', 'race', 'name', 'health', 'weapon',
              'armor', 'scores', 'inventory', 'display')

    collision_pipeline = (
        'map_collision',
        'user_collision',
    )

    AP_stats = {}
    allowed_actions = set(['shoot', 'move', 'heal', 'equip'])

    def __init__(self, id, user_id, race, name, health, weapon, armor, scores,
                 inventory, display):
        self.id = id
        self.user_id = user_id
        self.race = const.Race(race)
        self.name = name
        self.health = health
        self.weapon = Weapon(weapon, self)
        self.armor = Armor(armor, self)
        self.scores = scores
        self.inventory = inventory
        self.AP = const.MAX_AP

        self._pool = Pool(self.max_pool_size)
        self.operations = []
        self.steps = []
        self.extra_data = {}
        self.max_health = self.setup_params['health']
        self._footpace = [2, 2]
        self.display = const.Display(display)
        if self.id:
            self.cmd = CmdModel.get_last_or_create(self.id)
            # self.cm = CollisionManager(self,
            #                            pipelines=self.collision_pipeline)

    def is_allowed(self, fname):
        return bool(fname in self.allowed_actions)

    @staticmethod
    def model_key():
        return 'characters'

    def save(self):
        if not self.id:
            self.id = redis_db.incr('%s:ids' % self.model_key())

        data = json.dumps(field_extractor(self))
        return redis_db.hset(self.model_key(), self.id, data)

    @classmethod
    def get(cls, id):
        data = redis_db.hget(cls.model_key(), id)
        if data:
            return cls(**json.loads(data))

    @classmethod
    def delete(cls, id=None):
        if not id:
            return redis_db.delete(cls.model_key())
        return redis_db.hdel(cls.model_key(), id)

    def remove(self):
        return CharacterModel.delete(self.id)

    @classmethod
    def create(cls, user_id, name, race, health, weapon, armor, display,
               *args, **kwargs):
        char = cls(id=None, user_id=user_id, race=race, name=name,
                   health=health, weapon=weapon, armor=armor, scores=0,
                   display=display, inventory=[])
        char.save()
        char.cmd = CmdModel.get_last_or_create(char.id)
        # char.cm = CollisionManager(char, pipelines=char.collision_pipeline)
        return char

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'race': self.race.value,
            'display': self.display.value,
            'x': self.cmd.x,
            'y': self.cmd.y,
            # 'width': self.width,
            # 'height': self.height,
            # 'pivot': self.pivot,
            'action': self.cmd.action.value,
            'direction': self.cmd.direction.value,
            'armor': self.armor.name.value,
            'weapon': self.weapon.name.value,
            'health': self.health,
            'operations_blocked': self.operations_blocked,
            'animation': self.animation,
            'extra_data': self.extra_data,
            'updated_at': time.time(),
            'scores': self.scores,
            'max_health': self.max_health,
            'operations': self.operations,
            'AP': self.AP,
            'max_AP': const.MAX_AP,
            'steps': self.steps
        }

    # @property
    # def size(self):
    #     _sprite = sprite_proto.get((self.armor.name,
    #                                 self.weapon.name,
    #                                 self.cmd.action))
    #     return _sprite['frames']['width'], _sprite['frames']['height']

    # @property
    # def pivot(self):
    #     return {
    #         "x": self.cmd.x + self.size[0] / 2,
    #         "y": (self.cmd.y + 2 * self.size[1] / 3 + 10)
    #     }

    @property
    def animation(self):
        if self.weapon.name == const.Weapon.Unarmed:
            weapon_key = ''
        elif self.cmd.action == const.Action.Attack:
            weapon_key = ''.join([self.weapon.name.name, 'Burst'])
        else:
            weapon_key = self.weapon.name.name

        if self.cmd.action == const.Action.Heal:
            action = const.Action.Magichigh.name
        else:
            action = self.cmd.action.name

        data = {
            "key": ''.join([
                'Stand', action, weapon_key, '_', self.cmd.direction.name])
        }
        if self.armor.name == const.Armor.Unarmored:
            key_armor = self.race.name
        else:
            key_armor = self.armor.name.name

        data['armor'] = key_armor
        return data

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

    # @property
    # def width(self):
    #     return self.size[0]

    # @property
    # def height(self):
    #     return self.size[1]

    @property
    def is_full_health(self):
        return self.health == const.HUMAN_HEALTH

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
                    block_for = const.HEAL_TIME
                if ct - operation['blocked_at'] <= block_for:
                    return True
                else:
                    del self.operations[i]
                    self.extra_data['sound_to_play'] = None
        except KeyError:
            return False
        else:
            return False

    def _delayed_command(self, delay, fname, *args, **kwargs):

        def _callback(*args, **kwargs):
            getattr(self, fname)(*args, **kwargs)

        g = self._pool.greenlet_class(_callback, *args, **kwargs)
        self._pool.add(g)
        g.start_later(delay)
        return g

    @autosave
    def shoot(self):
        if all([
            self.weapon_in_hands,
            not self.operations_blocked,
            self.AP - const.FIRE_AP >= 0,
            self.is_allowed('shoot')
        ]):
            self.display_show()
            self._clear_greenlets()
            self.cmd.action = const.Action.Attack
            self.block_operation('shoot')
            self.use_AP(const.FIRE_AP)
            self.extra_data['sound_to_play'] = self.weapon.w.SOUND

            # detected = [other for other in local_db['characters']
            #             if other.id != self.id and not
            #             other.is_dead and self.weapon.in_vision(other)]

            # if detected:
            #     logging.info('Found characters: %s', detected)
            #     self.weapon.shoot(detected)

            self._delayed_command(self.weapon.w.SHOOT_TIME, 'stop')
            self._delayed_command(1, 'restore_AP')

    @autosave
    def stealth(self):
        raise NotImplementedError()

    @property
    def weapon_in_hands(self):
        return self.weapon.name != const.Weapon.Unarmed

    @autosave
    def equip(self, type):
        if not self.is_allowed('equip'):
            return
        logging.info('Current weapon: %s', self.weapon.name)

        if type == 'weapon' and self.weapon_in_hands:
            self.weapon = Weapon(const.Weapon.Unarmed, self)
        elif type == 'weapon':
            self.weapon = Weapon(self.setup_params['weapon'], self)

    def use_AP(self, p):
        self.AP -= p
        if self.AP < 0:
            self.AP = 0

    def restore_AP(self):
        x = 0
        self._kill_AP_threads()
        for _ in range(const.MAX_AP - self.AP):
            thread = self._delayed_command(x, 'incr_AP')
            self.AP_stats[self.id].append(thread)
            x += 1

    def _kill_AP_threads(self):
        self.AP_stats.setdefault(self.id, [])
        if self.AP_stats.get(self.id):
            gevent.killall(self.AP_stats[self.id])
            self.AP_stats[self.id] = []

    @autosave
    def incr_AP(self):
        self.AP += 1
        if self.AP > const.MAX_AP:
            self.AP = const.MAX_AP

        logging.info("ID: %s - AP: %s" % (self.id, self.AP))

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

    def display_hide(self):
        self.display = const.Display.Hidden

    def display_show(self):
        self.display = const.Display.Exposed

    def display_toggle(self):
        if self.display == const.Display.Hidden:
            self.display_show()
        else:
            self.display_hide()

    @autosave
    def heal(self, target=None):
        if all([
            not self.is_full_health,
            not self.operations_blocked,
            self.AP - const.HEAL_AP >= 0,
            self.is_allowed('heal')
        ]):
            if target is not None and target != self:
                raise NotImplementedError()
            else:
                # TODO: For future, add inventory and
                # replace heal of inventory stimulators
                logging.info('Health before heal: %s', self.health)
                self.health += random.randrange(10, 20, 1)
                logging.info('Health before heal: %s', self.health)

                self.cmd.action = const.Action.Heal
                self.block_operation('heal')
                self.use_AP(const.HEAL_AP)

                if self.health > self.max_health:
                    self.health = self.max_health

                self._delayed_command(const.HEAL_TIME, 'stop')
                self._delayed_command(1, 'restore_AP')

    @autosave
    def kill(self):
        self.display_show()
        self._kill_AP_threads()
        death_actions = [const.DeathAction.Melt]
        self.cmd.action = random.choice(death_actions)
        self.extra_data['resurection_time'] = const.RESURECTION_TIME

        self._delayed_command(const.RESURECTION_TIME, 'resurect')

    @autosave
    def update_scores(self):
        self.scores += 1

    @autosave
    def resurect(self):
        self.health = self.max_health
        self.weapon = Weapon(const.Weapon.Unarmed, self)
        self.cmd.x = random.randint(0, 1280 - 100)
        self.cmd.y = random.randint(0, 768 - 100)
        self.cmd.action = const.Action.Breathe
        self.cmd.direction = const.Direction.W
        self.AP = const.MAX_AP

        try:
            del self.extra_data['resurection_time']
        except KeyError:
            pass

    PATH_TREADS = {}

    def _kill_path(self):
        try:
            self.PATH_TREADS[self.id].kill()
            self.PATH_TREADS[self.id] = None
            self.steps = []
        except (KeyError, AttributeError):
            pass

    def _clear_greenlets(self):
        self._kill_AP_threads()
        self._kill_path()

    @autosave
    def move(self, point):
        if not self.is_allowed('move'):
            return
        self._clear_greenlets()
        self.stop()

        pf = Pathfinder.build_path(self, point, 'A*')

        def _move(pf):
            for i, lk in enumerate(lookahead(reversed(list(pf)))):
                step, has_more = lk
                speed = 0.015
                if i == 0:
                    prev_step = step
                if prev_step[0] - step[0] != 0 and prev_step[1] - step[1] != 0:
                    logging.debug('UID: %s, define GO', self.id)
                    if step[0] > prev_step[0] and step[1] < prev_step[1]:
                        logging.debug('UID: %s, GO UP-RIGHT', self.id)
                        direction = const.Direction.NE
                    elif step[0] > prev_step[0] and step[1] > prev_step[1]:
                        logging.debug('UID: %s, GO BOTTOM-RIGHT', self.id)
                        direction = const.Direction.SE
                    elif step[0] < prev_step[0] and step[1] > prev_step[1]:
                        logging.debug('UID: %s, GO BOTTOM-LEFT', self.id)
                        direction = const.Direction.SW
                    elif step[0] < prev_step[0] and step[1] < prev_step[1]:
                        logging.debug('UID: %s, GO UP-LEFT', self.id)
                        direction = const.Direction.NW

                    speed *= math.sqrt(2)
                elif prev_step[0] - step[0] == 0:
                    logging.debug('UID: %s, GO Y', self.id)
                    if step[1] - prev_step[1] >= 0:
                        logging.debug('UID: %s, GO BOTTOM', self.id)
                        direction = const.Direction.S
                    else:
                        logging.debug('UID: %s, GO TOP', self.id)
                        direction = const.Direction.N
                elif prev_step[1] - step[1] == 0:
                    logging.debug('UID: %s, GO X', self.id)
                    if step[0] - prev_step[0] >= 0:
                        logging.debug('UID: %s, GO RIGHT', self.id)
                        direction = const.Direction.E
                    else:
                        logging.debug('UID: %s, GO LEFT', self.id)
                        direction = const.Direction.W
                prev_step = step

                self.steps.append(step)
                self._plot_path(const.Action.Walk, direction, step)
                gevent.sleep(speed)
                if not has_more:
                    self.stop()
                    self._delayed_command(1, 'restore_AP')

        self.PATH_TREADS[self.id] = self._pool.spawn(_move, pf)

    @autosave
    def stop(self):
        self._plot_path(const.Action.Breathe, self.cmd.direction, self.coords)

    @autosave
    def _plot_path(self, action, direction, coords):
        if self.operations_blocked or self.is_dead:
            return
        logging.info('Current coords: %s', self.coords)

        self.cmd.action = const.Action(action)
        self.cmd.direction = const.Direction(direction)

        logging.info('\n'
                     'Direction: %s\n'
                     'Action: %s\n'
                     'Weapon: %s\n',
                     self.cmd.direction, self.cmd.action,
                     self.weapon.name.value)

        if self.cmd.action == const.Action.Walk:
            self.cmd.x = coords[0]
            self.cmd.y = coords[1]
