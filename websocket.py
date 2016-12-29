# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
import json
from collections import OrderedDict

import gevent
from gevent import monkey; monkey.patch_all()  # noqa
from geventwebsocket import (
    WebSocketServer, WebSocketApplication, Resource, WebSocketError)
from eventemitter import EventEmitter

from conf import settings
from utils import setup_logging
from db import local_db
from app.models import UserModel


ws_event = EventEmitter()


class GameApplication(WebSocketApplication):

    _packager_initialized = False
    _packager_max_workers = 1

    def __init__(self, *args, **kwargs):
        super(GameApplication, self).__init__(*args, **kwargs)

        if not GameApplication._packager_initialized:
            [gevent.spawn(self.run_ticker)
             for _ in xrange(self._packager_max_workers)]
            GameApplication._packager_initialized = True

    def run_ticker(self):
        while True:
            gevent.sleep(0.01)
            # logging.info('Current clients: %s',
            #              self.ws.handler.server.clients.keys())
            # logging.info('Updating map...')
            self.broadcast_all('users_map',
                               {'users': UserModel.get_users_map(),
                                'count': len(self.ws.handler.server.clients)})

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
        user = UserModel.get(local_db['socket2uid'][ws])
        if user and not user.is_dead and not user.operations_blocked:
            return user

    def on_open(self):
        logging.info("Connection opened")
        self.broadcast('render_map', local_db['map_size'])

    def on_message(self, message):
        if message:
            message = json.loads(message)
            logging.info('Evaluate msg %s' % message['msg_type'])
            ws_event.emit(message['msg_type'], self, message)

    @ws_event.on('player_equip')
    def player_equip(self, message):
        user = self.get_user_from_ws()
        if not user:
            return
        user.equip(message['data']['equipment'])
        self.broadcast('player_update', user.to_dict())

    @ws_event.on('register_user')
    def register_user(self, message):
        user = UserModel.register_user(self.ws)
        self.broadcast('render_map', local_db['map_size'])
        self.broadcast('register_user', user.to_dict())

    @ws_event.on('unregister_user')
    def unregister_user(self, message):
        user_id = UserModel.unregister_user(self.ws)
        self.broadcast_all('unregister_user', {'id': user_id})

    @ws_event.on('kill_user')
    def kill_user(self, message):
        user = self.get_user_from_ws()
        if not user:
            return
        user.kill()
        self.broadcast('player_update', user.to_dict())

    @ws_event.on('player_move')
    def player_move(self, message):
        user = self.get_user_from_ws()
        if not user:
            return
        user.move(message['data']['action'], message['data']['direction'])
        self.broadcast('player_update', user.to_dict())

    @ws_event.on('player_shoot')
    def player_shoot(self, message):
        user = self.get_user_from_ws()
        if not user:
            return

        for hitted_player in user.shoot():
            self.broadcast('player_update', hitted_player.to_dict(),
                           local_db['uid2socket'][hitted_player.id])

        self.broadcast('player_update', user.to_dict())
        from constants import SHOOT_DELAY

        def _callback():
            user = self.get_user_from_ws()
            if not user:
                return
            user.move('idle', user.direction)
            self.broadcast('player_update', user.to_dict())

        gevent.spawn_later(SHOOT_DELAY, _callback)


if __name__ == '__main__':
    try:
        loglevel = logging.ERROR if not settings.DEBUG else logging.INFO
        setup_logging(default_level=loglevel)
        logging.info('Starting server...\n')
        server = WebSocketServer(
            settings.WEBSOCKET_ADDRESS, Resource(OrderedDict({
                '/game': GameApplication
            })))
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Killing server...\n')
        UserModel.delete()
