import logging
import random
import json

from db import DB
from .sprite import sprite_proto, sp_key_builder


class UserModel(dict):

    collision_pipeline = (
        'map_collision',
        # 'user_collision',
    )

    def __init__(self, speed=5, action='idle', direction='left',
                 armor='enclave_power_armor', weapon='no_weapon'):
        self.id = None
        self.speed = speed
        self.action = action
        self.direction = direction
        self.armor = armor
        self.weapon = weapon
        self.weapons = ['no_weapon', 'flamer']
        self.armors = ['enclave_power_armor']
        self.load_sprites()

        # self.width = self.sprite['frames']['width']
        # self.height = self.sprite['frames']['height']

        self.x = random.randint(0, DB['map']['width'] - 100)
        self.y = random.randint(0, DB['map']['height'] - 100)

    def __setattr__(self, name, value):
        super(UserModel, self).__setattr__(name, value)
        self[name] = value

    def to_dict(self):
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'speed': self.speed,
            'action': self.action,
            'direction': self.direction,
            'armor': str(self.armor),
            'weapon': str(self.weapon),
            'weapons': [str(weapon) for weapon in self.weapons],
            'armors': [str(armor) for armor in self.armors],
            'sprites': self.sprites
        }

    @classmethod
    def from_dict(cls, data):
        user = cls()
        for k, v in data.items():
            setattr(user, k, v)
        return user

    def to_json(self):
        return json.dumps(self.to_dict())

    def load_sprites(self):
        self.sprites = {
            sp_key_builder(
                armor, weapon, action): (sprite_proto
                                         .clone((armor, weapon, action)))
            for armor in self.armors
            for weapon in self.weapons
            for action in ['idle', 'walk']}

    @classmethod
    def register_user(cls, socket, **kwargs):
        user = cls()
        user.id = DB['id_counter']
        DB['id_counter'] += 1
        DB['users'][user.id] = user.to_dict()
        DB['sockets'][socket] = user.id
        return user

    @classmethod
    def unregister_user(cls, socket):
        try:
            user_id = DB['sockets'][socket]
            del DB['sockets'][socket]
            del DB['users'][user_id]
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
        if (self.x > DB['map']['width'] - 100 or self.x < 0 or
           self.y > DB['map']['height'] - 100 or self.y < 0):
            return True
        return False

    def user_collision(self):
        # TODO: Fix widht and height
        for other in DB['users'].values():
            if (self != other and self.x < other.x + other.width and
               self.x + self.width > other.x and
               self.y < other.y + other.height and
               self.height + self.y > other.y):
                return True
        return False

    def autosave(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            DB['users'][self.id] = self.to_dict()
            return result
        return wrapper

    @autosave
    def equip(self, type):
        # FIXME: Hardcoded, need to fix in future
        logging.error('Current weapon: %s', self.weapon)

        if type == 'weapon' and self.weapon != 'no_weapon':
            self.weapon = 'no_weapon'
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
