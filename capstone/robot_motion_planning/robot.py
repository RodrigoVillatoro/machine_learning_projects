from terrain import Terrain

# global dictionaries for robot movement and sensing
dir_sensors = {'u': ['l', 'u', 'r'], 'r': ['u', 'r', 'd'],
               'd': ['r', 'd', 'l'], 'l': ['d', 'l', 'u'],
               'up': ['l', 'u', 'r'], 'right': ['u', 'r', 'd'],
               'down': ['r', 'd', 'l'], 'left': ['d', 'l', 'u']}
dir_move = {'u': [0, 1], 'r': [1, 0], 'd': [0, -1], 'l': [-1, 0],
            'up': [0, 1], 'right': [1, 0], 'down': [0, -1], 'left': [-1, 0]}
dir_reverse = {'u': 'd', 'r': 'l', 'd': 'u', 'l': 'r',
               'up': 'd', 'right': 'l', 'down`': 'u', 'left': 'r'}


wall_index = {'l': 0, 'u': 1, 'r': 2, 'd': 3,
              'left': 0, 'up': 1, 'right': 2, 'down': 3}

# Distance placeholder for walls
WALL_VALUE = 99


class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''
        self.total_moves = 0  # Store total number of moves made by the robot
        self.robot_pos = {'location': [0, 0], 'heading': 'up'}  # Current pos
        self.last_movement = 0  # 1 forward, -1 reverse, 0 if it only rotated
        self.reached_destination = False
        self.round = 1

        # Goal
        center = maze_dim/2
        self.center_locations = [
            [center, center], [center - 1, center],
            [center, center - 1], [center - 1, center - 1]]

        self.terrain = Terrain(maze_dim)

        # DEBUG:
        self.terrain.draw()

    def reset_values(self):
        # self.terrain.reset_visited_flags()
        self.total_moves = 0
        self.robot_pos = {'location': [0, 0], 'heading': 'up'}
        self.last_movement = 0
        self.reached_destination = False
        self.round = 2

    def next_move(self, sensors):
        '''
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returning the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        '''

        # Store direction and current location
        heading = self.robot_pos['heading']
        location = self.robot_pos['location']
        x = location[0]
        y = location[1]

        # If it's the starting position, just move forward
        if location == [0, 0]:
            rotation = 0
            movement = 1
            real_walls = [1, 0, 1, 1]
            self.store_last_movement(movement)
            self.total_moves += 1

            # Update terrain
            self.terrain.update(x, y, heading, real_walls)

        # If we have reached the center of the maze
        elif location in self.center_locations:
            # Set rotation and movement to 'Reset'
            rotation = 'Reset'
            movement = 'Reset'

            # State that we have reached destination (used to update_location)
            self.reached_destination = True

        # Else, first update distances, then get next move
        else:

            # 1) Push current location to stack
            self.terrain.cells_to_check.append(location)

            # 2) Add newly discovered walls
            real_walls = self.get_walls_for_current_location(x, y, sensors)

            # 3) Update terrain and distances
            self.terrain.update(x, y, heading, real_walls)

            # 4) Get next move
            rotation, movement = self.get_next_move(x, y, heading, sensors)

        # # DEBUG:
        # if rotation == 'Reset' or self.round == 2:
        self.terrain.draw_double()
        import pdb; pdb.set_trace()

        self.update_location(rotation, movement)

        # If we have reached destination, reset visual flags for visited
        if rotation == 'Reset' and movement == 'Reset':
            self.reset_values()

        return rotation, movement

    def get_walls_for_current_location(self, x, y, sensors):

        # If it had been visited before, just get those values
        if self.terrain.grid[x][y].visited != '':
            walls = self.terrain.grid[x][y].get_total_walls()

        # Else, get current walls. Note that it can only have real walls,
        # Since the location has never been visited, and imaginary walls
        # Are the result of dead ends that force the robot to the prev location
        else:
            # Placeholder
            walls = [0, 0, 0, 0]

            # Store heading
            heading = self.robot_pos['heading']

            # If Change sensor info to wall info
            walls_sensors = [1 if x == 0 else 0 for x in sensors]

            # Map walls to correct x and y coordinates
            for i in range(len(walls_sensors)):
                dir_sensor = dir_sensors[heading][i]
                index = wall_index[dir_sensor]
                walls[index] = walls_sensors[i]

            # Update missing wall index (the cell right behind the robot)
            index = wall_index[dir_reverse[heading]]
            walls[index] = 0

            # # Include imaginary walls in walls
            # imaginary_walls = self.terrain.grid[x][y].imaginary_walls
            # for i in range(len(walls)):
            #     if walls[i] == 1 or imaginary_walls[i] == 1:
            #         walls[i] = 1

        return walls

    def update_location(self, rotation, movement):

        # Perform rotation
        if rotation == -90:
            self.robot_pos['heading'] = \
                dir_sensors[self.robot_pos['heading']][0]
        elif rotation == 90:
            self.robot_pos['heading'] = \
                dir_sensors[self.robot_pos['heading']][2]
        elif rotation == 0:
            pass
        else:
            print "Invalid rotation value, no rotation performed."

        # Advance
        if movement == 1:
            self.robot_pos['location'][0] += \
                dir_move[self.robot_pos['heading']][0]
            self.robot_pos['location'][1] += \
                dir_move[self.robot_pos['heading']][1]
        elif movement == -1:
            self.robot_pos['location'][0] -= \
                dir_move[self.robot_pos['heading']][0]
            self.robot_pos['location'][1] -= \
                dir_move[self.robot_pos['heading']][1]

        # If we have reached the destination reset location and heading
        if self.reached_destination:
            self.reset_values()

    def number_of_walls(self, sensors):
        number_of_walls  = 0
        for sensor in sensors:
            if sensor == 0:
                number_of_walls += 1
        return number_of_walls

    def get_next_move(self, x, y, heading, sensors):

        # If we reach a dead end:
        if sensors == [0, 0, 0] or (self.number_of_walls(sensors) == 2 and self.last_movement == -1):

            # 1) Move back one step
            rotation = 0
            movement = -1

            # 2) Get reference to cell
            cell = self.terrain.grid[x][y]

            # 3) Place imaginary wall behind the robot before exiting location
            reverse_direction = dir_reverse[heading]
            index = self.terrain.get_index_of_wall(reverse_direction)
            cell.imaginary_walls[index] = 1

            # 4) Change the value of visited to signify dead end
            cell.visited = 'x'

            # 5) Update imaginary walls and distances
            self.terrain.update_imaginary_walls(x, y, cell.imaginary_walls)

        else:

            # 1) Get adjacent distances from sensors
            adj_distances, adj_visited = self.terrain.get_adjacent_distances(x, y, heading, self.last_movement, sensors)

            # 2) Get the minimum distance and index of that distance
            min_distance = min(adj_distances)
            min_indexes = [i for i, x in enumerate(adj_distances) if x == min_distance]

            # If it's the first round, prefer unexplored cells
            # Get the first unvisited index, or the first if all are visited
            min_index = min_indexes[0]
            if self.round == 1:
                for i in range(len(min_indexes)):
                    if adj_visited[i] is '':
                        min_index = min_indexes[i]
                        break
            # If it's the second round, prefer explored cells
            else:
                for i in range(len(min_indexes)):
                    if adj_visited[i] is not '':
                        min_index = min_indexes[i]
                        break

            # 3) Use that information to make a decision
            # Move Left
            if min_index == 0:
                rotation = -90
                movement = 1
            # Move Up
            elif min_index == 1:
                rotation = 0
                movement = 1
            # Move Right
            elif min_index == 2:
                rotation = 90
                movement = 1
            # Minimum distance is behind, so just rotate clockwise
            else:
                rotation = 90
                movement = 0

        self.store_last_movement(movement)

        return rotation, movement

    def store_last_movement(self, movement):
        """
        Take note if the last step was only a rotation
        """
        self.last_movement = movement
        self.total_moves += 1


