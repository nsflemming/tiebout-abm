'''Nathaniel Flemming 15/2/23'''
#  Agent Based Modeling package imports
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid, MultiGrid
from mesa.datacollection import DataCollector
import random

#  initialize model
class multigridmodel(Model):
    def __init__(self, height, width, density):
        self.height = height
        self.width = width
        self.density = density
        self.schedule = RandomActivation(self)  # schedule for which agent moves when
        self.grid = MultiGrid(width, height, torus=True)  # set torus so no edge
        self.happy = 0  # start at 0 happy, will go through and check if agents happy
        self.datacollector = DataCollector({"happy": lambda m: m.happy})  # pull # of happy agents
        self.running = True  # whether ABM is still running

class Resident(Agent):
    def __init__(self, pos, model, preference):  # position on grid, model,
        super().__init__(pos, model)  # super lets you take args from other classes, in this case model
        self.pos = pos
        self.preference = preference

    def step(self):  # each step of model, agent can do stuff
        spend =   # initialize spend, the current spending of the city they reside in
        neighbors = self.model.grid.neighbor_iter(self.pos)  # iterate over all neighbors of pos of current agent
        for neighbor in neighbors:  # iterate through neighbors to check type
            if neighbor.spending == self.preference:
                similar += 1  # increment similar if neighbor type matches agent
        # move if not enough similar neighbors
        if similar < self.model.homophily:  # homophily specified in model, what prop of their neighbors need to be same
            self.model.grid.move_to_empty(self)  # move self to empty space
        else:
            self.model.happy += 1  # update model, tell model that have one more happy agent