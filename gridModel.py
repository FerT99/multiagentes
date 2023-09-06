# Commented out IPython magic to ensure Python compatibility.
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

# %matplotlib inline
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import numpy as np
import pandas as pd

import time
import datetime
import random

from sklearn.neighbors import NearestNeighbors

neighbors = NearestNeighbors(metric="euclidean")

GRID = []

with open("grid.txt", "r") as my_file:
    for line in my_file:
        data = line.split()
        GRID.append(data)
my_file.close()

ROW_COUNT = int(GRID[0][0])
COL_COUNT = int(GRID[0][1])
GRID.pop(0)

# U - Unknown
# 0 - Clean
# 1-8 - Dirty
# "S" - Start
# "P" - Papeleria
# "X" - Obstacles

def translateGrid():
    unknown_count = 0
    robot_grid = []
    for i in range(ROW_COUNT):
      temp_list = []
      for y in range(COL_COUNT):
        temp_list.append("U")
      robot_grid.append(temp_list)

    for row in range(ROW_COUNT):
      for col in range(COL_COUNT):
          if GRID[row][col] == "S":
            robot_grid[row][col] = GRID[row][col]
            start = (row, col)
          elif GRID[row][col] == "P":
            robot_grid[row][col] = GRID[row][col]
            papelera = (row, col)
          else:
            unknown_count += 1
    return robot_grid, start, papelera, unknown_count

from os import truncate
class Robot(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.max_capacity = MAX_CAPACITY # trash-holding max capacity (constant)
        self.trash_picked = 0 # n of trash pieces picked and holding
        self.moveFlag = False
        self.goalPos = self.pos #(tuple)


    def step(self):
      self.isDone()

      if self.model.cleanFlag == False:
        self.checkForObstacles()
        self.inTrash()

        if self.goalPos == self.pos:
          self.moveFlag = False
          if self.goalPos in self.model.goalPositions:
            self.model.goalPositions.remove(self.goalPos)
          self.goalPos = self.model.start

        if self.trash_picked == MAX_CAPACITY:
          self.offload()

        elif self.moveFlag == True:
          goal_x, goal_y = self.goalPos
          cell = self.model.knownGrid[goal_x][goal_y]
          if cell == 'X' or cell == '0':
            self.moveFlag = False
            if self.goalPos in self.model.goalPositions:
              self.model.goalPositions.remove(self.goalPos)
            self.goalPos = self.model.start
            self.explore()
          else:
            x, y = self.goalPos
            self.moveTo(x, y)

        else:
          self.explore()

        self.inTrash()
        self.checkForObstacles()


    def explore(self):
      possible_options = self.checkMap()

      while len(possible_options) > 0:
        potential = random.choice(possible_options)
        self.model.goalPositions.append(potential)
        self.moveFlag = True
        self.goalPos = potential
        x, y = self.goalPos
        self.moveTo(x, y)
        break
      if len(possible_options) == 0:
        second_options = self.randomChoice()
        while len(second_options) > 0:
          potential = random.choice(second_options)
          self.model.goalPositions.append(potential)
          self.moveFlag = True
          self.goalPos = potential
          x, y = self.goalPos
          self.moveTo(x, y)
          break

    def offload(self):
      if self.moveFlag == True:
        self.moveFlag = False
        if self.goalPos in self.model.goalPositions:
          self.model.goalPositions.remove(self.goalPos)
        self.goalPos = self.model.start
      if self.pos != self.model.papelera:
        x, y = self.model.papelera
        self.moveTo(x, y)
      else:
        self.trash_picked = 0
        self.getOut()


    def getOut(self):
      neighborhood = self.model.grid.get_neighborhood(self.pos, moore = True, include_center = False)
      for neighbor in neighborhood:
        x, y = neighbor
        cell = self.model.knownGrid[x][y]
        if self.isCellFree(x, y):
          self.model.grid.move_agent(self, neighbor)
          return
      else:
        print("I'M STUCK!! :(")


    def inTrash(self):
      #check if trash
      x, y = self.pos
      if self.model.knownGrid[x][y] == 'U':
        self.model.unknown_count -= 1
        self.model.knownGrid[x][y] = GRID[x][y]
      cell = self.model.knownGrid[x][y]
      if cell != 'P' and cell != 'S' and cell != '0' and self.trash_picked < MAX_CAPACITY:
        self.clean()


    def isCellFree(self, x, y):
      if self.model.grid.out_of_bounds((x,y)) == False:
        if self.model.knownGrid[x][y] != 'X'and self.model.grid.is_cell_empty((x,y)):
          return True
      return False


    def checkMap(self) -> tuple:
      goal_list = [] #list of tuples
      i = 1
      while i <= 8:
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore = True, include_center = False, radius = i)
        for neighbor in neighborhood:
            x, y = neighbor
            cell = self.model.knownGrid[x][y]
            if cell != '0' and cell != 'P' and cell != 'S' and self.isCellFree(x, y):
              goal_list.append(neighbor)

        if len(goal_list) > 0:
          return goal_list

        i += 1

      if len(goal_list) == 0:
        goal_list = self.randomChoice()
      return goal_list


    def randomChoice(self):
      goal_list = []
      for row in range(ROW_COUNT):
        for col in range(COL_COUNT):
          cell = self.model.knownGrid[row][col]
          if cell != '0' and cell != 'P' and cell != 'S' and cell != 'X' and self.isCellFree(row, col):
            goal_list.append((row, col))
      return goal_list


    def moveTo(self, end_x, end_y):
      self.checkObstacleWall()
      start_x, start_y = self.pos

      #right is 1, left is -1, 0 is perfect
      x_dir = self.directionCheck(start_x, end_x)

      #up is 1, down is -1, 0 is perfect
      y_dir = self.directionCheck(start_y, end_y)

      #if free, move directly
      if self.isCellFree(start_x + x_dir, start_y + y_dir):
        self.model.grid.move_agent(self, (start_x + x_dir, start_y + y_dir))

      elif x_dir == 0 or y_dir == 0:
        if x_dir == 0:
          if self.isCellFree(start_x - 1, start_y + y_dir):
            self.model.grid.move_agent(self, (start_x - 1, start_y + y_dir))

          elif self.isCellFree(start_x + 1, start_y + y_dir):
            self.model.grid.move_agent(self, (start_x + 1, start_y + y_dir))

          elif self.isCellFree(start_x - 1, start_y):
            self.model.grid.move_agent(self, (start_x - 1, start_y))

          elif self.isCellFree(start_x + 1, start_y):
            self.model.grid.move_agent(self, (start_x + 1, start_y))

          elif self.isCellFree(start_x - 1, start_y - y_dir):
            self.model.grid.move_agent(self, (start_x - 1, start_y  - y_dir))

          elif self.isCellFree(start_x + 1, start_y  - y_dir):
            self.model.grid.move_agent(self, (start_x + 1, start_y  - y_dir))
          else:
            print("backed into corner")

        elif y_dir == 0:
          if self.isCellFree(start_x + x_dir, start_y - 1):
            self.model.grid.move_agent(self, (start_x + x_dir, start_y - 1))

          elif self.isCellFree(start_x + x_dir, start_y + 1):
            self.model.grid.move_agent(self, (start_x + x_dir, start_y + 1))

          elif self.isCellFree(start_x, start_y - 1):
            self.model.grid.move_agent(self, (start_x, start_y - 1))

          elif self.isCellFree(start_x, start_y + 1):
            self.model.grid.move_agent(self, (start_x, start_y + 1))

          elif self.isCellFree(start_x - x_dir, start_y + 1):
            self.model.grid.move_agent(self, (start_x - x_dir, start_y + 1))

          elif self.isCellFree(start_x - x_dir, start_y  - 1):
            self.model.grid.move_agent(self, (start_x - x_dir, start_y - 1))
          else:
            print("backed into corner")

      else:
        #if not, if horizontal is available, move
        if self.isCellFree(start_x + x_dir, start_y):
            self.model.grid.move_agent(self, (start_x + x_dir, start_y))

        #if not, if vertical is available, move
        elif self.isCellFree(start_x, start_y + y_dir):
            self.model.grid.move_agent(self, (start_x, start_y + y_dir))

        #if not, move horizontally, but away vertically
        elif self.isCellFree(start_x + x_dir, start_y - y_dir):
            self.model.grid.move_agent(self, (start_x + x_dir, start_y - y_dir))

        #if not, move vertically, but away horizontally
        elif self.isCellFree(start_x - x_dir, start_y + y_dir):
            self.model.grid.move_agent(self, (start_x - x_dir, start_y + y_dir))


        #if not, move away vertically
        elif self.isCellFree(start_x, start_y - y_dir):
            self.model.grid.move_agent(self, (start_x, start_y - y_dir))

        #if not, move away horizontally
        elif self.isCellFree(start_x - x_dir, start_y):
            self.model.grid.move_agent(self, (start_x - x_dir, start_y))

        else:
            print("error, moving away")


    def directionCheck(self, start, end):
        if start < end:
            dir = 1 #needs to move to the right/up
        elif start > end:
            dir = -1 #needs to move to left/down
        else:
            dir = 0 #doesn't need to move horizontally/vertically

        return dir


    def clean(self):
        x, y = self.pos
        quantity = int(self.model.knownGrid[x][y])
        pickup_amount = min(quantity, MAX_CAPACITY - self.trash_picked)
        self.trash_picked += pickup_amount
        self.model.knownGrid[x][y] = str(quantity - pickup_amount)


    def checkForObstacles(self):
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore = True, include_center = False)
        for neighbor in neighborhood:
          x, y = neighbor
          if GRID[x][y] == 'X' and self.model.knownGrid[x][y] == 'U':
            self.model.unknown_count -= 1
            self.model.knownGrid[x][y] = 'X'

    def checkObstacleWall(self):
      if self.moveFlag == False:
        return

      neighborhood = self.model.grid.get_neighborhood(self.pos, moore = True, include_center = False)
      obstacle_list = []
      for neighbor in neighborhood:
        x, y = neighbor
        if self.model.knownGrid[x][y] == 'X':
          obstacle_list.append(neighbor)

      if len(obstacle_list) < 3:
        return

      else:
        x_list = []
        y_list = []
        for obstacle in obstacle_list:
          x1, y1 = obstacle
          x_list.append(x1)
          y_list.append(y1)

        x_set = set(x_list)
        y_set = set(y_list)

        startx, starty = self.pos
        goalx, goaly = self.goalPos
        x_dir = self.directionCheck(startx, goalx)
        y_dir = self.directionCheck(starty, goaly)

        if len(x_set) <= len(x_list) - 2:
          self.model.goalPositions.remove(self.goalPos)
          if not self.model.grid.out_of_bounds((startx + x_dir, starty + 2)):
            self.goalPos = (startx + x_dir, starty + 2)
          elif not self.model.grid.out_of_bounds((startx + x_dir, starty - 2)):
            self.goalPos = (startx + x_dir, starty - 2)
          elif not self.model.grid.out_of_bounds((startx, starty + 2)):
            self.goalPos = (startx, starty + 2)
          elif not self.model.grid.out_of_bounds((startx, starty - 2)):
            self.goalPos = (startx, starty - 2)
          else:
            print("cry x")
          self.model.goalPositions.append(self.goalPos)

        if len(y_set) <= len(y_list) - 2:
          self.model.goalPositions.remove(self.goalPos)
          if not self.model.grid.out_of_bounds((startx + 2, starty + y_dir)):
            self.goalPos = (startx + 2, starty + y_dir)
          elif not self.model.grid.out_of_bounds((startx - 2, starty + y_dir)):
            self.goalPos = (startx - 2, starty + y_dir)
          elif not self.model.grid.out_of_bounds((startx + 2, starty)):
            self.goalPos = (startx + 2, starty)
          elif not self.model.grid.out_of_bounds((startx - 2, starty)):
            self.goalPos = (startx - 2, starty)
          else:
            print("cry y")
          self.model.goalPositions.append(self.goalPos)



    def isDone(self):
      allowed_chars = {'0', 'X', 'S', 'P'}
      for row in self.model.knownGrid:
        for cell in row:
          if cell not in allowed_chars:
            self.model.cleanFlag = False
            return
      self.model.cleanFlag = True
      return

class GridModel(Model):
    def __init__(self, width, height, num_robots):
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.counter = 1
        self.knownGrid, self.start, self.papelera, self.unknown_count = translateGrid()
        self.startx, self.starty = self.start
        self.goalPositions = []
        self.cleanFlag = False
        self.robotPosx = []
        self.robotPosy = []
        self.intGrid = []

        #Create robots
        for i in range(num_robots):
            robot = Robot(i, self)
            self.grid.place_agent(robot, self.start)
            self.schedule.add(robot)

    def step(self):
      temp_listx = []
      temp_listy = []
      for agent in self.schedule.agents:
        x, y = agent.pos
        temp_listx.append(x)
        temp_listy.append(y)
      
      known_grid = []      
      for row in range(ROW_COUNT):
        for col in range(COL_COUNT):
          cell = self.knownGrid[row][col]
          if cell == "P":
            known_grid.append(3)
          elif cell == "S":
            known_grid.append(4)
          elif cell == "U":
            known_grid.append(0)
          elif cell == "0":
            known_grid.append(2)
          elif cell == "X":
            known_grid.append(5)
          else:
            known_grid.append(6)
      self.intGrid = known_grid
        
      self.robotPosx = temp_listx
      self.robotPosy = temp_listy

      self.schedule.step()
      self.counter += 1

MAX_CAPACITY = 5
NUM_ROBOTS = 5

#Initialize model
model = GridModel(ROW_COUNT, COL_COUNT, NUM_ROBOTS)