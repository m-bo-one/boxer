# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
import json
import random
from collections import OrderedDict

from gevent import monkey; monkey.patch_all()  # noqa
from geventwebsocket import (
    WebSocketServer, WebSocketApplication, Resource, WebSocketError)

from utils import setup_logging


DB = {
    'map': {
        'width': 300,
        'height': 300
    },
    'users': {},
    'sockets': {},
    'id_counter': 0,
}


class UserModel(dict):

    def __init__(self):
        self.id = DB['id_counter']
        DB['id_counter'] += 1
        self.x = random.randint(0, DB['map']['width'])
        self.y = random.randint(0, DB['map']['height'])
        self.width = 20
        self.height = 20
        self.speed = 2
        self.friction = 1

        self._vel_x = 0
        self._vel_y = 0

        self.update(self.__dict__)

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

        self.update(self.__dict__)


class EchoApplication(WebSocketApplication):

    def on_open(self):
        logging.info("Connection opened")
        self.register_user()

    def on_message(self, message):
        logging.info('Current clients: %s',
                     self.ws.handler.server.clients.keys())
        if message is None:
            return

        message = json.loads(message)
        logging.info('Evaluate msg %s' % message['msg_type'])
        if message['msg_type'] == 'player_move':
            self.move_user(message)
        if message['msg_type'] == 'unregister_user':
            self.unregister_user()

        logging.info('Updating map...')
        self.broadcast_all('users_map', DB['users'])

    def on_close(self, reason):
        logging.info(reason)
        try:
            self.unregister_user()
        except WebSocketError as e:
            logging.error(e.message)

    def register_user(self):
        user = UserModel.register_user(self.ws)
        self.broadcast('register_user', user)

    def unregister_user(self):
        user_id = UserModel.unregister_user(self.ws)
        self.broadcast_all('unregister_user', {'id': user_id})

    def broadcast(self, msg_type, data):
        self.ws.send(json.dumps({'msg_type': msg_type, 'data': data}))

    def broadcast_all(self, msg_type, data):
        for client in self.ws.handler.server.clients.values():
            client.ws.send(json.dumps({'msg_type': msg_type, 'data': data}))

    def move_user(self, message):
        user = DB['users'][message['data']['id']]
        user.move(message['data']['direction'])
        self.broadcast('player_move', user)


if __name__ == '__main__':
    try:
        setup_logging()
        logging.info('Starting server...\n')
        server = WebSocketServer(('', 9999),
                                 Resource(OrderedDict({'/': EchoApplication})))
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Killing server...\n')
