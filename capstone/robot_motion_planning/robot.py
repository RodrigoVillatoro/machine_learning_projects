import numpy as np

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
inc_location = {}

# Stack where we push cells that need to be checked for updating
# cells_stack = []

# Distance placeholder for walls
WALL_VALUE = 10000


class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''
        self.total_moves = 0  # Store total number of moves made by the robot
        self.reached_destination = False  # Did the robot reach the center?
        self.prev_location = None  # Store previous cell
        self.robot_pos = {'location': [0, 0], 'heading': 'up'}  # Current pos
        self.last_movement = 0  # 1 if robot advanced, 0 if it only rotated

        self.terrain = Terrain(maze_dim)
        self.terrain.draw()

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
            walls = [1, 0, 1, 1]
            self.store_last_movement(movement)
            self.total_moves += 1

            # Update terrain
            self.terrain.update(x, y, walls, heading)

        # If not, first update distances, then get next move
        else:

            # 1) Push current location to stack
            self.terrain.cells_to_check.append(location)

            # 2) Add newly discovered walls
            walls = self.get_walls_for_current_location(x, y, sensors)

            # 3) Update terrain and distances
            self.terrain.update(x, y, walls, heading)

            # 4) Get next move
            rotation, movement = self.get_next_move(sensors)

        self.terrain.draw()

        self.update_location(rotation, movement)

        return rotation, movement

    def get_walls_for_current_location(self, x, y, sensors):

        # If it had been visited before, just return the values
        if self.terrain.grid[x][y].direction != '':
            return self.terrain.grid[x][y].walls

        # Else, take note of the walls
        # Placeholder
        walls = [0, 0, 0, 0]

        # Store location values and heading
        heading = self.robot_pos['heading']

        # Change sensor info to wall info
        walls_sensors = [1 if x == 0 else 0 for x in sensors]

        # Map walls to correct x and y coordinates
        for i in range(len(walls_sensors)):
            dir_sensor = dir_sensors[heading][i]
            index = wall_index[dir_sensor]
            walls[index] = walls_sensors[i]

        # Update missing wall index (the cell right behind the robot)
        index = wall_index[dir_reverse[heading]]
        walls[index] = 0

        return walls

    def update_location(self, rotation, movement):

        # Update previous location
        self.prev_location = self.robot_pos['location']

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
        if movement != 0:
            self.robot_pos['location'][0] += \
                dir_move[self.robot_pos['heading']][0]
            self.robot_pos['location'][1] += \
                dir_move[self.robot_pos['heading']][1]

    def get_next_move(self, sensors):

        # 1) Get adjacent distances from sensors
        adj_distances = self.get_adjacent_distances(sensors)

        # 2) Get the minimum distance and index of that distance
        min_distance = min(adj_distances)
        min_index = adj_distances.index(min_distance)

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
        self.total_moves += 1

        return rotation, movement

    def store_last_movement(self, movement):
        """
        Take note if the last step was only a rotation
        """
        self.last_movement = movement

    def get_adjacent_distances(self, sensors):

        # Placeholder (robot's coordinates)
        distances = [WALL_VALUE, WALL_VALUE, WALL_VALUE, WALL_VALUE]

        # Store location values and heading
        x = self.robot_pos['location'][0]
        y = self.robot_pos['location'][1]
        heading = self.robot_pos['heading']

        for i in range(len(sensors)):
            if sensors[i] != 0:
                dir_sensor = dir_sensors[heading][i]
                distances[i] = self.terrain.get_distance(x, y, dir_sensor)

        # Update missing distance (cell right behind the robot)
        # This is only valid if the last step was not just a rotation
        if self.last_movement != 0:
            behind = dir_reverse[heading]
            distances[3] = self.terrain.get_distance(x, y, behind)

        return distances
