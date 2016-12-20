import numpy as np

# global dictionaries for robot movement and sensing
dir_sensors = {'u': ['l', 'u', 'r'], 'r': ['u', 'r', 'd'],
               'd': ['r', 'd', 'l'], 'l': ['d', 'l', 'u'],
               'up': ['l', 'u', 'r'], 'right': ['u', 'r', 'd'],
               'down': ['r', 'd', 'l'], 'left': ['d', 'l', 'u']}
dir_move = {'u': [0, 1], 'r': [1, 0], 'd': [0, -1], 'l': [-1, 0],
            'up': [0, 1], 'right': [1, 0], 'down': [0, -1], 'left': [-1, 0]}
dir_reverse = {'u': 'd', 'r': 'l', 'd': 'u', 'l': 'r',
               'up': 'd', 'right': 'l', 'down`': 'u', 'left': 'r'}


class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''

        self.location = [0, 0]
        self.heading = 'up'
        self.maze_dim = maze_dim
        self.maze_distances = np.empty([maze_dim, maze_dim], dtype=int)
        self.robot_pos = {'location': [0, 0], 'heading': 'up'}
        self.prev_states = []
        self.visited_cells = np.zeros([maze_dim, maze_dim], dtype=int)

        self.fill_maze()
        self.print_maze()

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

        rotation = 0
        movement = 0

        adj_distances = self.get_adjacent_distances(sensors)
        min_distance = min(adj_distances)
        min_index = adj_distances.index(min_distance)

        # Left
        if min_index == 0:
            rotation = -90
            movement = 1
        # Up
        elif min_index == 1:
            rotation = 0
            movement = 1
        # Right
        elif min_index == 2:
            rotation = 90
            movement = 1


        # TODO: delete this line
        import pdb; pdb.set_trace()

        # Check if there was any change
        if movement != 0:

            print('MIN INDEX: {}'.format(min_index))

            print('------------')
            print('before... MOVING {}'.format(self.robot_pos['heading']))
            print(sensors)
            print(self.robot_pos)

            self.mark_cell_as_visited()
            self.store_prev_state(sensors)
            self.perform_movement(rotation)

            print('after... MOVING {}'.format(self.robot_pos['heading']))
            print(self.robot_pos)
            print('------------')


        #
        # # check right
        # if sensors[2] is not 0:
        #
        #     rotation = 90
        #     movement = 1
        #
        #     print('------------')
        #     print('before... MOVING RIGHT')
        #     print(sensors)
        #     print(self.robot_pos)
        #
        #     self.store_prev_state(sensors)
        #     self.perform_movement(rotation)
        #
        #     print('after... MOVING RIGHT')
        #     print(self.robot_pos)
        #     print('------------')
        #
        # # move up
        # elif sensors[1] is not 0:
        #
        #     rotation = 0
        #     movement = 1
        #
        #     print('------------')
        #     print('before... MOVING UP')
        #     print(sensors)
        #     print(self.robot_pos)
        #
        #     self.store_prev_state(sensors)
        #     self.perform_movement(rotation)
        #
        #     print('after... MOVING UP')
        #     print(self.robot_pos)
        #     print('------------')
        #
        # # move left
        # elif sensors[0] is not 0:
        #
        #     rotation = -90
        #     movement = 1
        #
        #     print('------------')
        #     print('before... MOVING LEFT')
        #     print(sensors)
        #     print(self.robot_pos)
        #
        #     self.store_prev_state(sensors)
        #     self.perform_movement(rotation)
        #
        #     print('after... MOVING LEFT')
        #     print(sensors)
        #     print(self.robot_pos)
        #     print('------------')
        #
        # # dead end
        # else:
        #     pass

        return rotation, movement

    def fill_maze(self):

        center = self.maze_dim / 2
        max_distance = self.maze_dim - 2

        # Fill top left half
        for i in range(0, center):
            for j in range(center):
                self.maze_distances[i][j] = max_distance - j - i

        # The two rows in the center should be equal
        for i in range(center, center + 1):
            for j in range(0, center):
                self.maze_distances[i][j] = self.maze_distances[i - 1][j]

        # Fill bottom left half
        for i in range(center + 1, self.maze_dim):
            for j in range(0, center):
                self.maze_distances[i][j] = self.maze_distances[i - 1][j] + 1

        # The two rows in the center should have the same values
        for i in range(0, self.maze_dim):
            for j in range(center, center + 1):
                self.maze_distances[i][j] = self.maze_distances[i][j - 1]

        # Fill remaining columns
        for i in range(0, self.maze_dim):
            for j in range(center + 1, self.maze_dim):
                self.maze_distances[i][j] = self.maze_distances[i][j - 1] + 1

    def print_maze(self):
        print(self.maze_distances)

    def store_prev_state(self, sensors):

        # Create stack of prev positions
        x = self.robot_pos['location'][0]
        y = self.robot_pos['location'][1]
        location = [x, y]
        heading = self.robot_pos['heading']
        curr_dist = self.maze_distances[self.robot_pos[
            'location'][0]][self.robot_pos['location'][1]]
        adj_dist = self.get_adjacent_distances(sensors)

        robot_state = [location, heading, sensors, curr_dist, adj_dist]
        self.prev_states.append(robot_state)
        print (self.prev_states)

    def perform_movement(self, angle):

        # Perform rotation
        if angle == -90:
            self.robot_pos['heading'] = \
                dir_sensors[self.robot_pos['heading']][0]
        elif angle == 90:
            self.robot_pos['heading'] = \
                dir_sensors[self.robot_pos['heading']][2]
        elif angle == 0:
            pass
        else:
            print "Invalid rotation value, no rotation performed."

        # Advance
        print('*** DISTANCE FOR THIS LOCATION ***')
        print(self.maze_distances[self.robot_pos[
            'location'][0]][self.robot_pos['location'][1]])

        self.robot_pos['location'][0] += \
            dir_move[self.robot_pos['heading']][0]
        self.robot_pos['location'][1] += \
            dir_move[self.robot_pos['heading']][1]

    def get_adjacent_distances(self, sensors):

        distances = [10000, 10000, 10000]

        curr_loc_x = self.robot_pos['location'][0]
        curr_loc_y = self.robot_pos['location'][1]

        # Left, simulate rotation of -90
        if sensors[0] is not 0:
            heading = dir_sensors[self.robot_pos['heading']][0]
            new_loc_x = curr_loc_x + dir_move[heading][0]
            new_loc_y = curr_loc_y + dir_move[heading][1]
            distances[0] = self.maze_distances[new_loc_x][new_loc_y]

        # Up, no rotation
        if sensors[1] is not 0:
            heading = self.robot_pos['heading']
            new_loc_x = curr_loc_x + dir_move[heading][0]
            new_loc_y = curr_loc_y + dir_move[heading][1]
            distances[1] = self.maze_distances[new_loc_x][new_loc_y]

        # Right, simulate rotation of 90
        if sensors[2] is not 0:
            heading = dir_sensors[self.robot_pos['heading']][2]
            new_loc_x = curr_loc_x + dir_move[heading][0]
            new_loc_y = curr_loc_y + dir_move[heading][1]
            distances[2] = self.maze_distances[new_loc_x][new_loc_y]

        return distances



    def mark_cell_as_visited(self):
        # Change axes order to get correct visual representation
        y = self.robot_pos['location'][0]
        # Modify x axis to get correct visual representation
        x = self.maze_dim - self.robot_pos['location'][1] - 1
        self.visited_cells[x][y] += 1
        print(self.visited_cells)
