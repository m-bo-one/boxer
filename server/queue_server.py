from gevent import monkey; monkey.patch_all()  # noqa

import gevent
import zmq.green as zmq
import time
import logging

from conf import settings
from utils import setup_logging, generate_temp_password, check_temp_password

from app.models import UserModel


class EventDispatcherZMQ(object):

    def __init__(self):
        self._context = zmq.Context()
        self.socket = self._context.socket(zmq.PAIR)
        logging.info('ZMQ: Binding address (%s, %s)', *settings.ZMQ_ADDRESS)
        self.socket.bind("tcp://%s:%s" % settings.ZMQ_ADDRESS)

    def start(self):
        logging.info('ZMQ: Server PAIR starting...')
        gevent.spawn(self._run).join()

    def _run(self):
        while True:
            msg = self.socket.recv_json()
            logging.info('ZMQ: received msg - %s', msg)
            getattr(self, msg['type'])(msg['data'])

    def send(self, type, data):
        self.socket.send_json({
            'type': type,
            'time': time.time(),
            'data': data
        })

    def login(self, msg):
        username = msg.get('username')
        password = msg.get('password')

        if len(username) < 4:
            self.send('login',
                      {'status': 'fail',
                       'message': 'Username must be not less than 4 symbols.'})
            return

        if len(password) < 8:
            self.send('login',
                      {'status': 'fail',
                       'message': 'Password must be not less than 8 symbols.'})
            return

        try:
            user = filter(lambda user: user['username'] == username,
                          UserModel.all(to_obj=False))[0]
            if not check_temp_password(password, user.password):
                self.send('login', {'status': 'fail',
                                    'message': 'Passwords not equal'})
                return
        except IndexError:
            user = UserModel.create(password=generate_temp_password(password))

        self.send('login', {'status': 'ok', 'uid': user.id})


if __name__ == '__main__':
    setup_logging()
    server_mq = EventDispatcherZMQ()
    server_mq.start()
