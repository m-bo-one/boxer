import heapq
import constants as const


class PriorityQueue(object):

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def _df(coord):
    # TODO
    return coord


class Pathfinder(object):

    dir_funcs = {
        const.Direction.W: lambda p, s: (p[0] - s[0], p[1]),
        const.Direction.E: lambda p, s: (p[0] + s[0], p[1]),
        const.Direction.N: lambda p, s: (p[0], p[1] - s[1]),
        const.Direction.S: lambda p, s: (p[0], p[1] + s[1]),

        const.Direction.SW: lambda p, s: (p[0] + _df(s[0]), p[1] + _df(s[1])),
        const.Direction.SE: lambda p, s: (p[0] - _df(s[0]), p[1] + _df(s[1])),
        const.Direction.NE: lambda p, s: (p[0] - _df(s[0]), p[1] - _df(s[1])),
        const.Direction.NW: lambda p, s: (p[0] + _df(s[0]), p[1] - _df(s[1])),
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

    @staticmethod
    def passable(point):
        from .colliders import spatial_hash
        return not spatial_hash.is_predict_point_collide(point)

    @staticmethod
    def in_bounds(point):
        from .colliders import spatial_hash
        return spatial_hash.in_bounds(point)

    def get_neighbors(self, point):
        steps = self._possible_steps(point)
        if (point[0] + point[1]) % 2 == 0:
            steps.reverse()  # aesthetics
        steps = filter(self.in_bounds, steps)
        return filter(self.passable, steps)

    @staticmethod
    def heuristic(a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    @property
    def start(self):
        return (self.obj.x, self.obj.y)

    def g_bfs_search(self, goal):
        if goal[0] % self.obj.speed[0] or goal[1] % self.obj.speed[1]:
            raise TypeError('Wrong speed for this coordinates.')

        # check if clicked point has no collision
        if not self.passable(goal) or not self.in_bounds(goal):
            return

        print('Point %s' % str(goal))

        frontier = PriorityQueue()
        frontier.put(self.start, 0)
        self.came_from = {}
        self.came_from[self.start] = None

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break

            for next in self.get_neighbors(current):
                if next not in self.came_from:
                    priority = self.heuristic(goal, next)
                    frontier.put(next, priority)
                    self.came_from[next] = current

    def a_star_search(self, goal):
        if goal[0] % self.obj.speed[0] or goal[1] % self.obj.speed[1]:
            raise TypeError('Wrong speed for this coordinates.')

        # check if clicked point has no collision
        if not self.passable(goal) or not self.in_bounds(goal):
            return

        print('Point %s' % str(goal))

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

            for next in self.get_neighbors(current):
                new_cost = self.cost_so_far[current]
                if (next not in self.cost_so_far or
                   new_cost < self.cost_so_far[next]):
                    self.cost_so_far[next] = new_cost + \
                        self.cost_so_far.get(current, next)
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
    def build_path(cls, obj, goal, alg='A*'):
        goal = tuple(goal)
        p = Pathfinder(obj, [
            const.Direction.N,
            const.Direction.E,
            const.Direction.S,
            const.Direction.W,

            # const.Direction.SW,
            # const.Direction.SE,
            # const.Direction.NE,
            # const.Direction.NW,
        ])
        if alg == 'A*':
            p.a_star_search(goal)
        elif alg == 'BFS':
            p.g_bfs_search(goal)
        return p.reconstruct_path(goal)
