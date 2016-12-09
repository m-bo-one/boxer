# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import json
import random
from collections import OrderedDict

from gevent import monkey; monkey.patch_all()  # noqa
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource


DB = {
    'map': {
        'width': 300,
        'height': 300
    },
    'users': {},
    'id_counter': 0
}


class UserModel(object):

    def __init__(self):
        self.id = DB['id_counter']
        DB['id_counter'] += 1
        self.x = random.randint(0, DB['map']['width'])
        self.y = random.randint(0, DB['map']['height'])
        self.width = 20
        self.height = 20
        self.speed = 2
        self.friction = 0.98

        self._vel_x = 0
        self._vel_y = 0

    @classmethod
    def register_user(cls):
        user = cls()
        DB['users'][user.id] = user
        return user

    def to_dict(self):
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'speed': self.speed,
            'velX': self._vel_x,
            'velY': self._vel_y,
            'friction': self.friction
        }

    def coords(self):
        return (self.x, self.y)

    def move(self, direction):
        if (direction == 'top'):
            if (self._vel_y > -self.speed):
                self._vel_y -= 1
        if (direction == 'bottom'):
            if (self._vel_y < self.speed):
                self._vel_y += 1
        if (direction == 'right'):
            if (self._vel_x < self.speed):
                self._vel_x += 1
        if (direction == 'left'):
            if (self._vel_x > -self.speed):
                self._vel_x -= 1

        self._vel_x *= self.friction
        self.x += self._vel_x
        self._vel_y *= self.friction
        self.y += self._vel_y

        if (self.x >= DB['map']['width'] - self.width):
            self.x = DB['map']['width'] - self.width
        elif (self.x <= 0):
            self.x = 0

        if (self.y > DB['map']['height'] - self.height):
            self.y = DB['map']['height'] - self.height
        elif (self.y <= 0):
            self.y = 0


class EchoApplication(WebSocketApplication):

    def on_open(self):
        print("Connection opened")

    def on_message(self, message):
        if message is None:
            return

        message = json.loads(message)
        print('Evaluate msg %s' % message['msg_type'])
        if message['msg_type'] == 'register_user':
            self.register_user()
        elif message['msg_type'] == 'player_move':
            self.move_user(message)

    def on_close(self, reason):
        print(reason)

    def register_user(self):
        user = UserModel.register_user()
        resp = {
            'msg_type': 'register_user',
            'data': user.to_dict()
        }
        self.ws.send(json.dumps(resp))

    def update_all(self):
        for client in self.ws.handler.server.clients.values():
            client.ws.send(json.dumps({
                'msg_type': 'users_map',
                'data': DB['users']
            }))

    def move_user(self, message):
        user = DB['users'][message['data']['id']]
        user.move(message['data']['direction'])
        resp = {
            'msg_type': 'player_move',
            'data': user.to_dict()
        }
        self.ws.send(json.dumps(resp))


if __name__ == '__main__':
    print('Starting server...\n')
    server = WebSocketServer(('', 9999),
                             Resource(OrderedDict({'/': EchoApplication})))
    server.serve_forever()
    print('Killing server...\n')
