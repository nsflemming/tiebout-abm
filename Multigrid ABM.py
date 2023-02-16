'''Nathaniel Flemming 15/2/23'''
#  Agent Based Modeling package imports
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid, MultiGrid
from mesa.datacollection import DataCollector
import random

#  initialize model
class multigridmodel(Model):
    def __init__(self, residents, cities, height, width, density):
        self.num_residents = residents
        self.num_cities = cities
        self.height = height
        self.width = width
        self.density = density
        self.schedule = RandomActivation(self)  # schedule for which agent moves when
        self.grid = MultiGrid(width, height, torus=True)  # set torus so no edge
        self.happy = 0  # start at 0 happy, will go through and check if agents happy
        self.datacollector = DataCollector({"happy": lambda m: m.happy})  # pull # of happy agents
        self.running = True  # whether ABM is still running
        #  create resident agents
        for i in range(self.num_residents):
            a = Resident(i, self)
            self.schedule.add(a)
            #  place on grid
            x = self.random.randrange(self.grid.width)
            y= self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y))
        #  Create cities agents
        for i in range(self.num_cities):
            a = City(i, self)
            self.schedule.add(a)
            #  place on grid
            x = self.random.randrange(self.grid.width)
            y= self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y))

class Resident(Agent):
    def __init__(self, id, pos, model):  # position on grid, model,
        super().__init__(id, pos, model)  # super lets you take args from other classes, in this case model
        self.pos = pos
        #  randomize preference
        self.preference = random.randint(0,3)
    def step(self):  #  each step of model, agent can do stuff
        #neighboring cities to iterate over
        neighborcities = self.model.grid.neighbor_iter(
            self.pos,
            moore=True,
            include_center=True,
            radius=1)  # iterate over all neighbors of pos of current agent
        ##  spending gap comparison
        currentgap = 3 #  initialize current gap?
        for city in neighborcities: #  How do I do this without iterating through all the neighbors?
            if city.pos == self.pos:
                currentgap = self.preference - city.spending #  check current gap between spending and preferences
        newgap = currentgap + 1  # initialize new gap?
        for city in neighborcities:
            if city.pos != self.pos:
                newgap = self.preference - city.spending #  check gaps for other cities
                if newgap < currentgap: #  if find a city that's a better match...
                    self.model.grid.move_agent(self, pos = city.pos)  # move self to new city

class City(Agent):
    def __init__(self, id, pos, model):  # position on grid, model,