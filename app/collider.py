"""Main collision logic
"""


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
    pass
