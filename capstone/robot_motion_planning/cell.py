from global_variables import WALL_VALUE


class Cell:

    def __init__(self, real_walls=None, distance=0, visited=''):
        """
        Simplified representation of the maze for debugging purposes
        :param walls: array of 0's (no walls) and 1's (walls) [l, u, r, d]
        :param distance: distance to the center of the maze
        :param visited: directions = < ^ > V; x = dead end, * = visited
        """
        if real_walls is None:
            real_walls = [0, 0, 0, 0]

        self.real_walls = real_walls  # Actual walls on the maze
        self.imaginary_walls = [0, 0, 0, 0]  # Walls added by the program
        self.distance = distance
        self.visited = visited

    def get_total_walls(self):
        """
        Include imaginary walls in walls
        :return: total walls... real and imaginary
        """
        total_walls = [0, 0, 0, 0]
        for i in range(len(self.real_walls)):
            if self.real_walls[i] == 1 or self.imaginary_walls[i] == 1:
                total_walls[i] = 1
        return total_walls

    def top(self):
        """
        Returns the formatted info of the top of the cell (wall or not wall).
        Used to print the maze.
        :return: str with the first line that will visually represent a cell
        """
        cell = '+'
        if self.real_walls[1]:
            cell += ' --- '
        elif self.imaginary_walls[1]:
            cell += ' ... '
        else:
            cell += '     '

        return cell

    def middle(self):
        """
        Returns the formatted info of the center of the cell (wall, distance,
        visited). Used to print the maze.
        :return: str with the second line that will visually represent a cell
        """
        if self.distance == WALL_VALUE:
            distance = str(-1)
        else:
            distance = str(self.distance)
        cell = ''
        if self.real_walls[0]:
            cell += '|'
        elif self.imaginary_walls[0]:
            cell += ':'
        else:
            cell += ' '
        cell += ' '
        if len(distance) == 1:
            cell += ' '
        cell += distance
        if len(self.visited) == 0:
            cell += ' '
        cell += self.visited
        cell += ' '

        return cell

    def bottom(self):
        """
        Returns the formatted info of the bottom of the cell (wall or not
        wall). Used to print the maze.
        :return: str with the third line that will visually represent a cell
        """
        cell = '+'
        if self.real_walls[3]:
            cell += ' --- '
        elif self.imaginary_walls[3]:
            cell += ' ... '
        else:
            cell += '     '

        return cell

    def top_double(self):
        """
        Returns the formatted info of the top of the cell (wall or not wall).
        Used to print the maze.
        :return: str with the first line that will visually represent a cell
        """
        cell = '+'
        if self.real_walls[1]:
            cell += ' --- '
        elif self.imaginary_walls[1]:
            cell += ' ... '
        else:
            cell += '     '
        cell += '+'

        return cell

    def middle_double(self):
        """
        Returns the formatted info of the center of the cell (wall, distance,
        visited). Used to print the maze.
        :return: str with the second line that will visually represent a cell
        """
        distance = str(self.distance)
        cell = ''
        if self.real_walls[0]:
            cell += '|'
        elif self.imaginary_walls[0]:
            cell += ':'
        else:
            cell += ' '
        cell += ' '
        if len(distance) == 1:
            cell += ' '
        cell += distance
        if len(self.visited) == 0:
            cell += ' '
        cell += self.visited
        cell += ' '
        if self.real_walls[2]:
            cell += '|'
        elif self.imaginary_walls[2]:
            cell += ':'
        else:
            cell += ' '

        return cell

    def bottom_double(self):
        """
        Returns the formatted info of the bottom of the cell (wall or not
        wall). Used to print the maze.
        :return: str with the third line that will visually represent a cell
        """
        cell = '+'
        if self.real_walls[3]:
            cell += ' --- '
        elif self.imaginary_walls[3]:
            cell += ' ... '
        else:
            cell += '     '
        cell += '+'

        return cell

    def __str__(self):
        """
        Returns an individual cell, not used in the print_maze function.
        """
        cell = '\n'
        cell += self.top_double()
        cell += '\n'
        cell += self.middle_double()
        cell += '\n'
        cell += self.bottom_double()
        cell += '\n'
        return cell
