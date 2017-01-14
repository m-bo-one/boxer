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
from app.models import CharacterModel
from app.colliders import spatial_hash


main_queue = Queue()


class GameApplication(WebSocketApplication):

    @staticmethod
    def _g_cleaner(user):
        # spatial_hash.remove_obj_by_point(user.pivot, user)
        try:
            local_db['characters'].remove(user)
        except KeyError:
            pass

    def broadcast(self, msg_type, data):
        try:
            print('-------')
            self.ws.send(json.dumps({'msg_type': msg_type, 'data': data}))
        except WebSocketError as e:
            GameApplication._g_cleaner(self.user)
            logging.error(e)

    # def broadcast_all(self, msg_type, data):
    #     for client in self.ws.handler.server.clients.values():
    #         GameApplication.broadcast(client, msg_type, data)

    # @property
    # def user(self):
    #     return self.ws.handler.active_client.user

    # @user.setter
    # def user(self, obj):
    #     self.ws.handler.active_client.user = obj

    # @user.deleter
    # def user(self, obj):
    #     del self.ws.handler.active_client.user

    # def update_state(self):
    #     self.broadcast('users_map', {
    #         'users': {
    #             'update': [
    #                 char.to_dict() for char in local_db['characters']],
    #             'remove': []
    #         }
    #     })

    def on_open(self):
        local_db.setdefault('characters', set())
        logging.debug("Connection opened")

    def on_message(self, message):
        if message:
            message = json.loads(message)
            logging.info('Evaluate msg %s' % message['msg_type'])
            getattr(self, message['msg_type'])(message)

    def player_equip(self, message):
        self.user.equip(message['data']['equipment'])

    def player_heal(self, message):
        self.user.heal()

    def register_user(self, message):
        self.user = CharacterModel.create('hello')
        print(self.user.id)
        local_db['characters'].add(self.user)
        self.broadcast('register_user', self.user.to_dict())

    def unregister_user(self, message):
        char_id = self.user.id
        if char_id is not None:
            self._g_cleaner(self.user)
            main_queue.put_nowait(char_id)

    def player_move(self, message):
        self.user.move(message['data']['action'], message['data']['direction'])

    def player_shoot(self, message):
        self.user.shoot()


def main_ticker(server):
    local_db.setdefault('characters', set())
    while True:
        gevent.sleep(0.01)
        print('--------')
        data = {
            'users': {
                'update': [
                    char.to_dict() for char in local_db['characters']
                ],
                'remove': []
            },
            'count': len(server.clients),
        }
        try:
            result = main_queue.get_nowait()
            data['users']['remove'].append(result)
        except:
            pass

        for client in server.clients.values():
            try:
                client.ws.send(json.dumps({
                    'msg_type': 'users_map', 'data': data}))
            except WebSocketError as e:
                GameApplication._g_cleaner(client.user)
                logging.error(e)


if __name__ == '__main__':
    try:
        CharacterModel.delete()
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
