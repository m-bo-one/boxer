import os
import logging
import random

from PIL import Image
from db import DB
from conf import settings
from utils import await_greenlet


class UserModel(dict):

    collision_pipeline = (
        'map_collision',
        # 'user_collision',
    )

    def __init__(self):
        self.id = DB['id_counter']
        DB['id_counter'] += 1

        self.speed = 5
        self.image_name = 'warrior.png'
        self.image_url = os.path.join(settings.MEDIA_URL, self.image_name)
        try:
            width, height = await_greenlet(self.get_image_size,
                                           self.image_name)
            self.width = width
            self.height = height
        except IOError:
            self.width = 20
            self.height = 20

        self.x = random.randint(0, DB['map']['width'] - self.width)
        self.y = random.randint(0, DB['map']['height'] - self.height)

        self.username = '<username>'

        self.update(self.__dict__)

    @staticmethod
    def get_image_size(image_name):
        image = Image.open(os.path.join(settings.MEDIA_PATH, image_name))
        image.close()
        return image.size

    @classmethod
    def register_user(cls, socket):
        user = cls()
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

    def move(self, direction):
        logging.info('Current direction: %s', direction)
        logging.info('Current coords: %s', self.coords)

        x, y = self.coords

        if direction == 'top':
            self.y -= self.speed

        elif direction == 'bottom':
            self.y += self.speed

        elif direction == 'right':
            self.x += self.speed

        elif direction == 'left':
            self.x -= self.speed

        if self.is_collide:
            self.x = x
            self.y = y

        self.update(self.__dict__)
