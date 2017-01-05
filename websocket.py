# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
import json
from collections import OrderedDict

import gevent
from gevent import monkey; monkey.patch_all()  # noqa
from gevent.queue import Queue
from geventwebsocket import (
    WebSocketServer, WebSocketApplication, Resource, WebSocketError)
from eventemitter import EventEmitter

from conf import settings
from utils import setup_logging
from db import local_db
from app.models import UserModel
from app.collider import spatial_hash


ws_event = EventEmitter()
main_queue = Queue()


class GameApplication(WebSocketApplication):

    @staticmethod
    def broadcast(client, msg_type, data):
        try:
            client.ws.send(json.dumps({'msg_type': msg_type, 'data': data}))
        except WebSocketError as e:
            logging.error(e)

    @staticmethod
    def broadcast_all(clients, msg_type, data):
        gevent.joinall([
            gevent.spawn(GameApplication.broadcast, client, msg_type, data)
            for client in clients
        ])

    def get_user_from_ws(self, ws=None):
        self.user.update()
        if all([
            self.user, not self.user.is_dead, not self.user.operations_blocked
        ]):
            return self.user

    def on_open(self):
        logging.info("Connection opened")
        self.broadcast(self, 'render_map', local_db['map_size'])
        ws_event.emit('register_user', self, {})

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

    @ws_event.on('player_heal')
    def player_heal(self, message):
        user = self.get_user_from_ws()
        if not user:
            return
        user.heal()

    @ws_event.on('register_user')
    def register_user(self, message):
        self.user = UserModel.create()
        self.broadcast(self, 'register_user', self.user.to_dict())

    @ws_event.on('unregister_user')
    def unregister_user(self, message):
        user_id = self.user.remove()
        if user_id is not None:
            main_queue.put_nowait(user_id)

    @ws_event.on('player_move')
    def player_move(self, message):
        user = self.get_user_from_ws()
        if not user:
            return
        user.move(message['data']['action'], message['data']['direction'])

    @ws_event.on('player_shoot')
    def player_shoot(self, message):
        user = self.get_user_from_ws()
        if not user:
            return
        user.shoot()


def main_ticker(server):

    while True:
        gevent.sleep(0.01)
        data = {
            'users': {
                'update': UserModel.get_users_map(),
                'remove': []
            },
            'count': len(server.clients),
        }
        try:
            result = main_queue.get_nowait()
            data['users']['remove'].append(result)
        except:
            pass
        GameApplication.broadcast_all(server.clients.values(),
                                      'users_map', data)


if __name__ == '__main__':
    try:
        UserModel.delete()
        loglevel = logging.ERROR if not settings.DEBUG else logging.INFO
        setup_logging(default_level=loglevel)
        logging.info('Starting server...\n')
        server = WebSocketServer(
            settings.WEBSOCKET_ADDRESS, Resource(OrderedDict({
                '/game': GameApplication
            })))
        server._spawn(main_ticker, server)
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Killing server...\n')
