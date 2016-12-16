# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
import json
from collections import OrderedDict

from gevent import monkey; monkey.patch_all()  # noqa
from geventwebsocket import (
    WebSocketServer, WebSocketApplication, Resource)

from conf import settings
from utils import setup_logging
from db import DB
from models import UserModel


class GameApplication(WebSocketApplication):

    def on_open(self):
        logging.info("Connection opened")
        self.render_map()
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

    def render_map(self):
        self.broadcast('render_map', DB['map'])

    def register_user(self):
        user = UserModel.register_user(self.ws)
        self.broadcast('register_user', user)
        self.broadcast_all('users_map', DB['users'])

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
        user.move(message['data']['action'], message['data']['direction'])
        self.broadcast('player_move', user)


if __name__ == '__main__':
    try:
        setup_logging()
        logging.info('Starting server...\n')
        server = WebSocketServer(
            settings.WEBSOCKET_ADDRESS, Resource(OrderedDict({
                '/game': GameApplication
            })))
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Killing server...\n')
