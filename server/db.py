import logging
import signal

import gevent
import redis
import redis.connection
import pymongo

from conf import settings

__all__ = [
    'redis_db',
    'local_db',
]


class DBClient(object):

    shared_state = {}
    max_connections = 200

    def __init__(self):
        self.__dict__ = self.shared_state

    def _redis_connector(self):
        db_conf = settings.DATABASES['redis']
        try:
            redis.connection.socket = gevent.socket
        except AttributeError:
            # use default socket connection
            pass
        pool = redis.ConnectionPool.from_url(
            url='redis://%s:%s?db=%s' % (
                db_conf['HOST'], db_conf['PORT'], db_conf['NAME']),
            max_connections=self.max_connections)
        return redis.Redis(connection_pool=pool)

    def _local_connector(self):
        return {
            'map_size': {
                'width': 1280,
                'height': 768
            }
        }

    def _mongo_connector(self):
        db_conf = settings.DATABASES['mongo']
        client = pymongo.MongoClient(db_conf['HOST'], db_conf['PORT'],
                                     maxPoolSize=self.max_connections)
        signal.signal(signal.SIGHUP, lambda s, t: client.close())
        return client[db_conf['NAME']]

    def connect(self, name):
        try:
            return self.shared_state[name]
        except KeyError:
            logging.info('Perform new connection to %s', name)
            self.shared_state[name] = getattr(self, '_%s_connector' % name)()
            return self.shared_state[name]
        except AttributeError:
            raise Exception('Connector not found.')


redis_db = DBClient().connect('redis')
local_db = DBClient().connect('local')
mongo_db = DBClient().connect('mongo')
