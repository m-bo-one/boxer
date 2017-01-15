from __future__ import division

import json
import datetime

from mongoengine import Document, StringField, DateTimeField, ListField

from utils import generate_token

from .characters import CharacterModel


class UserModel(Document):

    CHAR_LIMIT = 3

    meta = {'collection': 'users'}

    token = StringField(required=True, max_length=255)
    username = StringField(required=True, max_length=16)
    hash = StringField(required=True, max_length=255)
    email_addr = StringField(required=True, max_length=255)
    creation_date = DateTimeField(default=datetime.datetime.utcnow)
    last_login = DateTimeField(default=datetime.datetime.utcnow)
    desc = StringField(required=True, max_length=255, default='')
    role = StringField(required=True, max_length=10)
    characters = ListField(default=[])

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
        return [CharacterModel.get(cid) for cid in self.characters]

    def add_character(self, name, race):
        chars = self.get_characters()
        if len(chars) < self.CHAR_LIMIT:
            char = CharacterModel.create(user_id=str(self.id), name=name,
                                         race=race)
            self.characters.append(char.id)
        else:
            raise TypeError('Only %s characters allowed.' % self.CHAR_LIMIT)

    def remove_character(self, cid):
        if not self.characters:
            raise IndexError('Nothing to delete.')
        if cid in self.characters:
            char = CharacterModel.get(cid)
            if char.user_id == str(self.id):
                CharacterModel.delete(cid)
                self.characters.remove(cid)
