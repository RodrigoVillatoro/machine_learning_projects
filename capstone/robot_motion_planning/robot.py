import sys

from global_variables import (dir_move, dir_reverse, dir_sensors, rotations,
                              wall_index, MAX_DISTANCES, WALL_VALUE)
from terrain import Terrain


class Robot(object):
    def __init__(self, maze_dim):
        '''
        Used to set up attributes that the robot will use to learn and
        navigate the maze.
        '''

        # Position-related attributes
        self.robot_pos = {'location': [0, 0], 'heading': 'up'}  # Current pos
        self.steps_first_round = 0
        self.steps_final_round = 0
        self.maze_dim = maze_dim

        # Goal-related attributes
        center = maze_dim/2
        self.center_locations = [
            [center, center], [center - 1, center],
            [center, center - 1], [center - 1, center - 1]]
        self.reached_destination = False

        # For exploring state
        self.exploring = False
        self.steps_exploring = 0

        # Initialize terrain
        self.terrain = Terrain(maze_dim)

        # Algorithm to use:
        if str(sys.argv[2]).lower() == 'ff':
            self.algorithm = 'flood-fill'
        elif str(sys.argv[2]).lower() == 'ar':
            self.algorithm = 'always-right'
        elif str(sys.argv[2]).lower() == 'mr':
            self.algorithm = 'modified-right'

        # Explore after reaching center of the maze:
        if str(sys.argv[3]).lower() == 'true':
            self.explore_after_center = True
        elif str(sys.argv[3]).lower() == 'false':
            self.explore_after_center = False

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

        # Store current location and direction
        x, y, heading = self.get_current_position()

        # Get walls for current location
        walls = self.get_walls_for_current_location(x, y, heading, sensors)

        # If we have reached the center of the maze
        if self.is_at_center_of_the_maze(x, y):

            # Move backwards
            rotation = 0
            movement = -1

            # Update terrain (visual representation)
            self.terrain.update(x, y, heading, walls, self.exploring)

            # State that we have reached destination
            self.reached_destination = True

            # Set flags to exploring
            self.exploring = True

        # Else, first update distances, then get next move
        else:

            # 1) Push current location to stack
            self.terrain.cells_to_check.append([x, y])

            # 2) Add current cell to stack of visited destinations
            if [x, y] not in self.terrain.visited_before_reaching_destination:
                self.terrain.visited_before_reaching_destination.append([x, y])

            # 4) Update terrain and distances
            self.terrain.update(x, y, heading, walls, self.exploring)

            # 4) Get next move
            rotation, movement = self.get_next_move(x, y, heading, sensors)

        self.update_location(rotation, movement)

        # If we have reached destination, reset values
        if rotation == 'Reset' and movement == 'Reset':
            self.reset_values()

        # If we are about to hit the goal in the second round
        if self.robot_pos['location'] in self.center_locations \
                and self.steps_final_round != 0:
            self.report_results()

        return rotation, movement

    def reset_values(self):
        self.robot_pos = {'location': [0, 0], 'heading': 'up'}

    def get_current_position(self):
        heading = self.robot_pos['heading']
        location = self.robot_pos['location']
        x = location[0]
        y = location[1]
        return x, y, heading

    def is_at_starting_position(self, x, y):
        return x == 0 and y == 0

    def is_at_center_of_the_maze(self, x, y):
        return [x, y] in self.center_locations

    def is_at_a_dead_end(self, sensors):
        x, y, heading = self.get_current_position()
        adj_distances, adj_visited = \
            self.terrain.get_adj_info(x, y, heading, sensors, False)
        return sensors == [0, 0, 0] or adj_distances == list(MAX_DISTANCES)

    def get_walls_for_current_location(self, x, y, heading, sensors):

        if self.is_at_starting_position(x, y):
            walls = [1, 0, 1, 1]

        # If it had been visited before, just get those values
        elif self.terrain.grid[x][y].visited != '':
            walls = self.terrain.grid[x][y].get_total_walls()

        # Else, get current walls. Note that it can only have real walls
        # since the location has never been visited, and imaginary walls
        # are the result of dead ends that force the robot to the prev location
        else:
            # Placeholder
            walls = [0, 0, 0, 0]

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

    def get_new_direction(self, rotation):
        if rotation == -90:
            return dir_sensors[self.robot_pos['heading']][0]
        elif rotation == 90:
            return dir_sensors[self.robot_pos['heading']][2]
        else:
            return self.robot_pos['heading']

    def update_location(self, rotation, movement):

        if movement == 'Reset' or rotation == 'Reset':
            return

        else:
            movement = int(movement)

            # Perform rotation
            if rotation == -90:
                self.robot_pos['heading'] = \
                    dir_sensors[self.robot_pos['heading']][0]
            elif rotation == 90:
                self.robot_pos['heading'] = \
                    dir_sensors[self.robot_pos['heading']][2]

            # Advance
            if movement == -1:
                self.robot_pos['location'][0] -= \
                    dir_move[self.robot_pos['heading']][0]
                self.robot_pos['location'][1] -= \
                    dir_move[self.robot_pos['heading']][1]
            else:
                while movement > 0:
                    self.robot_pos['location'][0] += \
                        dir_move[self.robot_pos['heading']][0]
                    self.robot_pos['location'][1] += \
                        dir_move[self.robot_pos['heading']][1]
                    movement -= 1

    def number_of_walls(self, sensors):
        number_of_walls = 0
        for sensor in sensors:
            if sensor == 0:
                number_of_walls += 1
        return number_of_walls

    def get_next_move(self, x, y, heading, sensors):

        if self.reached_destination and self.exploring:

            # Explore
            rotation, movement = self.explore(x, y, heading, sensors)
            self.steps_exploring += 1

        elif not self.reached_destination and not self.exploring:

            # First round (looking for center of the maze)
            if self.algorithm == 'flood-fill':
                rotation, movement = self.flood_fill(x, y, heading, sensors)
            elif self.algorithm == 'always-right':
                rotation, movement = self.always_right(
                    x, y, heading, sensors)
            elif self.algorithm == 'modified-right':
                rotation, movement = self.modified_right(
                    x, y, heading, sensors)
            else:
                # To Do: Raise Exception
                pass

            self.steps_first_round += 1

        else:
            # Final round (optimized moved)
            rotation, movement = self.final_round(x, y, heading, sensors)
            self.steps_final_round += 1

        return rotation, movement

    def always_right(self, x, y, heading, sensors):

        # 1) Get adjacent distances from sensors
        adj_distances, adj_visited = self.terrain.get_adj_info(
            x, y, heading, sensors)

        if adj_distances[2] != WALL_VALUE:
            valid_index = 2
        elif adj_distances[1] != WALL_VALUE:
            valid_index = 1
        elif adj_distances[0] != WALL_VALUE:
            valid_index = 0
        else:
            valid_index = 3

        rotation, movement = self.convert_from_index(valid_index)

        return rotation, movement

    def modified_right(self, x, y, heading, sensors):

        # 1) Get adjacent distances from sensors
        adj_distances, adj_visited = self.terrain.get_adj_info(
            x, y, heading, sensors)

        if adj_distances[2] != WALL_VALUE and adj_visited[2] != '*':
            valid_index = 2
        elif adj_distances[1] != WALL_VALUE and adj_visited[1] != '*':
            valid_index = 1
        elif adj_distances[0] != WALL_VALUE and adj_visited[0] != '*':
            valid_index = 0
        elif adj_distances[2] != WALL_VALUE:
            valid_index = 2
        elif adj_distances[1] != WALL_VALUE:
            valid_index = 1
        elif adj_distances[0] != WALL_VALUE:
            valid_index = 0
        else:
            valid_index = 3

        rotation, movement = self.convert_from_index(valid_index)

        return rotation, movement

    def right_check_for_dead_ends(self, x, y, heading, sensors):

        if self.is_at_a_dead_end(sensors):
            rotation, movement = self.deal_with_dead_end(x, y, heading)

        else:

            # 1) Get adjacent distances from sensors
            adj_distances, adj_visited = self.terrain.get_adj_info(
                x, y, heading, sensors)

            if adj_distances[2] != WALL_VALUE and adj_visited[2] != '*':
                valid_index = 2
            elif adj_distances[1] != WALL_VALUE and adj_visited[1] != '*':
                valid_index = 1
            elif adj_distances[0] != WALL_VALUE and adj_visited[0] != '*':
                valid_index = 0
            else:
                valid_index = adj_distances.index(min(adj_distances))

            rotation, movement = self.convert_from_index(valid_index)

        return rotation, movement

    def flood_fill(self, x, y, heading, sensors, exploring=False):
        """

        :param x:
        :param y:
        :param heading:
        :param sensors:
        :param exploring:
        :return:
        """

        if self.is_at_starting_position(x, y):
            rotation = 0
            movement = 1

        # If we reach a dead end:
        elif self.is_at_a_dead_end(sensors):
            rotation, movement = self.deal_with_dead_end(x, y, heading)

        else:
            min_index = self.get_valid_index(x, y, heading, sensors, exploring)
            rotation, movement = self.convert_from_index(min_index)

        return rotation, movement

    def get_valid_index(self, x, y, heading, sensors, exploring):

        if not exploring:

            # 1) Get adjacent distances from sensors
            adj_distances, adj_visited = self.terrain.get_adj_info(
                x, y, heading, sensors)

            # Get min index (guaranteed to not be a wall)
            valid_index = adj_distances.index(min(adj_distances))

            # If we have reached the destination, follow only visited
            valid_distances = []
            if self.reached_destination:
                for i, dist in enumerate(adj_distances[0:3]):
                    if dist != WALL_VALUE and adj_visited[i] is '*' or \
                                    adj_visited[i] is 'e':
                        valid_distances.append(dist)
            # If it's the first round, prefer cells that have not been visited
            else:
                for i, dist in enumerate(adj_distances):
                    if dist != WALL_VALUE and adj_visited[i] is '':
                        valid_distances.append(dist)

            if valid_distances:
                valid_index = adj_distances.index(min(valid_distances))

        else:

            # 1) Get adjacent distances from sensors
            adj_distances, adj_visited = self.terrain.get_adj_info(
                x, y, heading, sensors)

            # Convert WALL_VALUES to -1 (robot will follow max distance)
            adj_distances = [-1 if dist == WALL_VALUE else dist for dist in
                             adj_distances]

            # Get max index (guaranteed to not be a wall)
            valid_index = None

            # Prefer cells that have not been visited
            for i, dist in enumerate(adj_distances):
                if dist != -1 and adj_visited[i] is '':
                    valid_index = i
                    break

            if valid_index is None:
                possible_candidate = None
                for i, dist in enumerate(adj_distances):
                    if dist != -1 and adj_visited[i] is '*':
                        if possible_candidate is None:
                            possible_candidate = i
                        else:
                            a = adj_distances[possible_candidate]
                            b = adj_distances[i]
                            if b > a:
                                possible_candidate = i

                valid_index = possible_candidate

            if valid_index is None:
                possible_candidate = None
                for i, dist in enumerate(adj_distances):
                    if dist != -1 and adj_visited[i] is 'e':
                        if possible_candidate is None:
                            possible_candidate = i
                        else:
                            a = adj_distances[possible_candidate]
                            b = adj_distances[i]
                            if b > a:
                                possible_candidate = i

                valid_index = possible_candidate

        return valid_index

    def explore(self, x, y, heading, sensors):

        if self.should_end_exploring(x, y) or not self.explore_after_center:
            rotation = 'Reset'
            movement = 'Reset'
            self.exploring = False
            self.terrain.set_imaginary_walls_for_unvisited_cells()
            self.terrain.update_distances(last_update=True)

        else:

            # If we reach a dead end:
            if self.is_at_a_dead_end(sensors):
                rotation, movement = self.deal_with_dead_end(x, y, heading)

            else:
                valid_index = self.get_valid_index(x, y, heading, sensors, True)
                rotation, movement = self.convert_from_index(valid_index)

        return rotation, movement

    def convert_from_index(self, index):
        # Move Left
        if index == 0:
            rotation = -90
            movement = 1
        # Move Up
        elif index == 1:
            rotation = 0
            movement = 1
        # Move Right
        elif index == 2:
            rotation = 90
            movement = 1
        # Minimum distance is behind, so just rotate clockwise
        else:
            rotation = 90
            movement = 0

        return rotation, movement

    def deal_with_dead_end(self, x, y, heading):
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
        cell.distance = WALL_VALUE

        # 5) Update imaginary walls and distances
        self.terrain.update_imaginary_walls(x, y, cell.imaginary_walls)

        return rotation, movement

    def should_end_exploring(self, x, y):
        """
        The robot should end exploring in all these cases:
        - It has already explored more than 90% of the cells
        - It has already taken 30 steps (in the exploration phase)
        - It has reached the center of the maze (again)
        - It has reached the starting location (again)
        """

        # Check for % of cells covered
        if self.terrain.get_percentage_of_maze_explored() > 90:
            return True

        # Check for number of steps
        if self.steps_exploring > 15:
            return True

        # Check for center of the maze:
        if self.is_at_center_of_the_maze(x, y):
            return True

        if self.is_at_starting_position(x, y):
            return True

        return False

    def final_round(self, x, y, heading, sensors):
        """
        Returns the correct rotation and maximum numbers of steps that
         the robot can take to optimize the score while staying on track
        """

        rotation = None
        movement = None
        current_distance = self.terrain.grid[x][y].distance

        adj_distances, adj_visited = \
            self.terrain.get_adj_info(
                x, y, heading, sensors, False)

        # Change sensor info to max allowed moves, when it applies
        sensors = [3 if step > 3 else step for step in sensors]

        for i, steps in enumerate(sensors):

            # If we found a movement, exit and apply it
            if movement is not None:
                break

            # Otherwise, iterate through steps to see if one matches with the
            # next correct and logical distance for that number of steps
            elif self.is_a_possible_move(adj_distances, adj_visited, i):
                for idx in range(steps):
                    step = steps - idx
                    rotation = rotations[str(i)]
                    new_direction = self.get_new_direction(rotation)
                    furthest_distance = self.terrain.get_distance(
                        x, y, new_direction, step)
                    if furthest_distance == current_distance - step:
                        movement = step
                        break

        return rotation, movement

    def is_a_possible_move(self, adj_distances, adj_visited, i):
        """
        Distances are valid if they are not walls, unvisited, or dead ends.
        """
        return (adj_visited[i] is not ''
                and adj_visited[i] is not 'x'
                and adj_distances[i] is not WALL_VALUE)

    def report_results(self):
        distance = self.terrain.grid[0][0].distance
        percentage = self.terrain.get_percentage_of_maze_explored()
        first_round = self.steps_first_round + self.steps_exploring
        final_round = self.steps_final_round
        print('************ REPORT ************')
        print('ALGORITHM USED: {}'.format(self.algorithm))
        print('EXPLORING AFTER CENTER: {}'.format(self.explore_after_center))
        print('NUMBER OF MOVES FIRST ROUND: {}'.format(first_round))
        print('PERCENTAGE OF MAZE EXPLORED: {}%'.format(percentage))
        print('DISTANCE TO CENTER: {}'.format(distance))
        print('NUMBER OF MOVES FINAL ROUND: {}'.format(final_round))
        print('********************************')
