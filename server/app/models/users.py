from __future__ import division

import json
import datetime

from mongoengine import Document, StringField, DateTimeField

from utils import generate_token
from db import redis_db

from .characters import CharacterModel


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

    def get_characters(self):
        chars_data = redis_db.hgetall(":".join([self.meta['collection'],
                                                str(self.id),
                                                'characters']))
        return ([CharacterModel(**json.loads(data))
                for data in chars_data.itervalues()]
                if chars_data is not None else [])

    def add_character(self, name, race=None):
        chars = self.get_characters()
        if len(chars) < 3:
            return UserModel.create(name=name)
        else:
            raise TypeError('Only 3 characters allowed.')
