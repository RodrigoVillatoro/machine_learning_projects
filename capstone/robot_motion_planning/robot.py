from global_variables import (dir_move, dir_reverse, dir_sensors, wall_index,
                              WALL_VALUE)
from terrain import Terrain


class Robot(object):
    def __init__(self, maze_dim):
        '''
        Used to set up attributes that the robot will use to learn and
        navigate the maze.
        '''

        # Position-related attributes
        self.robot_pos = {'location': [0, 0], 'heading': 'up'}  # Current pos
        self.last_movement = 0  # 1 forward, -1 reverse, 0 if it only rotated

        # Goal-related attributes
        center = maze_dim/2
        self.center_locations = [
            [center, center], [center - 1, center],
            [center, center - 1], [center - 1, center - 1]]
        self.reached_destination = False

        # For exploring state
        self.exploring = False
        self.number_of_steps_exploring = 0

        # Initialize terrain
        self.terrain = Terrain(maze_dim)

    def reset_values(self):
        self.robot_pos = {'location': [0, 0], 'heading': 'up'}
        self.last_movement = 0

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
            if self.reached_destination and self.exploring:
                rotation, movement = self.explore(x, y, heading, sensors)
            else:
                rotation, movement = self.get_next_move(x, y, heading, sensors)

        self.update_location(rotation, movement)

        # If we have reached destination, reset values
        if rotation == 'Reset' and movement == 'Reset':
            self.reset_values()

        return rotation, movement

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
        adj_distances, adj_visited = self.terrain.get_adjacent_distances(x, y, heading, sensors, False)
        return sensors == [0, 0, 0] or adj_distances == [WALL_VALUE, WALL_VALUE, WALL_VALUE, WALL_VALUE]

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

    def update_location(self, rotation, movement):

        # Perform rotation
        if rotation == -90:
            self.robot_pos['heading'] = \
                dir_sensors[self.robot_pos['heading']][0]
        elif rotation == 90:
            self.robot_pos['heading'] = \
                dir_sensors[self.robot_pos['heading']][2]

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

    def number_of_walls(self, sensors):
        number_of_walls = 0
        for sensor in sensors:
            if sensor == 0:
                number_of_walls += 1
        return number_of_walls

    def get_next_move(self, x, y, heading, sensors):

        if self.is_at_starting_position(x, y):
            rotation = 0
            movement = 1

        # If we reach a dead end:
        elif self.is_at_a_dead_end(sensors):

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

        else:

            # 1) Get adjacent distances from sensors
            adj_distances, adj_visited = self.terrain.get_adjacent_distances(x, y, heading, sensors)

            # Get min index (guaranteed to not be a wall)
            min_index = adj_distances.index(min(adj_distances))

            # If we have reached the destination, follow only visited
            valid_distances = []
            if self.reached_destination:
                for i, dist in enumerate(adj_distances[0:3]):
                    if dist != WALL_VALUE and adj_visited[i] is '*' or adj_visited[i] is 'e':
                        valid_distances.append(dist)
            # If it's the first round, prefer cells that have not been visited
            else:
                for i, dist in enumerate(adj_distances):
                    if dist != WALL_VALUE and adj_visited[i] is '':
                        valid_distances.append(dist)

            if valid_distances:
                min_index = adj_distances.index(min(valid_distances))

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

    def explore(self, x, y, heading, sensors):

        if self.should_end_exploring(x, y):
            rotation = 'Reset'
            movement = 'Reset'
            self.exploring = False
            self.terrain.set_imaginary_walls_for_unvisited_cells()
            self.terrain.update_distances_last_time()

            self.terrain.draw()
            explored = self.terrain.get_percentage_of_maze_explored()
            print(explored)

        else:

            # If we reach a dead end:
            if self.is_at_a_dead_end(sensors):

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

            else:

                # 1) Get adjacent distances from sensors
                adj_distances, adj_visited = self.terrain.get_adjacent_distances(x, y, heading, sensors)

                # Convert wall values to -1 (robot will follow max distance, can't be wall)
                adj_distances = [-1 if dist == WALL_VALUE else dist for dist in adj_distances]

                # Get max index (guaranteed to not be a wall)
                valid_distance = max(adj_distances)
                # valid_index = adj_distances.index(valid_distance)
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

                # 3) Use that information to make a decision
                # Move Left
                if valid_index == 0:
                    rotation = -90
                    movement = 1
                # Move Up
                elif valid_index == 1:
                    rotation = 0
                    movement = 1
                # Move Right
                elif valid_index == 2:
                    rotation = 90
                    movement = 1
                # Minimum distance is behind, so just rotate clockwise
                else:
                    rotation = 90
                    movement = 0

            self.store_last_movement(movement)
            self.number_of_steps_exploring += 1

        return rotation, movement

    def store_last_movement(self, movement):
        self.last_movement = movement

    def should_end_exploring(self, x, y):

        # Check for % of cells covered
        if self.terrain.get_percentage_of_maze_explored() > 90:
            return True

        # Check for number of steps
        if self.number_of_steps_exploring > 30:
            return True

        # Check for center of the maze:
        if self.is_at_center_of_the_maze(x, y):
            return True

        if self.is_at_starting_position(x, y):
            return True

        return False

    def get_optimal_number_of_moves(self, x, y, heading, sensors):

        # 1) Get adjacent distances from sensors
        adj_distances, adj_visited = self.terrain.get_adjacent_distances(x, y, heading, sensors)

        # Get min index (guaranteed to not be a wall)
        min_index = adj_distances.index(min(adj_distances))

        # If we have reached the destination, follow only visited
        valid_distances = []
        if self.reached_destination:
            for i, dist in enumerate(adj_distances[0:3]):
                if dist != WALL_VALUE and adj_visited[i] is '*' or adj_visited[i] is 'e':
                    valid_distances.append(dist)
        # If it's the first round, prefer cells that have not been visited
        else:
            for i, dist in enumerate(adj_distances):
                if dist != WALL_VALUE and adj_visited[i] is '':
                    valid_distances.append(dist)

        if valid_distances:
            min_index = adj_distances.index(min(valid_distances))

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



