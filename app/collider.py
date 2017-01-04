"""Main collision logic
"""
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
        self.contents.setdefault(point, []).append(obj)

    def insert_object_for_box(self, box, obj):
        # hash the minimum and maximum points
        min, max = self._hash(box.min), self._hash(box.max)
        # iterate over the rectangular region
        for i in range(min[0], max[0] + 1):
            for j in range(min[1], max[1] + 1):
                # append to each intersecting cell
                self.contents.setdefault((i, j), []).append(obj)

    def remove_obj_by_point(self, point):
        try:
            del self.contents[point]
        except KeyError:
            pass

    def remove_obj_by_box(self, box):
        # hash the minimum and maximum points
        min, max = self._hash(box.min), self._hash(box.max)
        # iterate over the rectangular region
        for i in range(min[0], max[0] + 1):
            for j in range(min[1], max[1] + 1):
                # remove each intersecting cell
                try:
                    del self.contents[(i, j)]
                except KeyError:
                    pass


class CollisionManager(object):

    def __init__(self, obj, pipelines=None):
        self.obj = obj
        self.pipelines = (pipelines
                          if isinstance(pipelines, (tuple, list)) else [])

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
        # for other in self.__class__.all():
        #     if (self.id != other.id and self.x < other.x + other.width and
        #        self.x + self.width > other.x and
        #        self.y < other.y + other.height and
        #        self.height + self.y > other.y):
        #         return True
        return False
