from global_variables import WALL_VALUE


class Algorithm(object):
    def __init__(self):
        self.name = None

    def get_valid_index(self, adjacent_distances, adjacent_visited):
        raise NotImplementedError('Subclasses need to implement this method')


class AlwaysRight(Algorithm):
    def __init__(self):
        super(AlwaysRight, self).__init__()
        self.name = 'always-right'

    def get_valid_index(self, adjacent_distances, adjacent_visited):
        if adjacent_distances[2] != WALL_VALUE:
            valid_index = 2
        elif adjacent_distances[1] != WALL_VALUE:
            valid_index = 1
        elif adjacent_distances[0] != WALL_VALUE:
            valid_index = 0
        else:
            valid_index = 3

        return valid_index


class ModifiedRight(Algorithm):
    def __init__(self):
        super(ModifiedRight, self).__init__()
        self.name = 'modified-right'

    def get_valid_index(self, adjacent_distances, adjacent_visited):
        if adjacent_distances[2] != WALL_VALUE and adjacent_visited[2] != '*':
            valid_index = 2
        elif adjacent_distances[1] != WALL_VALUE and adjacent_visited[1] != '*':
            valid_index = 1
        elif adjacent_distances[0] != WALL_VALUE and adjacent_visited[0] != '*':
            valid_index = 0
        elif adjacent_distances[2] != WALL_VALUE:
            valid_index = 2
        elif adjacent_distances[1] != WALL_VALUE:
            valid_index = 1
        elif adjacent_distances[0] != WALL_VALUE:
            valid_index = 0
        else:
            valid_index = 3

        return valid_index


class FloodFill(Algorithm):
    def __init__(self):
        super(FloodFill, self).__init__()
        self.name = 'flood-fill'

    def get_valid_index(self, adjacent_distances, adjacent_visited):

        # Get min index (guaranteed to not be a wall)
        valid_index = adjacent_distances.index(min(adjacent_distances))

        possible_distance = WALL_VALUE
        for i, dist in enumerate(adjacent_distances):
            # Prefer unvisited cells
            if dist != WALL_VALUE and adjacent_visited[i] is '':
                if dist <= possible_distance:
                    valid_index = i
                    smallest_distance = dist
                    possible_distance = smallest_distance
                    # Index 1 is for the forward direction (the fastest)
                    if valid_index == 1:
                        break

        return valid_index
