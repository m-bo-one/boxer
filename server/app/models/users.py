from __future__ import division

import json
import time

from utils import generate_temp_password, generate_token, check_temp_password

from . import MongoModelMixin


class UserModel(MongoModelMixin):

    fields = (
        'username',
        'password',
        'token',
        'created_at',
        'updated_at'
    )
    model_key = staticmethod(lambda: 'users')

    def __init__(self, username, password=None, **kwargs):
        self._id = None
        self.username = username
        self.password = password
        self.created_at = None
        self.updated_at = None
        self.token = None

    def check_password(self, password):
        return check_temp_password(password, self.password)

    def hash_password(self, password):
        self.password = generate_temp_password(password)

    def save(self):
        if not self._id:
            self.created_at = time.time()
            self.token = generate_token()
        self.updated_at = time.time()
        super(UserModel, self).save()

    def to_dict(self):
        return {
            'username': self.username,
            'token': self.token
        }

    def to_json(self):
        return json.dumps(self.to_dict())
