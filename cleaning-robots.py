# # Cleaning Robots
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

# %% [markdown]
# Map syntax:
# * U: unknown
# * S: starting point
# * P: trash can 
# * X: obstacle
# * 0-8: n of trash pieces 

# %%
# Input map. First row: n rows, n, columns
MAP = [[4, 5],
        [0, 1, 1, "X", 1],
        ["S", 0, 1, 6, 7],
        [0, "P", 4, 0, 7],
        [2, 3, 5, "X", 0]]

# %%
n_rows = MAP[0][0]
n_cols = MAP[0][1]

for i in range(n_rows):
    for j in range(n_cols):
        if MAP[i+1][j] == 'S':
            STARTING_POINT = (i, j)
        elif MAP[i+1][j] == 'P':
            TRASHCAN_POS = (i, j)

# %%
class Obstacle(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

# %%
class TrashPile(Agent):
    def __init__(self, unique_id, model, amount):
        super().__init__(unique_id, model)
        self.amount = amount

# %%
class Robot(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.max_capacity = 5 # trash-holding max capacity (constant)
        self.trash_picked = 0 # n of trash pieces picked and holding
        self.known_trash = set() # known trash locations
        self.known_obstacles = set() # known obstacle locations


    def step(self):
        self.update_knowledge()
        while self.trash_picked < self.max_capacity:
            self.explore()
        self.offload() # PENDING... 


    def explore(self):
        neighbors = self.model.grid.get_neighbor(self.pos, moore=True, include_center=False) # adjacent agents

        # Check for neighboring obstacles
        for neighbor in neighbors:
            if isinstance(neighbor, Obstacle):
                self.known_obstacles.add((neighbor.pos))
                self.update_knowledge()
        
        # Valid moves are empty cells or cells containing trash
        valid_moves = [neighbor for neighbor in neighbors 
                       if self.model.grid.is_cell_empty(neighbor)
                       or isinstance(neighbor, TrashPile)
                       and not(neighbor.pos == STARTING_POINT or neighbor == TRASHCAN_POS)]
        
        if valid_moves:
            known_trash_pos = {trash.pos for trash in self.known_trash}
            moves_towards_trash = [move for move in valid_moves if move.pos in known_trash_pos]

            if moves_towards_trash:
                chosen_neighbor = random.choice(moves_towards_trash)
                self.model.grid.move_agent(self, chosen_neighbor.pos)
                self.clean(chosen_neighbor)                
            else:
                chosen_neighbor = random.choice(valid_moves)
                self.model.grid.move_agent(self, chosen_neighbor.pos)
            
                if isinstance(chosen_neighbor, TrashPile): # cell containing trash
                    self.known_trash.add(chosen_neighbor)
                    self.update_knowledge()
                    self.clean(chosen_neighbor)                
        else: # no valid moves
            return
        
        
    def update_knowledge(self):
        for agent in self.model.schedule.agents:
            if isinstance(agent, Robot) and agent != self:
                agent.known_obstacles.update(self.known_obstacles)
                agent.known_trash.update(self.known_trash)


    def clean(self, trash):
        current_capacity = self.max_capacity - self.trash_picked
        pickup_amount = min(current_capacity, trash.amount)
        self.trash_picked += pickup_amount
        trash.amount -= pickup_amount
        if trash.amount == 0:
            self.model.grid.remove_agent(trash)
            self.model.schedule.remove(trash)
            self.known_trash.remove(trash)

    def Moveto(self, end_x, end_y):
        start_x, start_y = self.pos

        #right is 1, left is -1, 0 is perfect
        x_dir = self.DirectionCheck(start_x, end_x)
        
        #up is 1, down is -1, 0 is perfect
        y_dir = self.DirectionCheck(start_y, end_y)

        #if free, move diagonally
        if self.model.is_cell_empty(start_x + x_dir, start_y + y_dir):
            self.model.move_agent(self, (start_x + x_dir, start_y + y_dir))
        
        #if not, if horizontal is available, move
        elif self.model.is_cell_empty(start_x + x_dir, start_y):
            self.model.move_agent(self, (start_x + x_dir, start_y))

        #if not, if vertical is available, move
        elif self.model.is_cell_empty(start_x, start_y + y_dir):
            self.model.move_agent(self, (start_x, start_y + y_dir))
        
        #if not, move horizontally, but away vertically
        elif self.model.is_cell_empty(start_x + x_dir, start_y - y_dir):
            self.model.move_agent(self, (start_x + x_dir, start_y - y_dir))
        
        #if not, move vertically, but away horizontally
        elif self.model.is_cell_empty(start_x - x_dir, start_y + y_dir):
            self.model.move_agent(self, (start_x - x_dir, start_y + y_dir))
        
        #if not, move away vertically
        elif self.model.is_cell_empty(start_x, start_y - y_dir):
            self.model.move_agent(self, (start_x, start_y - y_dir))
        
        #if not, move away horizontally
        elif self.model.is_cell_empty(start_x - x_dir, start_y):
            self.model.move_agent(self, (start_x - x_dir, start_y))
        
        else:
            print("error, backed into corner")
    
    def DirectionCheck(self, start, end):
        if start < end:
            dir = 1 #needs to move to the right/up
        elif start > end:
            dir = -1 #needs to move to left/down
        else:
            dir = 0 #doesn't need to move horizontally/vertically
        
        return dir