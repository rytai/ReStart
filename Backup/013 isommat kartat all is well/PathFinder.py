from pygame import time
from random import sample
from priority_dict import priority_dict

__author__ = 'Kodex'


class PathFinder:
    class Node:
        position = (0, 0)
        parent = None
        g_cost = None
        h_cost = None

        def __init__(self, position=(0, 0)):
            self.position = position
            self.g_cost = 0
            self.h_cost = 0
            self.parent = None

            self.heap = 0

        @property
        def position_x(self):
            return self.position[0]

        @property
        def position_y(self):
            return self.position[1]

        def f_cost(self):
            return self.g_cost + self.h_cost

        f_cost = property(f_cost)

    class Grid:
        nodes = {}

        def __init__(self, _list_of_open_tiles):
            """

            :rtype : Grid
            """
            self.nodes = {position: PathFinder.Node(position) for position in _list_of_open_tiles}

    def __init__(self, _list_of_open_tiles):
        """


        :rtype : PathFinder
        """
        self.grid = PathFinder.Grid(_list_of_open_tiles)

        self.cost_of_movement = 10

    def find_path_between_points(self, start_tile, end_tile):
        """


        :param point_a: Tuple(int, int)
        :param point_b: Tuple(int, int)
        :rtype : List(Tuple)
        :rtype time_module: pygame.time
        """

        assert isinstance(start_tile, tuple)
        assert isinstance(end_tile, tuple)

        method_init_time = time.get_ticks()

        # Create start and end nodes.
        try:
            start_node = self.grid.nodes[start_tile]
        except KeyError:
            print "parthfinding error: starting point not in grid(map)"
        target_node = self.grid.nodes[end_tile]

        # Keep track of the open and closed nodes.
        # Add the start node as the first node to start the flood from.
        open_nodes = priority_dict()
        open_nodes[start_node] = 0
        closed_nodes = set()

        # start looping
        while open_nodes.__len__() > 0:

            current_node = open_nodes.pop_smallest()


            # Remove the current node from open set and add it to closed set.
            #open_nodes.remove(current_node)
            closed_nodes.add(current_node)
            # Found the end tile.
            if current_node == target_node:
                complete_path = self.retrace_path(start_node, target_node)

                method_run_time = time.get_ticks() - method_init_time
                print 'Pathfinding completed in {}ms'.format(method_run_time)
                print complete_path
                return complete_path

            for neighbour_node in self.get_neighbours(current_node):
                if neighbour_node in closed_nodes:
                    continue

                assert isinstance(current_node, PathFinder.Node)
                assert isinstance(neighbour_node, PathFinder.Node)
                new_movement_cost_to_neighbor = current_node.g_cost + 10
                # Try to find a lower cost for neighbor, or calculate if it doesn't have one.
                if new_movement_cost_to_neighbor < neighbour_node.g_cost or neighbour_node not in open_nodes.keys():

                    # Calculate the costs for the neighbor
                    neighbour_node.g_cost = new_movement_cost_to_neighbor
                    neighbour_node.h_cost = self.get_distance(neighbour_node, target_node)
                    neighbour_node.parent = current_node

                    open_nodes[neighbour_node] = neighbour_node.f_cost

        return 'path not found'

    def retrace_path(self, start_node, end_node):
        """

        :rtype : [tuple(int,int)s]
        """
        current_node = end_node

        path = [current_node.position]
        
        while current_node != start_node:
            path.append(current_node.parent.position)
            current_node = current_node.parent

        path.reverse()
        return path

    def get_neighbours(self, node):
        """


        :type node: PathFinder.Node
        :rtype : [PathFinder.Node]
        """
        neighbours = []

        # Loop 3x3 grid around the node.
        for x in range(-1, 2):
            for y in range(-1, 2):
                # Do not check the center.
                if x == 0 and y == 0:
                    continue

                check_x, check_y = x + node.position_x, y + node.position_y
                # Add the node in position to neighbours if it exists, otherwise ignore thrown exception.
                try:
                    neighbours.append(self.grid.nodes[(check_x, check_y)])
                except KeyError:
                    pass

        return neighbours

    def get_distance(self, node_a, node_b):
        """

        :type node_a: PathFinder.Node
        :type node_b: PathFinder.Node
        """

        x_difference = abs(node_a.position_x - node_b.position_x)
        y_difference = abs(node_a.position_y - node_b.position_y)

        return max (x_difference, y_difference)

        # source: http://www.growingwiththeweb.com/2012/06/a-pathfinding-algorithm.html
