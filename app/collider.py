"""Main collision logic
"""
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
            px = point.x
            py = point.y
        return int(px / self.cell_size), int(py / self.cell_size)

    def insert_object_for_point(self, point, obj):
        self.contents.setdefault(point, set()).add(obj)

    def insert_object_for_box(self, box, obj):
        for cell in self._get_cells(box):
            # append to each intersecting cell
            self.insert_object_for_point(cell, obj)

    def _get_cells(self, box):
        # hash the minimum and maximum points
        min, max = self._hash(box['min']), self._hash(box['max'])
        return ((i, j) for j in range(min[1], max[1] + 1)
                for i in range(min[0], max[0] + 1))

    def remove_obj_by_point(self, point, obj):
        try:
            cell = self.contents[point]
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

    def collides(self, box, obj):
        potensial_collisions = set()
        for cell in self._get_cells(box):
            try:
                for el in self.contents[cell]:
                    if obj != el:
                        potensial_collisions.add(el)
            except KeyError:
                pass
        return potensial_collisions


spatial_hash = SpatialHash()


@contextmanager
def obj_update(obj):
    try:
        spatial_hash.remove_obj_by_box(obj.box, obj)
    except AttributeError:
        pass
    yield
    spatial_hash.insert_object_for_box(obj.box, obj)


class CollisionManager(object):

    def __init__(self, obj, pipelines=None):
        self.obj = obj
        self.pipelines = (pipelines
                          if isinstance(pipelines, (tuple, list)) else [])
        # spatial_hash.insert_object_for_box(obj.box, obj)
        print(spatial_hash.contents)

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
            self.obj.y < 0
        ):
            return True
        return False

    def user_collision(self):
        from .models import UserModel
        users = (user for user in spatial_hash.collides(self.obj.box, self.obj)
                 if isinstance(user, UserModel))
        for other in users:
            if all([
                self.obj.id != other.id, self.obj.x < other.x + other.width,
                self.obj.x + self.obj.width > other.x,
                self.obj.y < other.y + other.height,
                self.obj.height + self.obj.y > other.y
            ]):
                return True
        else:
            return False
