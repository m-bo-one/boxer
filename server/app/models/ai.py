import math
import gevent
from gevent.queue import Queue


import constants as const
from db import local_db
from .weapons import Weapon


class Turret(object):

    counter = 0

    def __init__(self,
                 x=local_db['map_size']['width'] / 2,
                 y=local_db['map_size']['height'] / 2):
        Turret.counter += 1
        self.id = self.counter
        self.weapon = Weapon(const.Weapon.TurretGun, self)
        self.x = x
        self.y = y
        self.current_target = None
        self._total_counter = 0
        self._queue = Queue()

        gevent.spawn(self.start)

    def start(self):
        while True:
            cmd = self._queue.get()
            method, args = cmd['method'], cmd['args']
            method(*args)
            self._total_counter -= 1

    def to_dict(self):
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'R': self.weapon.w.RANGE,
            'target': getattr(self.current_target, 'id', None)
        }

    @classmethod
    def get_all(cls):
        return [turret.to_dict() for turret in local_db['turrets']]

    def _multiply_vector(self, coords):
        return math.sqrt((coords[0] - self.x) ** 2 + (coords[1] - self.y) ** 2)

    def in_range(self, target):
        return bool((target.x - self.x) ** 2 + (target.y - self.y) ** 2 <=
                    self.weapon.w.RANGE ** 2)

    def detect_target(self, targets):
        targets = filter(self.in_range, targets)
        new_target = None
        for target in targets:
            if target and (
                target.is_dead or target.display == const.Display.Hidden
            ):
                continue
            if not new_target or (
                self._multiply_vector((new_target.x,
                                       new_target.y)) >
                self._multiply_vector((target.x, target.y))
            ):
                new_target = target
        if new_target:
            self.current_target = new_target
            if self._total_counter < 2:
                self.shoot()
                self._total_counter += 1
        else:
            self.current_target = None

    def shoot(self):
        if not self.current_target or self.current_target.is_dead:
            return

        self._queue.put({
            'method': self.weapon.shoot,
            'args': (self.current_target,)
        })

    def update(self):
        pass

    update_scores = update
