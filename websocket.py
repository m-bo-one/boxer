# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
import json
from collections import OrderedDict

from gevent import monkey; monkey.patch_all()  # noqa
from geventwebsocket import (
    WebSocketServer, WebSocketApplication, Resource, WebSocketError)

from conf import settings
from utils import setup_logging
from db import DB, DBClient
from models import UserModel


db = DBClient().connect('redis')


class GameApplication(WebSocketApplication):

    def get_user_from_ws(self):
        return UserModel.get(DB['sockets'][self.ws])

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
        if message['msg_type'] == 'player_equip':
            self.equip_user(message)
        if message['msg_type'] == 'unregister_user':
            self.unregister_user()

        logging.info('Updating map...')
        self.broadcast_all('users_map', UserModel.get_users_map())

    def on_close(self, reason):
        logging.info(reason)

    def equip_user(self, message):
        user = self.get_user_from_ws()
        user.equip(message['data']['equipment'])
        self.broadcast('player_update', user.to_dict())

    def render_map(self):
        self.broadcast('render_map', DB['map'])

    def register_user(self):
        user = UserModel.register_user(self.ws)
        self.broadcast('register_user', user.to_dict())
        self.broadcast_all('users_map', UserModel.get_users_map())

    def unregister_user(self):
        user_id = UserModel.unregister_user(self.ws)
        self.broadcast_all('unregister_user', {'id': user_id})

    def broadcast(self, msg_type, data, ws=None):
        try:
            ws = self.ws if not ws else ws
            ws.send(json.dumps({'msg_type': msg_type, 'data': data}))
        except WebSocketError as e:
            logging.error(e)

    def broadcast_all(self, msg_type, data):
        for client in self.ws.handler.server.clients.values():
            self.broadcast(msg_type, data, client.ws)

    def move_user(self, message):
        user = self.get_user_from_ws()
        user.move(message['data']['action'], message['data']['direction'])
        self.broadcast('player_update', user.to_dict())


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
        UserModel.delete()
