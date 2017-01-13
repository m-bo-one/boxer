from db import redis_db


class ModelMixin(object):

    @staticmethod
    def model_key():
        raise NotImplementedError()

    def save(self):
        if not self.id:
            self.id = redis_db.incr('%s:ids' % self.model_key())

        data = {}
        for field in self.fields:
            ufield = getattr(self, field)
            if hasattr(ufield, 'name'):
                ufield = ufield.name
            data[field] = ufield
        return redis_db.hmset('%s:%s' % (self.model_key(), self.id), data)

    @classmethod
    def get(cls, id):
        data = redis_db.hgetall('%s:%s' % (cls.model_key(), id))
        if data:
            if not data.get('id'):
                data['id'] = id
            return cls(**data)

    @classmethod
    def delete(cls, id=None):
        if not id:
            keys = redis_db.keys('%s:*' % cls.model_key())
            if keys:
                return redis_db.delete(*keys)
            return
        return redis_db.delete('%s:%s' % (cls.model_key(), id))


from .users import UserModel
from .characters import CharacterModel, CmdModel
