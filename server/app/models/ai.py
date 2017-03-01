import math


from db import local_db


class Turret(object):

    counter = 0

    def __init__(self, x=150, y=150, rrange=200):
        Turret.counter += 1
        self.id = self.counter
        self._range = rrange
        self.x = x
        self.y = y
        self.current_target = None

    def to_dict(self):
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'R': self._range,
            'target': getattr(self.current_target, 'id', None)
        }

    @classmethod
    def get_all(cls):
        return [turret.to_dict() for turret in local_db['turrets']]

    def _multiply_vector(self, coords):
        return math.sqrt((coords[0] - self.x) ** 2 + (coords[1] - self.y) ** 2)

    def in_range(self, target):
        return bool((target.x - self.x) ** 2 + (target.y - self.y) ** 2 <=
                    self._range ** 2)

    def detect_target(self, targets):
        targets = filter(self.in_range, targets)
        new_target = None
        for target in targets:
            if not new_target or (
                self._multiply_vector((new_target.x,
                                       new_target.y)) >
                self._multiply_vector((target.x, target.y))
            ):
                new_target = target
        if new_target:
            self.current_target = new_target
        else:
            self.current_target = None

    def rotate(self):
        raise NotImplementedError()
