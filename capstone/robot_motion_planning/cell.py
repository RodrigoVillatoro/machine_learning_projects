from global_variables import WALL_VALUE


class Cell:

    def __init__(self, real_walls=None, distance=0, visited=''):
        """
        Represents a particular cell in the maze
        :param real_walls: array of 0's (no walls) and 1's (walls) [l, u, r, d]
        :param distance: distance from that cell to the center of the maze
        :param visited: str; directions = < ^ > V; x = dead end, * = visited
        """
        if real_walls is None:
            real_walls = [0, 0, 0, 0]

        self.real_walls = real_walls  # Actual walls on the maze
        self.imaginary_walls = [0, 0, 0, 0]  # Walls added to avoid dead ends
        self.distance = distance  # Distance to the center of the maze
        self.visited = visited  # Used to know if robot has visited the cell

    def get_total_walls(self):
        """
        Get real and imaginary walls for a particular cell
        :return: array of 0s and 1s with real and imaginary walls
        """
        total_walls = [0, 0, 0, 0]
        for i in range(len(self.real_walls)):
            if self.real_walls[i] == 1 or self.imaginary_walls[i] == 1:
                total_walls[i] = 1
        return total_walls

    def top(self, double=False):
        """
        Gets the info for the top of the cell (wall or not wall).
        Used to print the maze or represent individual cells.
        :param double: only True if we want to print individual cell. Not used
         to print the whole maze since adjacent cells share walls
        :return: str with the first line that will visually represent a cell
        """
        cell = '+'
        if self.real_walls[1]:
            cell += ' --- '
        elif self.imaginary_walls[1]:
            cell += ' ... '
        else:
            cell += '     '
        if double:
            cell += '+'

        return cell

    def middle(self, double=False):
        """
        Gets info for the center of the cell (wall, distance, visited).
        Used to print the maze or represent individual cells.
        :param double: only True if we want to print individual cell. Not used
         to print the whole maze since adjacent cells share walls
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
        if double:
            if self.real_walls[2]:
                cell += '|'
            elif self.imaginary_walls[2]:
                cell += ':'
            else:
                cell += ' '

        return cell

    def bottom(self, double=False):
        """
        Get info for the bottom of the cell (wall or not wall).
        Used to print the maze or represent individual cells.
        :param double: only True if we want to print individual cell. Not used
         to print the whole maze since adjacent cells share walls
        :return: str with the third line that will visually represent a cell
        """
        cell = '+'
        if self.real_walls[3]:
            cell += ' --- '
        elif self.imaginary_walls[3]:
            cell += ' ... '
        else:
            cell += '     '
        if double:
            cell += '+'

        return cell

    def __str__(self):
        """
        Used to represent an individual cell with all of it's walls.
        Not used to print the maze, mostly for debug.
        """
        cell = '\n'
        cell += self.top(double=True)
        cell += '\n'
        cell += self.middle(double=True)
        cell += '\n'
        cell += self.bottom(double=True)
        cell += '\n'
        return cell
