import logging
import signal

import gevent
import redis
import redis.connection
from mongoengine import connect
from cork.mongodb_backend import (
    MongoDBBackend, MongoMultiValueTable, MongoSingleValueTable)

from conf import settings


__all__ = [
    'redis_db',
    'local_db',
    'mongo_db',
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
            max_connections=db_conf['POOL_MAX_SIZE'])
        return redis.Redis(connection_pool=pool)

    def _local_connector(self):
        return {
            'map_size': {
                'width': 1280,
                'height': 768
            },
            '_char_greenlets': {}
        }

    def _mongo_connector(self):
        class MongoDB(MongoDBBackend):

            def __init__(self,
                         db_name=settings.DATABASES['mongo']['NAME'],
                         hostname=settings.DATABASES['mongo']['HOST'],
                         port=settings.DATABASES['mongo']['PORT'],
                         initialize=False, username=None, password=None,
                         maxPoolSize=settings.DATABASES['mongo'][
                             'POOL_MAX_SIZE'
                         ],
                         maxIdleTimeMS=5):
                connection = connect(db_name, host=hostname, port=port,
                                     maxPoolSize=maxPoolSize,
                                     maxIdleTimeMS=maxIdleTimeMS)

                signal.signal(signal.SIGHUP, lambda s, t: connection.close())
                db = connection[db_name]
                if username and password:
                    db.authenticate(username, password)
                self._db = db
                self.users = MongoMultiValueTable('users', 'username',
                                                  db.users)
                self.pending_registrations = MongoMultiValueTable(
                    'pending_registrations',
                    'pending_registration',
                    db.pending_registrations
                )
                self.roles = MongoSingleValueTable('roles', 'role', db.roles)
                if initialize:
                    self._initialize_storage()
        return MongoDB()

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
