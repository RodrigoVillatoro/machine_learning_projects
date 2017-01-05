class Cell:

    def __init__(self, walls=None, distance=0, visited=''):
        """
        Simplified representation of the maze for debugging purposes
        :param walls: array of 0's (no walls) and 1's (walls) [l, u, r, d]
        :param distance: distance to the center of the maze
        :param visited: values, < ^ > V. blank if not visited, * otherwise.
        """
        if walls is None:
            walls = [0, 0, 0, 0]

        self.walls = walls
        self.distance = distance
        self.visited = visited

    def top(self):
        """
        Returns the formatted info of the top of the cell (wall or not wall).
        Used to print the maze.
        :return: str with the first line that will visually represent a cell
        """
        cell = '+'
        if self.walls[1]:
            cell += ' --- '
        else:
            cell += '     '
        cell += '+'

        return cell

    def middle(self):
        """
        Returns the formatted info of the center of the cell (wall, distance,
        visited). Used to print the maze.
        :return: str with the second line that will visually represent a cell
        """
        distance = str(self.distance)
        cell = ''
        if self.walls[0]:
            cell += '|'
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
        if self.walls[2]:
            cell += '|'
        else:
            cell += ' '

        return cell

    def bottom(self):
        """
        Returns the formatted info of the bottom of the cell (wall or not
        wall). Used to print the maze.
        :return: str with the third line that will visually represent a cell
        """
        cell = '+'
        if self.walls[3]:
            cell += ' --- '
        else:
            cell += '     '
        cell += '+'

        return cell

    def draw_cell(self):
        """
        Draws an individual cell, not used in the print_maze function.
        """
        cell = ''
        cell += self.top()
        cell += '\n'
        cell += self.middle()
        cell += '\n'
        cell += self.bottom()
        print(cell)
