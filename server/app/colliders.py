"""Main collision logic
"""
import random
import logging
from contextlib import contextmanager

from db import local_db


class SpatialHash(object):

    def __init__(self, cell_size=32):
        self.cell_size = float(cell_size)
        self.contents = {}

    def _hash(self, point):
        if isinstance(point, (tuple, list)):
            px = point[0]
            py = point[1]
        else:
            px = point['x']
            py = point['y']
        return int(px / self.cell_size), int(py / self.cell_size)

    def insert_object_for_point(self, point, obj):
        self.contents.setdefault(self._hash(point), set()).add(obj)

    def insert_object_for_box(self, box, obj):
        for cell in self._get_cells(box):
            # append to each intersecting cell
            self.contents.setdefault(cell, set()).add(obj)

    def _get_cells(self, box):
        # hash the minimum and maximum points
        box['min'] = (box['min'] if isinstance(box['min'], (list, tuple))
                      else (box['min']['x'], box['min']['y']))
        box['max'] = (box['max'] if isinstance(box['max'], (list, tuple))
                      else (box['max']['x'], box['max']['y']))
        min, max = self._hash(box['min']), self._hash(box['max'])
        return ((i, j) for j in range(min[1], max[1] + 1)
                for i in range(min[0], max[0] + 1))

    def remove_obj_by_point(self, point, obj):
        try:
            cell = self.contents[self._hash(point)]
            cell.remove(obj)
        except KeyError:
            pass

    def remove_obj_by_box(self, box, obj):
        for cell in self._get_cells(box):
            try:
                cell = self.contents[cell]
                cell.remove(obj)
            except KeyError:
                pass

    def pottential_collisions(self, box, obj, single=False):
        potensial_collisions = set()
        if single:
            cells = [self._hash(box)]
        else:
            cells = self._get_cells(box)

        for cell in cells:
            try:
                for el in self.contents[cell]:
                    potensial_collisions.add(el)
            except KeyError:
                pass

        try:
            potensial_collisions.remove(obj)
        except KeyError:
            pass
        logging.debug(potensial_collisions)
        return potensial_collisions


spatial_hash = SpatialHash()


@contextmanager
def obj_update(obj):
    try:
        spatial_hash.remove_obj_by_point(obj.pivot, obj)
    except AttributeError:
        pass
    yield
    spatial_hash.insert_object_for_point(obj.pivot, obj)


class CollisionManager(object):

    def __init__(self, obj, pipelines=None):
        self.obj = obj
        self.pipelines = (pipelines
                          if isinstance(pipelines, (tuple, list)) else [])
        logging.debug(spatial_hash.contents)
        spatial_hash.insert_object_for_point(obj.pivot, obj)

    @staticmethod
    def get_random_coords():
        x = random.randint(0, local_db['map_size']['width'] - 100)
        y = random.randint(0, local_db['map_size']['height'] - 100)
        return (x, y)

    @property
    def is_collide(self):
        result = False
        for col_func in self.pipelines:
            coll_func = getattr(self, col_func, None)
            if callable(coll_func):
                result = coll_func()
                if result:
                    break

        return result

    def map_collision(self):
        if (
            self.obj.x > local_db['map_size']['width'] - 100 or
            self.obj.x < 0 or
            self.obj.y > local_db['map_size']['height'] - 100 or
            self.obj.y + self.obj.height / 1.2 < 0
        ):
            return True
        return False

    def user_collision(self):
        colliders = spatial_hash.pottential_collisions(
            self.obj.pivot, self.obj, True)
        for other in colliders:
            if self._is_collide(other):
                return True
        else:
            return False

    def _is_collide(self, other):
        from .models import UserModel
        if isinstance(other, UserModel):
            return False
        return bool(self.obj.pivot['x'] < other.x + other.width and
                    self.obj.pivot['x'] >= other.x and
                    self.obj.pivot['y'] < other.y + other.height and
                    self.obj.pivot['y'] >= other.y)
