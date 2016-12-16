import os
import logging
import random

from db import DB
from conf import settings
from utils import await_greenlet, get_image


class AnimatedSprite(object):
    """Created animated sprite.
    Init params:
        [
            {
                'direction': 'rigth',
                'action': 'walk',
                'image_path': '../qwertyko.png',
                'count': 4,
                'speed': 0.5
            },

            ...
        ]
    """

    def __init__(self, image_name, action, direction, count, speed):
        self.image_name = image_name
        self.action = action
        self.direction = direction
        self.count = count
        self.speed = speed

        self.image = await_greenlet(get_image, self.image_name)
        self.image_url = os.path.join(settings.MEDIA_URL, self.image_name)
        self.height = self.image.height
        # width calculated dynamicaly through count
        self.width = self.image.width / float(count)
        self.size = (self.width, self.height)

    @property
    def way(self):
        return "_".join([self.action, self.direction])

    @classmethod
    def prepare_easeljs_data(cls, images_info):
        prev_count = 0
        resp_data = {}

        resp_data.setdefault('images', [])
        resp_data.setdefault('frames', {})
        resp_data.setdefault('animations', {})

        for image_info in images_info:
            sprite = cls(**image_info)
            prev_count += sprite.count
            resp_data['images'].append(sprite.image_url)
            resp_data['frames'] = {
                'height': sprite.height,
                'width': sprite.width,
                'count': prev_count
            }
            resp_data['animations'][sprite.way] = {
                'frames': list(range(prev_count - sprite.count, prev_count)),
                'speed': sprite.speed
            }
        return resp_data


class UserModel(dict):

    collision_pipeline = (
        'map_collision',
        # 'user_collision',
    )

    def __init__(self, speed, action='wait', direction='left', **extra):
        self.id = None
        self.speed = speed

        _easeljs_data = extra.get('easeljs_data')
        if _easeljs_data is None:
            _easeljs_data = []

        self.sprite = AnimatedSprite.prepare_easeljs_data(_easeljs_data)
        self.width = self.sprite['frames']['width']
        self.height = self.sprite['frames']['height']

        self.action = action
        self.direction = direction

        self.x = random.randint(0, DB['map']['width'] - int(self.width))
        self.y = random.randint(0, DB['map']['height'] - int(self.height))

    def __setattr__(self, name, value):
        super(UserModel, self).__setattr__(name, value)
        self[name] = value

    @classmethod
    def register_user(cls, socket, **kwargs):
        data = {
            'speed': 5,
            'action': 'wait',
            'direction': 'left',
            'easeljs_data': [
                {
                    'direction': 'left',
                    'action': 'walk',
                    'image_name': 'enclave_power_armor_left.jpg',
                    'count': 8,
                    'speed': 0.3
                },
                {
                    'direction': 'right',
                    'action': 'walk',
                    'image_name': 'enclave_power_armor_right.jpg',
                    'count': 8,
                    'speed': 0.3
                },
                {
                    'direction': 'top',
                    'action': 'walk',
                    'image_name': 'enclave_power_armor_top.jpg',
                    'count': 8,
                    'speed': 0.3
                },
                {
                    'direction': 'bottom',
                    'action': 'walk',
                    'image_name': 'enclave_power_armor_bottom.jpg',
                    'count': 8,
                    'speed': 0.3
                }
            ]
        }
        user = cls(**data)
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
