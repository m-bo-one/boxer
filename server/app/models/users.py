from __future__ import division

import json
import datetime

from utils import generate_token

from mongoengine import Document, StringField, DateTimeField


class UserModel(Document):

    meta = {'collection': 'users'}

    token = StringField(required=True, max_length=255)
    username = StringField(required=True, max_length=16)
    hash = StringField(required=True, max_length=255)
    email_addr = StringField(required=True, max_length=255)
    creation_date = DateTimeField(default=datetime.datetime.utcnow)
    last_login = DateTimeField(default=datetime.datetime.utcnow)
    desc = StringField(required=True, max_length=255, default='')
    role = StringField(required=True, max_length=10)

    def save(self):
        if not self.id:
            self.token = generate_token()
        super(UserModel, self).save()

    def to_dict(self):
        return {
            'username': self.username,
            'token': self.token
        }

    def to_json(self):
        return json.dumps(self.to_dict())
