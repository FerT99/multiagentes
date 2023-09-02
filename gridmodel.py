# Grid Model
from mesa import Agent, Model 
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128

import numpy as np
import pandas as pd
import random

import time
import datetime

class GridModel(Model):
    def __init__(self, width, height, num_robots):
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            agent_reporters={"Trash Picked": "trash_picked"}
        )
        self.counter = 0
        self.knownGrid = translateGrid()



        #Create obstacles and trash piles based on the MAP
        for i in range(n_rows):
            for j in range(n_cols):
                if MAP[i+1][j] == "X":
                    obstacle = Obstacle((i, j), self)
                    self.grid.place_agent(obstacle, (i, j))
                elif isinstance(MAP[i+1][j], int):
                    trash_pile = TrashPile((i, j), self, MAP[i+1][j])
                    self.grid.place_agent(trash_pile, (i, j))
        
        #Create robots
        for i in range(num_robots):
            robot = Robot(i, self)
            self.grid.place_agent(robot, STARTING_POINT)
            self.schedule.add(robot)

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.counter += 1

# %%
width = 0
height = 0
num_robots = 5
max_iterations = 0

#Initialize model
model = (width, height, num_robots)

while self.counter < max_iterations:
    model.step()

# %%