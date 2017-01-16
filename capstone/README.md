# Project 5: Robot Motion Planning Capstone Project
### Plot and Navigate a Virtual Maze

The following is the capstone project for Udacity's Machine Learning Engineering Nanodegree.  

#### Project Overview

This project takes inspiration from Micromouse competitions, where a robot starts at the lower left corner of a maze and is tasked with a) finding the center of the maze, and b) reaching the center in the fastest possible way. Instead of a physical maze and a physical robot, this project implements a virtual maze and a virtual robot.

#### Problem Statement

Given a maze of n x n dimensions —where n is an even number between 12 and 16— and starting coordinates of (0, 0) —the lower left corner—, a robot is tasked with two objectives: 

ROUND 1: The robot can navigate the maze to determine the most efficient path to the center. The robot has to reach the center of the maze in order to be able to start the second round, but can alternatively continue to explore the maze after finding the goal.

ROUND 2:  The robot attempts to reach the center of the maze in the fastest possible way. In the case of this project, that means reaching the center in the minimum number of steps.

In total, the robot hast a maximum of 1000 time steps to complete both rounds. 

#### Metrics

The score of an implementation is calculated by adding the number of steps required to complete the second round, plus 1/30 times the number of steps taken during the first round. In other words, the lowest the score, the better. The worst possible outcome: exceeding the 1000 time steps given to complete both rounds.

### Implementation

The implementation consists of four different classes: cell, terrain, robot, algorithms. 

* Cell: represents a square (location) in the maze.
* Terrain: representation of the maze from the robot’s point of view.
* Algorithms: has the logic that enables the robot to decide how to move. 
* Robot: responsible for the agent moving around the maze.

## How to run the code:

A script called tester.py has been provided to test the mazes and the algorithms. We can run the script by writing the following command in the console: 

```
python tester.py test_maze.01 ff false
```

The third argument is the maze we want to test, the fourth argument is the algorithm we want to use, and the fifth argument states if the robot should explore more cells after reaching the center. 

These are the options for each argument:

* (arg # 3): test_maze_01.txt, test_maze_02.txt, test_maze_03.txt, test_maze_04.txt
* (arg # 4): ff = Flood-Fill, ar = Always-Right, mr = Modified-Right
* (arg # 5): true, false


#### Requirements

Python 2.7.X

Numpy
