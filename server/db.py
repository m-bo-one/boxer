import logging

import gevent
import redis
import redis.connection

__all__ = [
    'redis_db',
    'local_db',
]


class DBClient(object):

    shared_state = {}
    max_connections = 200

    def __init__(self):
        self.__dict__ = self.shared_state

    def connect(self, name):
        try:
            return self.shared_state[name]
        except KeyError:
            logging.info('Perform new connection to %s', name)
            if name == 'redis':
                redis.connection.socket = gevent.socket
                pool = redis.ConnectionPool.from_url(
                    url='redis://127.0.0.1:6379?db=0',
                    max_connections=self.max_connections)
                self.shared_state[name] = redis.Redis(connection_pool=pool)
            elif name == 'local':
                self.shared_state[name] = {
                    'map_size': {
                        'width': 1280,
                        'height': 768
                    }
                }
            else:
                raise Exception('Connector not found.')

            return self.shared_state[name]


redis_db = DBClient().connect('redis')
local_db = DBClient().connect('local')
