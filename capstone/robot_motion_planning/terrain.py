from cell import Cell

dir_reverse = {'u': 'd', 'r': 'l', 'd': 'u', 'l': 'r',
               'up': 'd', 'right': 'l', 'down`': 'u', 'left': 'r'}
dir_sensors = {'u': ['l', 'u', 'r'], 'r': ['u', 'r', 'd'],
               'd': ['r', 'd', 'l'], 'l': ['d', 'l', 'u'],
               'up': ['l', 'u', 'r'], 'right': ['u', 'r', 'd'],
               'down': ['r', 'd', 'l'], 'left': ['d', 'l', 'u']}

robot_directions = {'u': '^', 'r': '>', 'd': 'V', 'l': '<',
                    'up': '^', 'right': '>', 'down': 'V', 'left': '<'}

opposite_wall = {'0': 2, '1': 3, '2': 0, '3': 1}
index_walls = {'l': 0, 'u': 1, 'r': 2, 'd': 3,
               'left': 0, 'up': 1, 'right': 2, 'down': 3}

WALL_VALUE = 99


class Terrain:
    def __init__(self, maze_dim):
        self.maze_dim = maze_dim
        self.grid = [[Cell() for i in range(maze_dim)] for j in range(maze_dim)]
        self.fill_distances()
        self.last_visited_cell = None
        self.cells_to_check = []

    def fill_distances(self):
        """
        Fills initial distances of the maze, assuming there are no walls.
        """
        center = self.maze_dim / 2
        max_distance = self.maze_dim - 2

        # Fill top left half
        for i in range(0, center):
            for j in range(center):
                self.grid[i][j].distance = max_distance - j - i

        # The two rows in the center should be equal
        for i in range(center, center + 1):
            for j in range(0, center):
                self.grid[i][j].distance = self.grid[i - 1][j].distance

        # Fill bottom left half
        for i in range(center + 1, self.maze_dim):
            for j in range(0, center):
                self.grid[i][j].distance = self.grid[i - 1][j].distance + 1

        # The two rows in the center should have the same values
        for i in range(0, self.maze_dim):
            for j in range(center, center + 1):
                self.grid[i][j].distance = self.grid[i][j - 1].distance

        # Fill remaining columns
        for i in range(0, self.maze_dim):
            for j in range(center + 1, self.maze_dim):
                self.grid[i][j].distance = self.grid[i][j - 1].distance + 1

    def print_row_of_cells(self, cells, include_delimiters=True):
        """
        Prints a single row of cells.
        :param cells: array or cells of the same y position
        :param include_delimiters: false to prevent duplicate walls
        """
        if include_delimiters:
            top = ''
            middle = '\n'
            bottom = '\n'
            for cell in cells:
                top += cell.top()
                middle += cell.middle()
                bottom += cell.bottom()
            result = top + middle + bottom
        else:
            middle = ''
            for cell in cells:
                middle += cell.middle()
            result = middle

        print(result)

    def print_row_of_cells_double(self, cells):
        top = ''
        middle = '\n'
        bottom = '\n'
        for cell in cells:
            top += cell.top()
            middle += cell.middle()
            bottom += cell.bottom()
        result = top + middle + bottom
        print(result)

    def draw(self):
        """
        Print maze with correct x and y axes
        """
        mod_terrain = []
        for i in range(self.maze_dim):
            mod_terrain.append([x[i] for x in self.grid])

        print_delimiters = True
        for i, row in enumerate(reversed(mod_terrain)):
            self.print_row_of_cells(row, print_delimiters)
            print_delimiters = not print_delimiters  # Flip value

        # # TODO: delete these lines
        # import pdb
        # pdb.set_trace()

    def draw_double(self):
        """
        Print maze with correct x and y axes
        """
        mod_terrain = []
        for i in range(self.maze_dim):
            mod_terrain.append([x[i] for x in self.grid])

        for i, row in enumerate(reversed(mod_terrain)):
            self.print_row_of_cells_double(row)

        # TODO: delete these lines
        import pdb
        pdb.set_trace()

    def update(self, x, y, heading, real_walls):

        # Get reference to current position
        cell = self.grid[x][y]

        # Store real_walls only if cell has not been visited (can't change)
        # Imaginary walls can't change; walls are updated before location
        if cell.visited == '':
            cell.real_walls = real_walls
            # Set adjacent walls (i.e. right wall of cell A is left wall of B)
            self.update_adjacent_walls(x, y, real_walls, 'real')

        # Visited value can change (includes direction)
        cell.visited = robot_directions[heading]

        # Change visual representation of direction (to draw it correctly)
        if self.last_visited_cell is not None \
                and self.last_visited_cell != cell:
            self.last_visited_cell.visited = '*'

        # Set last visited cell to this cell
        self.last_visited_cell = cell

        # Update all the distances of the visited cells of the maze
        self.update_distances()

    def update_imaginary_walls(self, x, y, imaginary_walls):

        # Get reference to current position
        cell = self.grid[x][y]

        cell.imaginary_walls = imaginary_walls
        self.update_adjacent_walls(x, y, imaginary_walls, 'imaginary')

        # Update all the distances of the visited cells of the maze
        self.update_distances()

    def get_index_of_wall(self, direction):
        return index_walls[direction]

    def get_distance(self, x, y, direction):
        # Left
        if direction == 'l' or direction == 'left':
            return self.grid[x - 1][y].distance
        # Up
        if direction == 'u' or direction == 'up':
            return self.grid[x][y + 1].distance
        # Right
        if direction == 'r' or direction == 'right':
            return self.grid[x + 1][y].distance
        # Down
        if direction == 'd' or direction == 'down':
            return self.grid[x][y - 1].distance

    def get_visited(self, x, y, direction):
        # Left
        if direction == 'l' or direction == 'left':
            return self.grid[x - 1][y].visited
        # Up
        if direction == 'u' or direction == 'up':
            return self.grid[x][y + 1].visited
        # Right
        if direction == 'r' or direction == 'right':
            return self.grid[x + 1][y].visited
        # Down
        if direction == 'd' or direction == 'down':
            return self.grid[x][y - 1].visited

    def get_adjacent_distances(self, x, y, heading, last_movement, sensors):

        # Placeholder (robot's coordinates)
        distances = [WALL_VALUE, WALL_VALUE, WALL_VALUE, WALL_VALUE]
        visited = ['', '', '', '']

        for i in range(len(sensors)):
            if sensors[i] != 0:
                dir_sensor = dir_sensors[heading][i]
                distances[i] = self.get_distance(x, y, dir_sensor)
                visited[i] = self.get_visited(x, y, dir_sensor)

        # Update missing distance (cell right behind the robot)
        # This is only valid if the last step was not rotation or reverse
        if last_movement != 0 and last_movement != -1:
            behind = dir_reverse[heading]
            distances[3] = self.get_distance(x, y, behind)
            visited[3] = self.get_visited(x, y, behind)

        return distances, visited

    def get_adjacent_distances_visited_cells(self, x, y):

        # Placeholder: left, up, right, down
        distances = [WALL_VALUE, WALL_VALUE, WALL_VALUE, WALL_VALUE]

        walls = self.grid[x][y].get_total_walls()

        for i, wall in enumerate(walls):
            if wall == 0:
                # Left
                if i == 0:
                    new_x = x - 1
                    new_y = y
                # Up
                elif i == 1:
                    new_x = x
                    new_y = y + 1
                # Right
                elif i == 2:
                    new_x = x + 1
                    new_y = y
                # Down
                else:
                    new_x = x
                    new_y = y - 1

                distances[i] = self.grid[new_x][new_y].distance

        return distances

    def update_distances(self):

        # While stack is not empty
        while len(self.cells_to_check) != 0:

            # Update current cell and get it's distance
            current_cell = self.cells_to_check.pop()
            x = current_cell[0]
            y = current_cell[1]
            current_distance = self.grid[x][y].distance

            # Get adjacent distances
            adj_distances = self.get_adjacent_distances_visited_cells(x, y)

            # Get the minimum
            min_distance = min(adj_distances)

            # If the cell we are standing on is not min_distance + 1
            if current_distance != min_distance + 1:

                # First update this cell's distance
                self.grid[x][y].distance = min_distance + 1

                # Then push adjacent cells to the stack
                for i, adj_distance in enumerate(adj_distances):
                    if adj_distance != WALL_VALUE:
                        # Left
                        if i == 0:
                            new_x = x - 1
                            new_y = y
                        # Up
                        elif i == 1:
                            new_x = x
                            new_y = y + 1
                        # Right
                        elif i == 2:
                            new_x = x + 1
                            new_y = y
                        # Down
                        else:
                            new_x = x
                            new_y = y - 1

                        # Add to stack only if location has been visited
                        new_cell = self.grid[new_x][new_y]
                        if new_cell.visited != '' and new_cell.visited != 'x':
                            location = [new_x, new_y]
                            self.cells_to_check.append(location)

    def reset_visited_flags(self):
        for x in range(self.maze_dim):
            for y in range(self.maze_dim):
                self.grid[x][y].visited = ''

    def is_valid_location(self, x, y):
        return 0 <= x <= self.maze_dim - 1 and 0 <= y <= self.maze_dim - 1

    def update_adjacent_walls(self, x, y, walls, type_of_wall):

        # Left
        if self.is_valid_location(x - 1, y):
            left = 0
            index = opposite_wall[str(left)]
            new_x = x - 1
            new_y = y
            value = walls[left]
            self.set_value_of_wall(new_x, new_y, value, index, type_of_wall)

        # Up
        if self.is_valid_location(x, y + 1):
            up = 1
            index = opposite_wall[str(up)]
            new_x = x
            new_y = y + 1
            value = walls[up]
            self.set_value_of_wall(new_x, new_y, value, index, type_of_wall)

        # Right
        if self.is_valid_location(x + 1, y):
            right = 2
            index = opposite_wall[str(right)]
            new_x = x + 1
            new_y = y
            value = walls[right]
            self.set_value_of_wall(new_x, new_y, value, index, type_of_wall)

        # Down
        if self.is_valid_location(x, y - 1):
            down = 3
            index = opposite_wall[str(down)]
            new_x = x
            new_y = y - 1
            value = walls[down]
            self.set_value_of_wall(new_x, new_y, value, index, type_of_wall)

        # # Left
        # if self.is_valid_location(x - 1, y):
        #     self.grid[x - 1][y].real_walls[] = real_walls[0]
        #     self.grid[x - 1][y].imaginary_walls[opposite_wall['0']] = \
        #         imaginary_walls[0]
        #
        # # Up
        # if self.is_valid_location(x, y + 1):
        #     self.grid[x][y + 1].real_walls[opposite_wall['1']] = real_walls[1]
        #     self.grid[x][y + 1].imaginary_walls[opposite_wall['1']] = \
        #         imaginary_walls[1]
        #
        # # Right
        # if self.is_valid_location(x + 1, y):
        #     self.grid[x + 1][y].real_walls[opposite_wall['2']] = real_walls[2]
        #     self.grid[x + 1][y].imaginary_walls[opposite_wall['2']] = \
        #         imaginary_walls[2]
        #
        # # Down
        # if self.is_valid_location(x, y - 1):
        #     self.grid[x][y - 1].real_walls[opposite_wall['3']] = real_walls[3]
        #     self.grid[x][y - 1].imaginary_walls[opposite_wall['3']] = \
        #         imaginary_walls[3]



    def set_value_of_wall(self, x, y, value, index, type_of_wall):

        if type_of_wall == 'real':
            self.grid[x][y].real_walls[index] = value

        elif type_of_wall == 'imaginary':
            self.grid[x][y].imaginary_walls[index] = value

