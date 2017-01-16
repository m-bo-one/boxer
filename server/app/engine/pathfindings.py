import heapq
import constants as const

from .colliders import spatial_hash


# class SquareGrid:
#     def __init__(self, width, height):
#         self.width = width
#         self.height = height
#         self.walls = []

#     def in_bounds(self, point):
#         spatial_hash
#         (x, y) = id
#         return 0 <= x < self.width and 0 <= y < self.height

#     def passable(self, id):
#         return id not in self.walls

#     def neighbors(self, id):
#         (x, y) = id
#         results = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
#         if (x + y) % 2 == 0:
#             results.reverse()  # aesthetics
#         results = filter(self.in_bounds, results)
#         results = filter(self.passable, results)
#         return results


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
        const.Direction.W: lambda p, s: (p[0] - s[0], p[1]),
        const.Direction.E: lambda p, s: (p[0] + s[0], p[1]),
        const.Direction.N: lambda p, s: (p[0], p[1] - s[1]),
        const.Direction.S: lambda p, s: (p[0], p[1] + s[1]),
    }

    def __init__(self, obj, directions):
        self.queue = PriorityQueue()
        self.obj = obj
        self.directions = directions
        self.came_from = {}
        self.cost_so_far = {}

    def _possible_steps(self, point):
        steps = []
        for direction in self.directions:
            steps.append(self.dir_funcs[direction](point, self.obj.speed))
        return steps

    def passable(self, point):
        return not spatial_hash.is_predict_point_collide(point)

    def get_neighbors(self, point):
        return filter(self.passable, self._possible_steps(point))

    @staticmethod
    def heuristic(a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    @property
    def start(self):
        return (self.obj.x, self.obj.y)

    def a_star_search(self, goal):
        if goal[0] % self.obj.speed[0] or goal[1] % self.obj.speed[1]:
            raise TypeError('Wrong speed for this coordinates.')
        frontier = PriorityQueue()
        frontier.put(self.start, 0)
        self.came_from = {}
        self.cost_so_far = {}
        self.came_from[self.start] = None
        self.cost_so_far[self.start] = 0

        counter = 0

        while not frontier.empty():
            print(counter)
            current = frontier.get()

            if current == goal:
                break

            for next in self.get_neighbors(current):
                new_cost = self.cost_so_far[current] + 1
                if (next not in self.cost_so_far or
                   new_cost < self.cost_so_far[next]):
                    self.cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    self.came_from[next] = current

            counter += 1

    def reconstruct_path(self, goal):
        if not self.came_from.get(goal):
            raise TypeError('Path not builded.')
        current = goal
        path = [current]
        # yield current
        while current != self.start:
            current = self.came_from[current]
            # yield current
        # yield self.start
            path.append(current)
        path.append(self.start)  # optional
        path.reverse()  # optional
        return path

    @classmethod
    def build_path(cls, obj, goal, alg='A*'):
        p = Pathfinder(obj, [
            const.Direction.W,
            const.Direction.S,
            const.Direction.E,
            const.Direction.N,
        ])
        if alg == 'A*':
            p.a_star_search(goal)
        return p.reconstruct_path(goal)
