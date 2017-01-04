from cell import Cell

robot_directions = {'u': '^', 'r': '>', 'd': 'V', 'l': '<',
                    'up': '^', 'right': '>', 'down': 'V', 'left': '<'}

WALL_VALUE = 10000


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

    def print_row_of_cells(self, cells):
        """
        Prints a single row of cells.
        :param cells: array or cells of the same y position
        """
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

        for row in reversed(mod_terrain):
            self.print_row_of_cells(row)

        # TODO: delete these lines
        import pdb
        pdb.set_trace()

    def update(self, x, y, walls, heading):

        # Get reference to cell
        cell = self.grid[x][y]

        # Store new walls and heading values
        cell.walls = walls
        cell.direction = robot_directions[heading]

        # Change visual representation of direction (to draw it correctly)
        if self.last_visited_cell is not None and self.last_visited_cell != cell:
            self.last_visited_cell.direction = '*'

        # Set last visited cell to this cell
        self.last_visited_cell = cell

        # Update all the distances of the visited cells of the maze
        self.update_distances()

    def get_distance(self, x, y, direction):
        # Left
        if direction == 'l' or direction == 'left':
            return self.grid[x - 1][y].distance
        # Up
        if direction == 'u' or direction =='up':
            return self.grid[x][y + 1].distance
        # Right
        if direction == 'r' or direction == 'right':
            return self.grid[x + 1][y].distance
        if direction == 'd' or direction == 'down':
            return self.grid[x][y - 1].distance

    def get_adjacent_distances_visited_cells(self, x, y):

        # Placeholder: left, up, right, down
        distances = [WALL_VALUE, WALL_VALUE, WALL_VALUE, WALL_VALUE]

        walls = self.grid[x][y].walls

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
                        if self.grid[new_x][new_y].direction != '':
                            location = [new_x, new_y]
                            self.cells_to_check.append(location)
