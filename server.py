# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from gevent import monkey; monkey.patch_all()  # noqa

import sys
import signal

import gevent
import gevent.pool

import bottle


class BaseHttpRunner(object):

    MAX_WORKERS = 20

    def __init__(self, host='127.0.0.1', port=8080):
        self._app = bottle.Bottle()
        self._pool = gevent.pool.Pool(self.MAX_WORKERS)
        self._host = host
        self._port = port
        self._debug = True

        self._register_routes()

        # register signal for killing mongoclient at ctrl+c
        signal.signal(signal.SIGHUP,
                      lambda signum, traceback: self.client.close())

    @property
    def request(self):
        """Just a wrapper
        """
        return bottle.request

    def _register_routes(self):
        """Assign routes here
        """
        self._app.route('/', method="GET", callback=self.handler_index)

    def handler_index(self):
        """Takes url as parameter, send to mongo queue collection
        """
        return bottle.template('index.html')

    def run_forever(self):
        """Start gevent server here
        """
        try:
            print('Starting server...\n')
            self._app.run(server='gevent', fast=True,  # user wsgi, not pywsgi
                          host=self._host, port=self._port,
                          reloader=self._debug, interval=0.1,
                          quiet=not self._debug)
        except KeyboardInterrupt:
            print('Killing server...\n')
            sys.exit()


if __name__ == '__main__':
    server = BaseHttpRunner()
    server.run_forever()
