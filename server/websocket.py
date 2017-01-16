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
from app.engine.colliders import spatial_hash


main_queue = Queue()


class GameApplication(WebSocketApplication):

    @staticmethod
    def _g_cleaner(user):
        # spatial_hash.remove_obj_by_point(user.pivot, user)
        CharacterModel._kill_AP_threads(user.id)
        try:
            del CharacterModel.AP_stats[user.id]
        except KeyError:
            pass
        try:
            local_db['characters'].remove(user)
        except KeyError:
            pass

    def broadcast(self, msg_type, data):
        try:
            self.ws.send(json.dumps({'msg_type': msg_type, 'data': data}))
        except WebSocketError as e:
            GameApplication._g_cleaner(self.user)
            logging.error(e)

    def on_open(self):
        local_db.setdefault('characters', set())
        logging.debug("Connection opened")

    def on_message(self, message):
        if message:
            message = json.loads(message)
            logging.info('Evaluate msg %s' % message['msg_type'])
            getattr(self, message['msg_type'])(message.get('data', None))

    def player_equip(self, message):
        self.user.equip(message['equipment'])

    def player_heal(self, message):
        self.user.heal()

    def register_user(self, message):
        self.user = CharacterModel.create(user_id=1, name='hello')
        print(self.user.id)
        local_db['characters'].add(self.user)
        self.broadcast('register_user', self.user.to_dict())

    def unregister_user(self, message):
        char_id = self.user.id
        if char_id is not None:
            self._g_cleaner(self.user)
            main_queue.put_nowait(char_id)

    def player_move(self, message):
        self.user.move(message['action'], message['direction'])

    def player_shoot(self, message):
        self.user.shoot()

    def player_build_path(self, message):
        self.user.build_path(message['point'])


def main_ticker(server):
    local_db.setdefault('characters', set())
    while True:
        gevent.sleep(0.01)
        data = {
            'users': {
                'update': [
                    char.to_dict() for char in local_db['characters']
                ],
                'remove': []
            },
            'count': len(server.clients),
        }
        if not main_queue.empty():
            result = main_queue.get_nowait()
            data['users']['remove'].append(result)

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
        log_params = {}
        if not settings.DEBUG:
            log_params = {
                'default_level': logging.ERROR
            }
        setup_logging(**log_params)
        logging.info('Starting server...\n')
        server = WebSocketServer(
            settings.WEBSOCKET_ADDRESS, Resource(OrderedDict({
                '/game': GameApplication
            })))
        server._spawn(main_ticker, server)
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Killing server...\n')
