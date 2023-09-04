# -*- coding: utf-8 -*-
"""Copy of debugging.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15Ji6dHy6ZjW-jB1q18nL3X0cZPyn03Vb
"""

!pip install numpy scikit-learn matplotlib seaborn mesa

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

with open("input2.txt", "r") as my_file:
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


translateGrid()

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
            self.goalPos = (0, 0)

        if self.trash_picked == MAX_CAPACITY:
          self.offload()

        elif self.moveFlag == True:
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
        if potential not in self.model.goalPositions:
          self.model.goalPositions.append(potential)
          self.moveFlag = True
          self.goalPos = potential
          x, y = self.goalPos
          self.moveTo(x, y)
          break
        else:
          possible_options.remove(potential)
      if len(possible_options) == 0:
        second_options = self.randomChoice()
        while len(second_options) > 0:
          potential = random.choice(second_options)
          if potential not in self.model.goalPositions:
            self.model.goalPositions.append(potential)
            self.moveFlag = True
            self.goalPos = potential
            x, y = self.goalPos
            self.moveTo(x, y)
            break
          else:
            second_options.remove(potential)
      if len(possible_options) == 0:
        if len(second_options) == 0:
          print("no options not moving, agent: ", self.unique_id)


    def offload(self):
      if self.moveFlag == True:
        self.moveFlag = False
        self.model.goalPositions.remove(self.goalPos)
        self.goalPos = (0,0)
      if self.pos != self.model.papelera:
        x, y = self.model.papelera
        self.moveTo(x, y)
      else:
        self.trash_picked = 0
        self.explore()


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
        if self.model.knownGrid[x][y] != 'X' and self.model.grid.is_cell_empty((x,y)):
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
        neighborhood = self.model.grid.get_neighborhood(self.pos,
                                              moore = True,
                                              include_center = False)
        for neighbor in neighborhood:
          x, y = neighbor
          if GRID[x][y] == 'X' and self.model.knownGrid[x][y] == 'U':
            self.model.unknown_count -= 1
            self.model.knownGrid[x][y] = 'X'


    def isDone(self):
      allowed_chars = {'0', 'X', 'S', 'P'}
      for row in self.model.knownGrid:
        for cell in row:
          if cell not in allowed_chars:
            self.model.cleanFlag = False
            return
      self.model.cleanFlag = True
      return

def get_grid(model):
  return

class GridModel(Model):
    def __init__(self, width, height, num_robots):
        print(width, height)
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid}
        )
        self.counter = 1
        self.knownGrid, self.start, self.papelera, self.unknown_count = translateGrid()
        self.goalPositions = []
        self.cleanFlag = False

        #Create robots
        for i in range(num_robots):
            robot = Robot(i, self)
            self.grid.place_agent(robot, self.start)
            self.schedule.add(robot)

    def step(self):
      print()
      print("step", self.counter)
      for agent in self.schedule.agents:
        print("self.pos", agent.unique_id, agent.pos)
        print("self.moveflag", agent.unique_id, agent.moveFlag)
        print("self.goalPos", agent.unique_id, agent.goalPos)
        print("self.trashpicked", agent.unique_id, agent.trash_picked)
        print()
      print("step", self.counter)
      print("goal positions list ", self.goalPositions)
      self.datacollector.collect(self)
      self.schedule.step()
      self.counter += 1

MAX_CAPACITY = 5
NUM_ROBOTS = 5

#Initialize model
model = GridModel(ROW_COUNT, COL_COUNT, NUM_ROBOTS)
counter = 0
while model.cleanFlag == False and counter < 100:
    model.step()
    counter += 1
    print('unknown: ', model.unknown_count)
if model.cleanFlag == True:
  print("CLEAAAAN")

grid = model.datacollector.get_model_vars_dataframe()

fig, axis = plt.subplots(figsize=(5, 5))
axis.set_xticks([])
axis.set_yticks([])
patch = plt.imshow(grid.iloc[0][0], cmap=plt.cm.binary)

def animate(i):
    patch.set_data(grid.iloc[i][0])

anim = animation.FuncAnimation(fig, animate, frames=10)

anim

