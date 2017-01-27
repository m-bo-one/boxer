# cython: profile=True
cimport cython
from cpython.exc cimport PyErr_CheckSignals

import heapq

cimport pathfindings
import constants as const


cdef extern from "math.h":
    double fabs(double x)
    double sqrt(double x)


cdef _get_nearest_multiple_point(tuple point, double footstep):
    cdef:
        int i
        int point_length = len(point)

    n_point = []
    for i from 0 <= i < point_length:
        t = point[i] % footstep
        if t > 0:
            recal = footstep - t
        else:
            recal = t
        recal += point[i]
        n_point.append(recal)
    return tuple(n_point)


cdef class Queue(object):

    def __cinit__(self):
        self.elements = []

    cdef bint empty(self):
        return len(self.elements) == 0

    cdef void put(self, tuple item):
        self.elements.append(item)

    cdef tuple get(self):
        return self.elements.pop()


cdef class PriorityQueue(object):

    def __cinit__(self):
        self.elements = []

    cdef bint empty(self):
        return len(self.elements) == 0

    cdef void put(self, tuple item, int priority):
        heapq.heappush(self.elements, (priority, item))

    cdef tuple get(self):
        return heapq.heappop(self.elements)[1]


cdef class Pathfinder(object):

    def __cinit__(self, double footstep, int cell_size, int htype, int stype,
                  list step_filters):
        self.footstep = footstep
        self.cell_size = cell_size
        self.htype = htype
        self.stype = stype
        self.step_filters = step_filters
        self.step_filters.append(
            lambda tuple point: (0 <= point[0] < 10000 and
                                 0 <= point[1] < 10000))
        self._came_from = {}
        self._step_funcs = {
            const.Direction.W: lambda tuple p: (<double>p[0] - self.footstep,
                                                <double>p[1]),
            const.Direction.E: lambda tuple p: (<double>p[0] + self.footstep,
                                                <double>p[1]),
            const.Direction.N: lambda tuple p: (<double>p[0],
                                                <double>p[1] - self.footstep),
            const.Direction.S: lambda tuple p: (<double>p[0],
                                                <double>p[1] + self.footstep),

            const.Direction.SW: lambda tuple p: (<double>p[0] + self.footstep,
                                                 <double>p[1] + self.footstep),
            const.Direction.SE: lambda tuple p: (<double>p[0] - self.footstep,
                                                 <double>p[1] + self.footstep),
            const.Direction.NE: lambda tuple p: (<double>p[0] - self.footstep,
                                                 <double>p[1] - self.footstep),
            const.Direction.NW: lambda tuple p: (<double>p[0] + self.footstep,
                                                 <double>p[1] - self.footstep),
        }

    @cython.cdivision(True)
    cdef tuple _centralize_cell(self, tuple cell):
        return (
            (cell[0] // self.cell_size) * self.cell_size + self.cell_size / 2,
            (cell[1] // self.cell_size) * self.cell_size + self.cell_size / 2
        )

    cdef list _possible_steps(self, tuple point):
        cdef:
            int i
            list steps = []
        for i from 0 <= i < len(self._step_funcs):
            steps.append(self._step_funcs[i](point))
        return steps

    cdef list get_neighbors(self, tuple point):
        cdef:
            int i, j
            int fc = 0

            list filtered_steps = []
            list steps = self._possible_steps(point)

            int steps_length = len(steps)
            int filters_length = len(self.step_filters)

        for i from 0 <= i < steps_length:
            for j from 0 <= j < filters_length:
                if self.step_filters[j](steps[i]):
                    fc += 1
            if fc == filters_length:
                filtered_steps.append(steps[i])
            fc = 0
        return filtered_steps

    cdef double heuristic(self, tuple start_point, tuple end_point):
        if self.htype == Htype.manhattan:
            return self._manhattan_distance(start_point, end_point)
        elif self.htype == Htype.diagonal:
            return self._diagonal_distance(start_point, end_point)
        elif self.htype == Htype.euclidean:
            return self._euclidean_distance(start_point, end_point)

    cdef double _manhattan_distance(self, tuple start_point, tuple end_point):
        return (fabs(start_point[0] - start_point[1]) +
                fabs(end_point[0] - end_point[1]))

    cdef double _diagonal_distance(self, tuple start_point, tuple end_point):
        return max(fabs(start_point[0] - start_point[1]),
                   fabs(end_point[0] - end_point[1]))

    cdef double _euclidean_distance(self, tuple start_point, tuple end_point):
        return sqrt(fabs(start_point[0] - start_point[1]) ** 2 +
                    fabs(end_point[0] - end_point[1]) ** 2)

    cdef void g_bfs_search(self, tuple start_point, tuple end_point):
        cdef:
            Queue frontier = Queue()
        frontier.put(start_point)

        self._came_from = {}
        self._came_from[start_point] = None

        while not frontier.empty():
            current = frontier.get()

            if current == end_point:
                break

            for next in self.get_neighbors(current):
                if next not in self._came_from:
                    frontier.put(next)
                    self._came_from[next] = current

            PyErr_CheckSignals()

    cdef void a_star_search(self, tuple start_point, tuple end_point):
        cdef:
            PriorityQueue frontier = PriorityQueue()
            dict cost_so_far = {}
        frontier.put(start_point, 0)

        self._came_from = {}
        self._came_from[start_point] = None

        cost_so_far[start_point] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == end_point:
                break

            for next in self.get_neighbors(current):
                new_cost = cost_so_far[current]
                if (next not in cost_so_far or
                   new_cost < cost_so_far[next]):
                    cost_so_far[next] = new_cost + cost_so_far.get(current, 1)
                    priority = new_cost + self.heuristic(next, end_point)
                    frontier.put(next, priority)
                    self._came_from[next] = current

            PyErr_CheckSignals()

    cdef list reconstruct_path(self, tuple start_point, tuple end_point):
        cdef tuple current = end_point
        cdef list path = [current]

        while current != start_point:
            current = self._came_from[current]
            path.append(current)

            PyErr_CheckSignals()

        return path

    cpdef list search(self, tuple start_point, tuple end_point):
        cdef:
            int j
            int filters_length = len(self.step_filters)

        for j from 0 <= j < filters_length:
            if not self.step_filters[j](end_point):
                raise Exception('Goal point lie in filtered.')

        start_point = _get_nearest_multiple_point(start_point, self.footstep)

        if self.stype == Stype.A:
            self.a_star_search(start_point, end_point)
        elif self.stype == Stype.BFS:
            self.g_bfs_search(start_point, end_point)

        return self.reconstruct_path(start_point, end_point)


    @staticmethod
    def quicktest():
        return Pathfinder(2, 32, Htype.euclidean, Stype.A, []) \
            .search((0, 0), (9000, 9000))
