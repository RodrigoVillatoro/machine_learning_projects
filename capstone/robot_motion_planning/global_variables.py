
# Global dictionaries for robot movement and sensing
dir_sensors = {'u': ['l', 'u', 'r'], 'r': ['u', 'r', 'd'],
               'd': ['r', 'd', 'l'], 'l': ['d', 'l', 'u'],
               'up': ['l', 'u', 'r'], 'right': ['u', 'r', 'd'],
               'down': ['r', 'd', 'l'], 'left': ['d', 'l', 'u']}

dir_move = {'u': [0, 1], 'r': [1, 0], 'd': [0, -1], 'l': [-1, 0],
            'up': [0, 1], 'right': [1, 0], 'down': [0, -1], 'left': [-1, 0]}

dir_reverse = {'u': 'd', 'r': 'l', 'd': 'u', 'l': 'r',
               'up': 'd', 'right': 'l', 'down': 'u', 'left': 'r'}

# Directions for visual representation (drawing maze)
robot_directions = {'u': '^', 'r': '>', 'd': 'V', 'l': '<',
                    'up': '^', 'right': '>', 'down': 'V', 'left': '<'}

# Wall-related
opposite_wall = {'0': 2, '1': 3, '2': 0, '3': 1}

wall_index = {'l': 0, 'u': 1, 'r': 2, 'd': 3,
               'left': 0, 'up': 1, 'right': 2, 'down': 3}

# Distance placeholder for walls
WALL_VALUE = 10000
