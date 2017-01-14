import json

from bson.objectid import ObjectId
from enum import IntEnum, Enum

from db import redis_db

from .weapons import Weapon
from .armors import Armor


def field_extractor(inst):
    data = {}
    for field in inst.fields:
        value = getattr(inst, field)
        if isinstance(value, (Enum, IntEnum)):
            value = value.value
        elif isinstance(value, (Weapon, Armor)):
            value = value.name.value
        data[field] = value
    return data


class RedisModelMixin(object):

    @staticmethod
    def model_key():
        raise NotImplementedError()

    def save(self):
        if not self.id:
            self.id = redis_db.incr('%s:ids' % self.model_key())

        data = json.dumps(field_extractor(self))
        return redis_db.hset(self.model_key(), self.id, data)

    @classmethod
    def get(cls, id):
        data = redis_db.hget(cls.model_key(), id)
        if data:
            return cls(**json.loads(data))

    @classmethod
    def delete(cls, id=None):
        if not id:
            return redis_db.delete(cls.model_key())
        return redis_db.hdel(cls.model_key())


class MongoModelMixin(object):

    @property
    def id(self):
        if self._id:
            return str(self._id)

    @staticmethod
    def model_key():
        raise NotImplementedError()

    @classmethod
    def get_collection(cls):
        from db import DBClient
        mongo_db = DBClient().connect('mongo')
        return mongo_db[cls.model_key()]

    def save(self):
        data = {field: getattr(self, field) for field in self.fields}
        _id = self.get_collection().insert(data)
        if not self._id:
            self._id = ObjectId(_id)

    @classmethod
    def delete(cls, ids):
        ids = [ObjectId(_id) for _id in ids]
        return cls.get_collection().remove({'_id': {'$in': ids}})

    def remove(self):
        rm = self.get_collection().remove({'_id': ObjectId(self._id)})
        self._id = None
        return rm

    @classmethod
    def get(cls, id):
        doc = cls.get_collection().find_one({'_id': ObjectId(id)})
        if not doc:
            raise TypeError('Collection %s with id - %s does not exist.' %
                            cls.model_key(), id)
        return cls._update(doc)

    @classmethod
    def _update(cls, doc):
        model_inst = cls(**doc)
        model_inst._id = doc['_id']
        for field in cls.fields:
            setattr(model_inst, field, doc[field])
        return model_inst

    @classmethod
    def filter(cls, **kwargs):
        return [cls._update(doc)
                for doc in cls.get_collection().find(**kwargs)]

    @classmethod
    def all(cls):
        return cls.filter()
