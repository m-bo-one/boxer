# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from gevent import monkey; monkey.patch_all()  # noqa

import logging
import time
import hashlib
import json

import gevent
import gevent.pool

import bottle

from utils import setup_logging
from conf import settings


class BaseHttpRunner(object):

    MAX_WORKERS = 20

    def __init__(self, address):
        self._app = bottle.Bottle()
        self._pool = gevent.pool.Pool(self.MAX_WORKERS)
        self._host = address[0]
        self._port = address[1]
        self._debug = settings.DEBUG

        bottle.TEMPLATE_PATH.insert(0, settings.TEMPLATES_PATH)
        self._register_routes()

    def template_with_context(self, template_name, **extra):
        context = {
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL,
            'FILE_VERSION': (hashlib.md5(str(time.time())).hexdigest()
                             if not self._debug else ''),
            'APP_SETTINGS': json.dumps(self.app_settings)
        }
        if isinstance(extra, dict):
            context.update(**extra)

        return bottle.template(template_name, **context)

    @property
    def app_settings(self):
        return {
            'WEBSOCKET_ADDRESS': "%s:%s" % settings.WEBSOCKET_ADDRESS,
            'DEBUG': settings.TEMPLATE_DEBUG,
            'FPS': settings.FPS
        }

    @property
    def request(self):
        """Just a wrapper
        """
        return bottle.request

    def _register_routes(self):
        """Assign routes here
        """
        self._app.route('/', method="GET", callback=self.handler_index)
        self._app.route('/media/<filename:re:.*\.(jpg|png|gif|ico|svg)>',
                        callback=self.handler_image)
        self._app.route('/static/<filename:path>',
                        callback=self.handler_static)

    def handler_image(self, filename):
        return bottle.static_file(filename,
                                  root=settings.MEDIA_PATH)

    def handler_static(self, filename):
        return bottle.static_file(filename,
                                  root=settings.STATIC_PATH)

    def handler_index(self):
        """Base index page
        """
        return self.template_with_context('index.html')

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
        server = BaseHttpRunner(settings.SITE_ADDRESS)
        server.run_forever()
    except KeyboardInterrupt:
        logging.info('Killing server...\n')
