import logging
import random

from db import DB
from .sprite import sprite_proto


class UserModel(dict):

    collision_pipeline = (
        'map_collision',
        # 'user_collision',
    )

    def __init__(self, speed=5, action='idle', direction='left',
                 armor='enclave_power_armor', weapon='flamer'):
        self.id = None
        self.speed = speed
        self.action = action
        self.direction = direction
        self.armor = armor
        self.weapon = weapon
        self.load_sprites()

        # self.sprite = sprite_proto.clone((armor, weapon, action))
        self.width = self.sprite['frames']['width']
        self.height = self.sprite['frames']['height']

        self.x = random.randint(0, DB['map']['width'] - int(self.width))
        self.y = random.randint(0, DB['map']['height'] - int(self.height))

    def __setattr__(self, name, value):
        super(UserModel, self).__setattr__(name, value)
        self[name] = value

    def load_sprites(self):
        self.sprites = {
            (self.armor, self.weapon, action): sprite_proto.clone(
                (self.armor, self.weapon, action))
            for action in ['idle', 'walk']}

    @classmethod
    def register_user(cls, socket, **kwargs):
        user = cls()
        user.id = DB['id_counter']
        DB['id_counter'] += 1
        DB['users'][user.id] = user
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
        if (self.x > DB['map']['width'] - self.width or self.x < 0 or
           self.y > DB['map']['height'] - self.height or self.y < 0):
            return True
        return False

    def user_collision(self):
        for other in DB['users'].values():
            if (self != other and self.x < other.x + other.width and
               self.x + self.width > other.x and
               self.y < other.y + other.height and
               self.height + self.y > other.y):
                return True
        return False

    def move(self, action, direction):
        way = '_'.join([action, direction])
        logging.info('Current way: %s', way)
        logging.info('Current coords: %s', self.coords)

        x, y = self.coords

        self.action = action
        self.direction = direction

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
