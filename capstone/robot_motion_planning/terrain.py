from cell import Cell
from global_variables import (dir_reverse, dir_sensors, opposite_wall,
                              robot_directions, wall_index, MAX_DISTANCES,
                              WALL_VALUE)


class Terrain:
    """
    Used by the robot to create a visual representation of the maze.
    It contains all the logic for the movement (fill maze, update distances,
    etc) as well as methods for debugging the program (i.e. printing the maze).
    """
    def __init__(self, maze_dim):
        self.maze_dim = maze_dim
        self.grid = [[Cell() for i in range(maze_dim)] for j in range(maze_dim)]
        self.fill_distances()
        self.last_visited_cell = None
        self.cells_to_check = []
        self.visited_before_reaching_destination = []

    # --------------------------------------------
    # FOR FLOOD-FILL ALGORITHM
    # --------------------------------------------

    def fill_distances(self):
        """
        Fills initial distances of the maze assuming there are no walls.
        It's the 1st step of the flood fill algorithm, used to guide the robot.
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

    # --------------------------------------------
    # UPDATE FUNCTIONS
    # --------------------------------------------

    def update(self, x, y, heading, walls, exploring):
        """
        Updates the maze's:
        - Real walls (including adjacent wall's)
        - Visual representation of the current cell
        - Visual representation of the previous cell
        - Distances of adjacent cells
        """

        # Get reference to current position
        cell = self.grid[x][y]

        # Store real_walls only if cell has not been visited.
        # Imaginary walls can't change; walls are updated before location.
        if cell.visited == '':
            cell.real_walls = walls
            # Set adjacent walls (i.e. right wall of cell A is left wall of B)
            self.update_adjacent_walls(x, y, walls, 'real')

        # Change the visual representation of the current cell
        cell.visited = robot_directions[heading]

        # Change visual representation of the previous cell
        self.change_visual_representation_of_prev_cell(cell, exploring)

        # Set last visited cell to this cell
        self.last_visited_cell = cell

        # Update all the distances of the visited cells of the maze
        self.update_distances()

    def change_visual_representation_of_prev_cell(self, curr_cell, exploring):
        """
        All visited cells during exploration are marked with 'e'. All
        other visited cells are marked with *, provided they are not the
        current cell the robot is standing on, or the cell is not a dead end.
        """
        if self.last_visited_cell is not None \
                and self.last_visited_cell != curr_cell \
                and self.last_visited_cell.visited is not 'x':
            if not exploring:
                self.last_visited_cell.visited = '*'
            else:
                self.last_visited_cell.visited = 'e'

    def update_imaginary_walls(self, x, y, imaginary_walls):
        """
        Adds adjacent imaginary walls, and updates distances of the maze
        to account for the new found imaginary walls.
        """

        # Get reference to current position
        cell = self.grid[x][y]

        cell.imaginary_walls = imaginary_walls
        self.update_adjacent_walls(x, y, imaginary_walls, 'imaginary')

        # Update all the distances of the visited cells of the maze
        self.update_distances()

    def get_index_of_wall(self, direction):
        return wall_index[direction]

    def get_distance(self, x, y, direction, steps=1):
        walls = self.grid[x][y].get_total_walls()
        distance = WALL_VALUE

        # Left
        if direction == 'l' or direction == 'left':
            if walls[wall_index['l']] == 0 \
                    and self.is_valid_location(x - steps, y):
                cell = self.grid[x - steps][y]
                distance = self.grid[x - steps][y].distance
        # Up
        if direction == 'u' or direction == 'up':
            if walls[wall_index['u']] == 0 \
                    and self.is_valid_location(x, y + steps):
                cell = self.grid[x][y + steps]
                distance = self.grid[x][y + steps].distance
        # Right
        if direction == 'r' or direction == 'right':
            if walls[wall_index['r']] == 0 \
                    and self.is_valid_location(x + steps, y):
                cell = self.grid[x + steps][y]
                distance = self.grid[x + steps][y].distance
        # Down
        if direction == 'd' or direction == 'down':
            if walls[wall_index['d']] == 0 \
                    and self.is_valid_location(x, y - steps):
                cell = self.grid[x][y - steps]
                distance = self.grid[x][y - steps].distance

        return distance

    def get_visited_flag(self, x, y, direction, steps=1):
        walls = self.grid[x][y].get_total_walls()
        visited = ''

        # Left
        if direction == 'l' or direction == 'left':
            if walls[wall_index['l']] == 0 \
                    and self.is_valid_location(x - steps, y):
                visited = self.grid[x - steps][y].visited
        # Up
        if direction == 'u' or direction == 'up':
            if walls[wall_index['u']] == 0 \
                    and self.is_valid_location(x, y + steps):
                visited = self.grid[x][y + steps].visited
        # Right
        if direction == 'r' or direction == 'right':
            if walls[wall_index['r']] == 0 \
                    and self.is_valid_location(x + steps, y):
                visited = self.grid[x + steps][y].visited
        # Down
        if direction == 'd' or direction == 'down':
            if walls[wall_index['d']] == 0 \
                    and self.is_valid_location(x, y - steps):
                visited = self.grid[x][y - steps].visited

        return visited

    def get_adj_info(self, x, y, heading, sensors, get_cell_behind=True):
        """
        Returns adjacent distances and visited flags in robot's coordinates
        """

        distances = list(MAX_DISTANCES)
        visited = ['', '', '', '']

        for i in range(len(sensors)):
            if sensors[i] != 0:
                dir_sensor = dir_sensors[heading][i]
                distances[i] = self.get_distance(x, y, dir_sensor)
                visited[i] = self.get_visited_flag(x, y, dir_sensor)

        # Update missing distance (cell right behind the robot)
        if get_cell_behind:
            behind = dir_reverse[heading]
            distances[3] = self.get_distance(x, y, behind)
            visited[3] = self.get_visited_flag(x, y, behind)

        return distances, visited

    def get_adjacent_distances_for_cell(self, x, y):

        distances = list(MAX_DISTANCES)
        distances[0] = self.get_distance(x, y, 'left')
        distances[1] = self.get_distance(x, y, 'up')
        distances[2] = self.get_distance(x, y, 'right')
        distances[3] = self.get_distance(x, y, 'down')

        return distances

    def update_distances(self, last_update=False):

        if last_update:
            cells_to_check = list(self.visited_before_reaching_destination)
        else:
            cells_to_check = self.cells_to_check

        # While stack is not empty
        while len(cells_to_check) != 0:

            # Update current cell and get it's distance
            current_cell = cells_to_check.pop()
            x = current_cell[0]
            y = current_cell[1]
            current_distance = self.grid[x][y].distance

            # Get adjacent distances
            adj_distances = self.get_adjacent_distances_for_cell(x, y)

            # Get the minimum
            min_distance = min(adj_distances)

            # If the cell we are standing on is not min_distance + 1
            if current_distance != min_distance + 1 and current_distance != WALL_VALUE:

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

                        new_cell = self.grid[new_x][new_y]
                        if new_cell.visited != 'x' \
                                and self.is_valid_location(new_x, new_y):
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

    def set_value_of_wall(self, x, y, value, index, type_of_wall):
        """
        Sets the correct value of real an imaginary walls for a given cell
        """
        if type_of_wall == 'real':
            self.grid[x][y].real_walls[index] = value

        elif type_of_wall == 'imaginary':
            self.grid[x][y].imaginary_walls[index] = value

    def set_imaginary_walls_for_unvisited_cells(self):
        """
        Used when first round finished. It converts all unvisited values of
         cells to -1 and places imaginary walls so distances can be updated
         correctly and robot can follow a logical (safe) path to the center.
        """
        for x in range(self.maze_dim):
            for y in range(self.maze_dim):
                cell = self.grid[x][y]
                if cell.visited == '':
                    cell.distance = WALL_VALUE
                    for i in range(4):
                        cell.imaginary_walls[i] = 1

    # --------------------------------------------
    # FOR DEBUGGING
    # --------------------------------------------

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
            top += cell.top_double()
            middle += cell.middle_double()
            bottom += cell.bottom_double()
        result = top + middle + bottom
        print(result)

    def draw(self):
        """
        Prints maze with correct x and y axes.
        """
        mod_terrain = []
        for i in range(self.maze_dim):
            mod_terrain.append([x[i] for x in self.grid])

        print_delimiters = True
        for i, row in enumerate(reversed(mod_terrain)):
            self.print_row_of_cells(row, print_delimiters)
            print_delimiters = not print_delimiters  # Flip value

    def draw_double(self):
        """
        Prints maze with correct x and y axes. Includes all walls.
        """
        mod_terrain = []
        for i in range(self.maze_dim):
            mod_terrain.append([x[i] for x in self.grid])

        for i, row in enumerate(reversed(mod_terrain)):
            self.print_row_of_cells_double(row)

    def get_percentage_of_maze_explored(self):
        num_cells_in_maze = self.maze_dim * self.maze_dim
        num_cells_explored = len(self.visited_before_reaching_destination)
        return (num_cells_explored * 100) / num_cells_in_maze
