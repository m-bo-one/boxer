# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from gevent import monkey; monkey.patch_all()  # noqa

import logging
import signal

import gevent
import gevent.pool

import bottle

from utils import setup_logging, PY2


class BaseHttpRunner(object):

    MAX_WORKERS = 20

    def __init__(self, address):
        self._app = bottle.Bottle()
        self._pool = gevent.pool.Pool(self.MAX_WORKERS)
        self._host = address[0]
        self._port = address[1]
        self._debug = True

        self._register_routes()

        # register signal for killing mongoclient at ctrl+c
        if PY2:
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
        self._app.route('/static/<filename:path>', method="GET",
                        callback=self.handler_static)

    def handler_static(self, filename):
        return bottle.static_file(filename, root='static')

    def handler_index(self):
        """Base index page
        """
        return bottle.template('templates/index.html')

    def run_forever(self):
        """Start gevent server here
        """
        self._app.run(server='gevent', fast=True,  # user wsgi, not pywsgi
                      host=self._host, port=self._port,
                      reloader=self._debug, interval=0.1,
                      quiet=not self._debug)


if __name__ == '__main__':
    try:
        setup_logging()
        logging.info('Starting server...\n')
        server = BaseHttpRunner(('127.0.0.1', 8080))
        server.run_forever()
    except KeyboardInterrupt:
        logging.info('Killing server...\n')
