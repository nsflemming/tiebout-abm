'''Nathaniel Flemming 15/2/23'''
#  Agent Based Modeling package imports
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid, MultiGrid
from mesa.datacollection import DataCollector
import random

#  initialize model
class multigridmodel(Model):
    def __init__(self, height, width, density, spending, preference):
        self.height = height
        self.width = width
        self.density = density
        self.spending = spending
        self.preference = preference
        self.schedule = RandomActivation(self)  # schedule for which agent moves when
        self.grid = MultiGrid(width, height, torus=True)  # set torus so no edge
        self.happy = 0  # start at 0 happy, will go through and check if agents happy
        self.datacollector = DataCollector({"happy": lambda m: m.happy})  # pull # of happy agents
        self.running = True  # whether ABM is still running