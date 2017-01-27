cdef enum Htype:
    manhattan = 1
    diagonal = 2
    euclidean = 3


cdef enum Stype:
    BFS = 1
    A = 2


cdef class Queue(object):

    cdef:
        public list elements
        object __weakref__

    cdef bint empty(self)

    cdef void put(self, tuple item)

    cdef tuple get(self)


cdef class PriorityQueue(object):

    cdef:
        public list elements
        object __weakref__

    cdef bint empty(self)

    cdef void put(self, tuple item, int priority)

    cdef tuple get(self)


cdef class Pathfinder(object):

    cdef:
        readonly int cell_size, htype, stype
        readonly double footstep
        readonly list step_filters
        list _step_funcs
        dict _came_from
        object __weakref__

    cdef tuple _centralize_cell(self, tuple cell)

    cdef list _possible_steps(self, tuple point)

    cdef list get_neighbors(self, tuple point)

    cdef double heuristic(self, tuple start_point, tuple end_point)

    cdef double _manhattan_distance(self, tuple start_point, tuple end_point)

    cdef double _diagonal_distance(self, tuple start_point, tuple end_point)

    cdef double _euclidean_distance(self, tuple start_point, tuple end_point)

    cdef void g_bfs_search(self, tuple start_point, tuple end_point)

    cdef void a_star_search(self, tuple start_point, tuple end_point)

    cdef list reconstruct_path(self, tuple start_point, tuple end_point)

    cpdef list search(self, tuple start_point, tuple end_point)
