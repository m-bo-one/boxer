from __future__ import division

import json
import time

from db import mongo_db
from utils import generate_temp_password, generate_token, check_temp_password

from . import ModelMixin


class UserModel(ModelMixin):

    fields = (
        'id',
        'username',
        'password',
        'token',
        'created_at',
        'updated_at'
    )
    collection = staticmethod(lambda: mongo_db['users'])

    def __init__(self, username, password):
        self.id = None
        self.username = username
        self.password = generate_temp_password(password)
        self.created_at = None
        self.updated_at = None
        self.token = None

    def check_password(self, password):
        return check_temp_password(password, self.password)

    def save(self):
        if not self.id:
            self.created_at = time.time()
            self.token = generate_token()
        self.updated_at = time.time()
        self.collection.insert({
            field: getattr(self, field) for field in self.fields
        })

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'token': self.token
        }

    def to_json(self):
        return json.dumps(self.to_dict())
