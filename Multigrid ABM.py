'''Nathaniel Flemming 15/2/23'''
#  Agent Based Modeling package imports
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid, MultiGrid
from mesa.datacollection import DataCollector
import random

#  initialize model
class multigridmodel(Model):
    def __init__(self, residents, height, width):
        self.num_residents = residents
        self.height = height
        self.width = width
        self.schedule = RandomActivation(self)  # schedule for which agent moves when
        self.grid = MultiGrid(width, height, torus=True)  # set torus so no edge
        # self.happy = 0  # start at 0 happy, will go through and check if agents happy
        # self.datacollector = DataCollector({"happy": lambda m: m.happy})  # pull # of happy agents
        self.running = True  # whether ABM is still running
        #  create resident agents
        for i in range(self.num_residents):
            #  set place on grid (random)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            agent = Resident(i, self)  # agent w/ given params
            self.schedule.add(agent)  # add agent to schedule
            self.grid.place_agent(agent, (x, y))  # place agent on grid

        #  Create city agents
        for cell in self.grid.coord_iter():  # iterate through grid coords
            # set place on grid (sequentially fill every cell)
            x = cell[1]
            y = cell[2]
            agent = City(cell, self)  # agent w/ given params
            #couldn't add cities to the schedule for some reason, maybe need 2 schedules?
            self.grid.place_agent(agent, (x, y))  # place agent on grid

class Resident(Agent):
    def __init__(self, id, model):  # unique id, model,
        super().__init__(id, model)  # super lets you take args from other classes, in this case model
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
                print(currentgap)
        newgap = currentgap + 1  # initialize new gap? auto greater than current gap, so not moving is default
        for city in neighborcities:
            if city.pos != self.pos:
                newgap = self.preference - city.spending #  check gaps for other cities
                print(newgap)
                if newgap < currentgap: #  if find a city that's a better match...
                    self.model.grid.move_agent(self, pos = city.pos)  # move self to new city
                    print(self.pos)

class City(Agent):
    def __init__(self, id, model):  # id, model
        super().__init__(id, model)
        #  randomize spending (same range as preference)
        self.spending = random.randint(0,3)

model = multigridmodel(1, 3, 3)  # residents, height, width. One city is made per cell

while model.running and model.schedule.steps < 10:
    model.step()