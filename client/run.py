# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from gevent import monkey; monkey.patch_all()  # noqa

import logging
import time
import hashlib
import json

import gevent
import gevent.pool
from gevent.pool import Semaphore

import zmq.green as zmq

import bottle
from beaker.middleware import SessionMiddleware
from cork import Cork
from cork.cork import AuthException, AAAException

from conf import settings
from db import mongo_db
from utils import setup_logging


class BaseHttpRunner(object):

    MAX_WORKERS = 20

    def __init__(self, address):
        self._sapp = SessionMiddleware(bottle.Bottle(), settings.SESSION_OPTS)
        self.app = self._sapp.app
        self._pool = gevent.pool.Pool(self.MAX_WORKERS)
        self._host = address[0]
        self._port = address[1]
        self._debug = settings.DEBUG
        self._lock = Semaphore()
        self.populate_mongodb_backend()
        self.ceng = Cork(backend=mongo_db)

        self._connect_zmq()

        bottle.TEMPLATE_PATH.insert(0, settings.CLIENT_PATH)
        self._register_routes()

    @staticmethod
    def populate_mongodb_backend():
        mongo_db.roles._coll.remove({})
        mongo_db.roles._coll.insert({'role': 'admin', 'val': 100})
        mongo_db.roles._coll.insert({'role': 'editor', 'val': 60})
        mongo_db.roles._coll.insert({'role': 'user', 'val': 50})

    def _connect_zmq(self):
        self._context = zmq.Context()
        self.zmq_socket = self._context.socket(zmq.REQ)
        logging.info('ZMQ: Conneting to address (%s, %s)',
                     *settings.ZMQ_ADDRESS)
        self.zmq_socket.connect("tcp://%s:%s" % settings.ZMQ_ADDRESS)

    def _zmq_request(self, type, data=None):
        if data is None:
            data = {}
        return {
            'type': type,
            'time': time.time(),
            'data': data
        }

    def _zmq_response(self, req):
        with self._lock:
            self._zmq_send(req)
            return self.zmq_socket.recv_json()

    def _zmq_send(self, req):
        self.zmq_socket.send_json(req)

    def prepare_context(self, **extra):
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

        context['current_user'] = self.ceng.current_user \
            if not self.ceng.user_is_anonymous else None

        return context

    @property
    def app_settings(self):
        return {
            'DEBUG': settings.TEMPLATE_DEBUG,
            'FPS': settings.FPS,
            'is_authorized': not self.ceng.user_is_anonymous
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
        self.app.route('/', method="GET",
                       callback=self.handler_index)
        self.app.route('/assets/<filename:re:.*\.(jpg|png|gif|ico|svg)>',
                       callback=self.handler_image)
        self.app.route('/assets/<filename:re:.*\.(ogg|mp3)>',
                       callback=self.handler_music)
        self.app.route('/assets/<filename:path>',
                       callback=self.handler_asset)
        self.app.route('/src/<filename:path>',
                       callback=self.handler_src)

        self.app.route('/api/login', method='POST',
                       callback=self.api_login)
        self.app.route('/api/registration', method='POST',
                       callback=self.api_registration)
        self.app.route('/api/constants', method='GET',
                       callback=self.api_constants)

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

    @bottle.jinja2_view('index.html')
    def handler_index(self):
        """Base index page
        """
        return self.prepare_context()

    def zmq_parse(f):
        def wrapper(self, *args, **kwargs):
            result = f(self, *args, **kwargs)
            status, msg, data = (result['status'], result['message'],
                                 result['data'])
            if not status:
                return self.json_response({
                    'status': 'error',
                    'message': 'Server error'
                }, 500)
            elif status == 'error':
                return self.json_response({
                    'status': 'error',
                    'message': msg
                }, 400)
            elif status == 'ok':
                return self.json_response({
                    'status': 'ok',
                    'message': msg,
                    'data': data
                })
        return wrapper

    def _create_simple_user(self, username, password, role='user'):
        if username in self.ceng._store.users:
            raise AAAException("User is already existing.")
        if role not in self.ceng._store.roles:
            raise AAAException("Nonexistent role")
        if self.ceng._store.roles[role] > 50:
            raise AAAException("Unauthorized role")

        req = self._zmq_request('registration', {
            'username': username,
            'role': role,
            'hash': self.ceng._hash(username, password).decode('ascii'),
            'email_addr': username
        })
        resp = self._zmq_response(req)
        if resp['status'] == 'error':
            raise Exception('ZMQ Error response, detail: %s' % str(resp))

    def api_registration(self):
        username = self.request.json.get('username')
        password = self.request.json.get('password')

        if len(username) < 4:
            return self.json_response({
                'status': 'error',
                'message': 'Username must be not less than 4 symbols.'
            }, 400)

        if len(password) < 8:
            return self.json_response({
                'status': 'error',
                'message': 'Password must be not less than 8 symbols.'
            })

        try:
            username = username.strip()
            password = password.strip()
            self._create_simple_user(username, password)
            self.ceng.login(username, password)
        except (AAAException, AuthException) as e:
            return self.json_response({
                'status': 'error',
                'message': e.message
            }, 400)
        except Exception as e:
            logging.error('API: %s', e.message)
            return self.json_response({
                'status': 'error',
                'message': 'Server error'
            }, 500)
        else:
            return self.json_response({
                'status': 'ok',
                'message': 'Success',
                'data': {
                    'username': username
                }
            })

    def api_login(self):
        username = self.request.json.get('username')
        password = self.request.json.get('password')

        if self.ceng.login(username, password):
            return self.json_response({
                'status': 'ok',
                'message': 'Success',
                'data': {
                    'username': username
                }
            })
        else:
            return self.json_response({
                'status': 'error',
                'message': 'Invalid username or password'
            }, 400)

    @zmq_parse
    def api_constants(self):
        request = self._zmq_request('constants')
        return self._zmq_response(request)

    def run_forever(self):
        """Start gevent server here
        """
        bottle.run(app=self._sapp,
                   server='gevent', fast=True,  # user wsgi, not pywsgi
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
