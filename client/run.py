# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from gevent import monkey; monkey.patch_all()  # noqa

import logging
import time
import hashlib
import json

import gevent
import gevent.pool

import zmq.green as zmq

import bottle

from eventemitter import EventEmitter
from conf import settings
from utils import setup_logging


class BaseHttpRunner(object):

    MAX_WORKERS = 20

    def __init__(self, address):
        self._app = bottle.Bottle()
        self._pool = gevent.pool.Pool(self.MAX_WORKERS)
        self._host = address[0]
        self._port = address[1]
        self._debug = settings.DEBUG
        self.evt = EventEmitter()

        self._connect_zmq()

        bottle.TEMPLATE_PATH.insert(0, settings.CLIENT_PATH)
        self._register_routes()

    def _connect_zmq(self):
        self._context = zmq.Context()
        self.zmq_socket = self._context.socket(zmq.REQ)
        logging.info('ZMQ: Conneting to address (%s, %s)',
                     *settings.ZMQ_ADDRESS)
        self.zmq_socket.connect("tcp://%s:%s" % settings.ZMQ_ADDRESS)

    def _zmq_request(self, type, data):
        return {
            'type': type,
            'time': time.time(),
            'data': data
        }

    def _zmq_response(self, req):
        def _callback(req):
            self.zmq_socket.send_json(req)
            resp = self.zmq_socket.recv_json()
            return resp['data']
        thread = self._pool.spawn(_callback, req)
        return thread.get()

    def template_with_context(self, template_name, **extra):
        context = {
            'SRC_URL': settings.SRC_URL,
            'ASSETS_URL': settings.ASSETS_URL,
            'FILE_VERSION': (hashlib.md5(str(time.time())).hexdigest()
                             if not settings.TEMPLATE_DEBUG else ''),
            'FILE_VERSION': '',
            'APP_SETTINGS': json.dumps(self.app_settings)
        }
        if isinstance(extra, dict):
            context.update(**extra)

        return bottle.template(template_name, **context)

    @property
    def app_settings(self):
        return {
            'DEBUG': settings.TEMPLATE_DEBUG,
            'FPS': settings.FPS
        }

    @property
    def request(self):
        """Just a wrapper
        """
        return bottle.request

    @staticmethod
    def json_response(data, status_code=200):
        response = bottle.response
        response.content_type = 'application/json'
        response.status = status_code
        return json.dumps(data)

    def _register_routes(self):
        """Assign routes here
        """
        self._app.route('/', method="GET",
                        callback=self.handler_index)
        self._app.route('/assets/<filename:re:.*\.(jpg|png|gif|ico|svg)>',
                        callback=self.handler_image)
        self._app.route('/assets/<filename:re:.*\.(ogg|mp3)>',
                        callback=self.handler_music)
        self._app.route('/assets/<filename:path>',
                        callback=self.handler_asset)
        self._app.route('/src/<filename:path>',
                        callback=self.handler_src)

        self._app.route('/api/login', method='POST',
                        callback=self.api_login)

    def handler_music(self, filename):
        return bottle.static_file(filename,
                                  root=settings.ASSETS_PATH)

    def handler_image(self, filename):
        return bottle.static_file(filename,
                                  root=settings.ASSETS_PATH)

    def handler_asset(self, filename):
        return bottle.static_file(filename,
                                  root=settings.ASSETS_PATH)

    def handler_src(self, filename):
        return bottle.static_file(filename,
                                  root=settings.SRC_PATH)

    def handler_index(self):
        """Base index page
        """
        return self.template_with_context('index.html')

    def api_login(self):
        request = self._zmq_request('login', self.request.json)
        result = self._zmq_response(request)
        if not result:
            return self.json_response({
                'status': 'error',
                'message': 'Server error'
            }, 500)
        elif result['status'] == 'error':
            return self.json_response({
                'status': 'error',
                'message': result['message']
            }, 400)
        elif result['status'] == 'ok':
            return self.json_response({
                'status': 'ok',
                'message': result['message'],
                'data': result['data']
            })

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
