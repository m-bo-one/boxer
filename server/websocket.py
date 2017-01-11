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

from conf import settings
from utils import setup_logging
from db import local_db
from app.models import UserModel
from app.colliders import spatial_hash


main_queue = Queue()


class GameApplication(WebSocketApplication):

    @staticmethod
    def _g_cleaner(client):
        user = client.user
        spatial_hash.remove_obj_by_point(user.pivot, user)
        try:
            local_db['users'].remove(user)
        except KeyError:
            pass

    @staticmethod
    def broadcast(client, msg_type, data):
        try:
            client.ws.send(json.dumps({'msg_type': msg_type, 'data': data}))
        except WebSocketError as e:
            GameApplication._g_cleaner(client)
            logging.error(e)

    @staticmethod
    def broadcast_all(clients, msg_type, data):
        gevent.joinall([
            gevent.spawn(GameApplication.broadcast, client, msg_type, data)
            for client in clients
        ])

    @property
    def user(self):
        return self.ws.handler.active_client.user

    def get_user_from_ws(self):
        self.user.update()
        if all([self.user, not self.user.is_dead,
                not self.user.operations_blocked]):
            return self.user

    @user.setter
    def user(self, obj):
        self.ws.handler.active_client.user = obj

    @user.deleter
    def user(self, obj):
        del self.ws.handler.active_client.user

    def on_open(self):
        logging.debug("Connection opened")
        getattr(self, 'register_user')({})

    def on_message(self, message):
        if message:
            message = json.loads(message)
            logging.info('Evaluate msg %s' % message['msg_type'])
            getattr(self, message['msg_type'])(message)

    def player_equip(self, message):
        user = self.get_user_from_ws()
        if not user:
            return
        user.equip(message['data']['equipment'])

    def player_heal(self, message):
        user = self.get_user_from_ws()
        if not user:
            return
        user.heal()

    def register_user(self, message):
        self.user = UserModel.create()
        local_db.setdefault('users', set())
        local_db['users'].add(self.user)
        self.broadcast(self, 'register_user', self.user.to_dict())

    def unregister_user(self, message):
        user = self.get_user_from_ws()
        if not user:
            return
        user_id = user.remove()
        if user_id is not None:
            self._g_cleaner(self.ws.handler.active_client)
            main_queue.put_nowait(user_id)

    def player_move(self, message):
        user = self.get_user_from_ws()
        if not user:
            return
        user.move(message['data']['action'], message['data']['direction'])

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
        setup_logging()
        logging.info('Starting server...\n')
        server = WebSocketServer(
            settings.WEBSOCKET_ADDRESS, Resource(OrderedDict({
                '/game': GameApplication
            })))
        server._spawn(main_ticker, server)
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Killing server...\n')
