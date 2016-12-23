# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
import json
from collections import OrderedDict

from gevent import monkey; monkey.patch_all()  # noqa
from geventwebsocket import (
    WebSocketServer, WebSocketApplication, Resource, WebSocketError)
from eventemitter import EventEmitter

from conf import settings
from utils import setup_logging
from db import DB, DBClient
from models import UserModel


db = DBClient().connect('redis')


class GameApplication(WebSocketApplication, EventEmitter):

    def __init__(self, *args, **kwargs):
        super(GameApplication, self).__init__(*args, **kwargs)
        self.on('player_move', self.player_move)
        self.on('player_equip', self.player_equip)
        self.on('player_shoot', self.player_shoot)
        self.on('unregister_user', self.unregister_user)

    def broadcast(self, msg_type, data, ws=None):
        try:
            ws = self.ws if not ws else ws
            ws.send(json.dumps({'msg_type': msg_type, 'data': data}))
        except WebSocketError as e:
            logging.error(e)

    def broadcast_all(self, msg_type, data):
        for client in self.ws.handler.server.clients.values():
            self.broadcast(msg_type, data, client.ws)

    def get_user_from_ws(self, ws=None):
        ws = self.ws if not ws else ws
        return UserModel.get(DB['sockets'][ws])

    def on_open(self):
        logging.info("Connection opened")
        user = UserModel.register_user(self.ws)
        self.broadcast('render_map', {
            'width': 1080,
            'height': 640
        })
        self.broadcast('register_user', user.to_dict())
        self.broadcast_all('users_map', UserModel.get_users_map())

    def on_message(self, message):
        logging.info('Current clients: %s',
                     self.ws.handler.server.clients.keys())

        if message is None:
            return

        message = json.loads(message)

        logging.info('Evaluate msg %s' % message['msg_type'])

        self.emit(message['msg_type'], message)

        logging.info('Updating map...')

        self.broadcast_all('users_map', UserModel.get_users_map())

    def player_equip(self, message):
        user = self.get_user_from_ws()
        if user.is_dead:
            return
        user.equip(message['data']['equipment'])
        self.broadcast('player_update', user.to_dict())

    def unregister_user(self, message):
        user_id = UserModel.unregister_user(self.ws)
        self.broadcast_all('unregister_user', {'id': user_id})

    def player_move(self, message):
        user = self.get_user_from_ws()
        if user.is_dead:
            return
        user.move(message['data']['action'], message['data']['direction'])
        self.broadcast('player_update', user.to_dict())

    def player_shoot(self, message):
        user = self.get_user_from_ws()
        if user.is_dead:
            return
        hitted_player = user.shoot()
        if hitted_player:
            self.broadcast('player_update', hitted_player.to_dict(),
                           DB['users'][hitted_player.id])


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
