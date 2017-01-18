import math
import heapq
import constants as const

from conf import settings
from db import local_db

from .colliders import spatial_hash


class PriorityQueue(object):

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Pathfinder(object):

    dir_funcs = {
        const.Direction.W: lambda p, s: (p[0] - s, p[1]),
        const.Direction.E: lambda p, s: (p[0] + s, p[1]),
        const.Direction.N: lambda p, s: (p[0], p[1] - s),
        const.Direction.S: lambda p, s: (p[0], p[1] + s),

        const.Direction.SW: lambda p, s: (p[0] + s, p[1] + s),
        const.Direction.SE: lambda p, s: (p[0] - s, p[1] + s),
        const.Direction.NE: lambda p, s: (p[0] - s, p[1] - s),
        const.Direction.NW: lambda p, s: (p[0] + s, p[1] - s),
    }

    def __init__(self, obj, chop_directions):
        self.queue = PriorityQueue()
        self.obj = obj
        self.came_from = {}
        self.cost_so_far = {}
        self.chop_directions = chop_directions
        self.start = self._centralize_cell(self.obj.coords)

    @staticmethod
    def _centralize_cell(cell, cell_size=settings.GAME['CELL_SIZE']):
        x = int((cell[0] // cell_size) * cell_size)
        y = int((cell[1] // cell_size) * cell_size)
        print((x + cell_size / 2, y + cell_size / 2))
        return (x + cell_size / 2, y + cell_size / 2)

    def _possible_steps(self, point, goal):
        steps = []
        for direction in self._aesthetics_directions(point, goal):
            steps.append(self.dir_funcs[direction](
                point, self.obj._footpace[0]))
        return steps

    @staticmethod
    def passable(point):
        return not spatial_hash.is_predict_point_collide(point)

    @staticmethod
    def in_bounds(point):
        from .colliders import spatial_hash
        return spatial_hash.in_bounds(point)

    def get_neighbors(self, point, goal):
        steps = self._possible_steps(point, goal)
        steps = filter(self.in_bounds, steps)
        return filter(self.passable, steps)

    def _aesthetics_directions(self, point, goal):
        if point[0] <= goal[0] and point[1] <= goal[1]:
            if goal[0] - point[0] > goal[1] - point[1]:
                directions = [const.Direction.E,
                              const.Direction.SE,
                              const.Direction.S,
                              const.Direction.NE,
                              const.Direction.N,
                              const.Direction.NW,
                              const.Direction.W,
                              const.Direction.SW
                              ]
            else:
                directions = [
                              const.Direction.S,
                              const.Direction.SE,
                              const.Direction.E,
                              const.Direction.NE,
                              const.Direction.N,
                              const.Direction.NW,
                              const.Direction.W,
                              const.Direction.SW
                              ]
        elif point[0] <= goal[0] and point[1] >= goal[1]:
            if goal[0] - point[0] > -(goal[1] - point[1]):
                directions = [const.Direction.E,
                              const.Direction.NE,
                              const.Direction.N,
                              const.Direction.SE,
                              const.Direction.S,
                              const.Direction.NW,
                              const.Direction.W,
                              const.Direction.SW
                              ]
            else:
                directions = [
                              const.Direction.N,
                              const.Direction.NE,
                              const.Direction.E,
                              const.Direction.SE,
                              const.Direction.S,
                              const.Direction.NW,
                              const.Direction.W,
                              const.Direction.SW
                              ]
        elif point[0] >= goal[0] and point[1] <= goal[1]:
            if -(goal[0] - point[0]) > goal[1] - point[1]:
                directions = [const.Direction.W,
                              const.Direction.SW,
                              const.Direction.S,
                              const.Direction.SE,
                              const.Direction.N,
                              const.Direction.NW,
                              const.Direction.E,
                              const.Direction.NE,
                              ]
            else:
                directions = [
                              const.Direction.S,
                              const.Direction.SW,
                              const.Direction.W,
                              const.Direction.SE,
                              const.Direction.N,
                              const.Direction.NW,
                              const.Direction.E,
                              const.Direction.NE,
                              ]
        elif point[0] >= goal[0] and point[1] >= goal[1]:
            if -(goal[0] - point[0]) > -(goal[1] - point[1]):
                directions = [const.Direction.W,
                              const.Direction.NW,
                              const.Direction.N,
                              const.Direction.NE,
                              const.Direction.S,
                              const.Direction.NW,
                              const.Direction.E,
                              const.Direction.NE,
                              ]
            else:
                directions = [
                              const.Direction.N,
                              const.Direction.NW,
                              const.Direction.W,
                              const.Direction.NE,
                              const.Direction.S,
                              const.Direction.NW,
                              const.Direction.E,
                              const.Direction.NE,
                              ]
        return [d for d in directions if d not in self.chop_directions]

    @classmethod
    def heuristic(cls, a, b):
        return cls._euclidean_distance(b, a)

    @staticmethod
    def _manhattan_distance(point, goal):
        (x1, y1) = point
        (x2, y2) = goal
        return abs(x1 - x2) + abs(y1 - y2)

    @staticmethod
    def _diagonal_distance(point, goal):
        (x1, y1) = point
        (x2, y2) = goal
        return max(abs(x1 - x2), abs(y1 - y2))

    @staticmethod
    def _euclidean_distance(point, goal):
        (x1, y1) = point
        (x2, y2) = goal
        return math.sqrt(abs(x1 - x2) ** 2 + abs(y1 - y2) ** 2)

    def g_bfs_search(self, goal):
        frontier = PriorityQueue()
        frontier.put(self.start, 0)
        self.came_from = {}
        self.came_from[self.start] = None

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break

            for next in self.get_neighbors(current, goal):
                if next not in self.came_from:
                    priority = self.heuristic(goal, next)
                    frontier.put(next, priority)
                    self.came_from[next] = current

    def a_star_search(self, goal):
        frontier = PriorityQueue()
        frontier.put(self.start, 0)
        self.came_from = {}
        self.cost_so_far = {}
        self.came_from[self.start] = None
        self.cost_so_far[self.start] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break

            for next in self.get_neighbors(current, goal):
                new_cost = self.cost_so_far[current]
                if (next not in self.cost_so_far or
                   new_cost < self.cost_so_far[next]):
                    self.cost_so_far[next] = new_cost + \
                        self.cost_so_far.get(current, 1)
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    self.came_from[next] = current

    def reconstruct_path(self, goal):
        if not self.came_from.get(goal):
            return
            yield
        else:
            current = goal
            yield current
            while current != self.start:
                current = self.came_from[current]
                yield current

    @classmethod
    def build_path(cls, obj, goal, alg='A*', chop_directions=None):
        if chop_directions is None:
            chop_directions = []
        goal = cls._centralize_cell(goal)
        # check if clicked point has no collision
        if not cls.passable(goal) or not cls.in_bounds(goal):
            return []
        p = Pathfinder(obj, chop_directions)
        if alg == 'A*':
            p.a_star_search(goal)
        elif alg == 'BFS':
            p.g_bfs_search(goal)
        return p.reconstruct_path(goal)
