from gevent import monkey; monkey.patch_all()  # noqa

import re
import gevent
import zmq.green as zmq
import time
import logging

from conf import settings
from utils import setup_logging

from app.models import UserModel
from utils import enum_names
import constants as const

from db import mongo_db


class EventDispatcherZMQ(object):

    def __init__(self):
        self.db = mongo_db
        self._context = zmq.Context()
        self.socket = self._context.socket(zmq.REP)
        logging.info('ZMQ: Binding address (%s, %s)', *settings.ZMQ_ADDRESS)
        self.socket.bind("tcp://%s:%s" % settings.ZMQ_ADDRESS)

    def start(self):
        logging.info('ZMQ: Server REP starting...')
        gevent.spawn(self._run).join()

    def _run(self):
        while True:
            msg = self.socket.recv_json()
            logging.info('ZMQ: received msg - %s', msg)
            getattr(self, msg['type'])(msg['data'])

    def send(self, type, status, message, data=None):
        if data is None:
            data = {}
        self.socket.send_json({
            'type': type,
            'time': time.time(),
            'data': data,
            'status': status,
            'message': message
        })

    def registration(self, msg):
        user = UserModel(**msg)
        try:
            user.save()
        except Exception as e:
            logging.error('ZMQ: %s', e.message)
            self.send('registration', 'error', 'Unexpected error')
        else:
            self.send('registration', 'ok', 'Success', user.to_dict())

    def login(self, msg):
        username = msg.get('username')
        password = msg.get('password')

        if len(username) < 4:
            self.send('login', 'error',
                      'Username must be not less than 4 symbols.')
            return

        if len(password) < 8:
            self.send('login', 'error',
                      'Password must be not less than 8 symbols.')
            return

        logging.info('ZMQ: Got password - %s' % password)
        try:
            user = UserModel.objects.get(username=username)
            logging.info('ZMQ: User password - %s' % user.password)
            if not user.check_password(password):
                self.send('login', 'error', 'Invalid password.')
                return
        except UserModel.DoesNotExist:
            user = UserModel(username=username)
            user.hash_password(password)
            user.save()
            logging.info('ZMQ: User hased password as - %s' % user.password)

        self.send('login', 'ok', 'Success', user.to_dict())

    def constants(self, msg):
        resp = {
            re.search(r'\'(.*?)\'', str(typo)).group(1): {
                name: getattr(typo, name).value
                for name in enum_names(typo)
            } for typo in [
                const.Armor, const.Weapon, const.Direction,
                const.Position, const.Action
            ]
        }
        self.send('constants', 'ok', 'Success', resp)


if __name__ == '__main__':
    setup_logging()
    server_mq = EventDispatcherZMQ()
    server_mq.start()
