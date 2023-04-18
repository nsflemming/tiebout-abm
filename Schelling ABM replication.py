'''Nathaniel Flemming 7/2/23'''
## Agent Based Modeling
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import random

# create agents
class SchellingAgent(Agent):
    def __init__(self, pos, model, agent_type):  # position on grid, model,
        super().__init__(pos, model)  # super lets you take args from other classes, in this case model
        self.pos = pos
        self.type = agent_type

    def step(self):  # each step of model, agent can do stuff
        similar = 0  # initialize similar to track the number of similar neighbors
        neighbors = self.model.grid.neighbor_iter(self.pos)  # iterate over all neighbors of pos of current agent
        for neighbor in neighbors:  # iterate through neighbors to check type
            if neighbor.type == self.type:
                similar += 1  # increment similar if neighbor type matches agent
        # move if not enough similar neighbors
        if similar < self.model.homophily:  # homophily specified in model, what prop of their neighbors need to be same
            self.model.grid.move_to_empty(self)  # move self to empty space
        else:
            self.model.happy += 1  # update model, tell model that have one more happy agent




# create model
class SchellingModel(Model):
    # grid height & width, how much of grid is filled w/ agents, what prop minority, what prop need to not move
    def __init__(self, height, width, density, minority_pc, homophily):
        self.height = height
        self.width = width
        self.density = density
        self.minority_pc = minority_pc
        self.homophily = homophily
        self.schedule = RandomActivation(self)  # schedule for which agent moves when
        self.grid = SingleGrid(width, height, torus=True)  # set torus so no edge
        self.happy = 0  # start at 0 happy, will go through and check if agents happy
        self.datacollector = DataCollector({"happy": lambda m: m.happy})  # pull # of happy agents
        self.running = True  # whether ABM is still running

        for cell in self.grid.coord_iter():  # iterate through grid coords
            x = cell[1]
            y = cell[2]
            if random.random() < self.density:  # if density parameter low, less likely to add agent
                if random.random() < self.minority_pc:  # higher minority % = more likely to add one
                    agent_type = 1
                else:
                    agent_type = 0
                agent = SchellingAgent((x, y), self, agent_type)  # agent w/ given params
                self.grid.position_agent(agent, (x, y))  # place agent on grid
                self.schedule.add(agent)  # add agent to schedule so it'll move

    def step(self):  # run model, has agent move and update
        self.happy = 0
        self.schedule.step()
        self.datacollector.collect(self)  # collect data at each step, from instance of class
        if self.happy == self.schedule.get_agent_count():  # check if all agents happy
            self.running = False


model = SchellingModel(10, 10, .6, .9, 3)  # height, width, density, minority %, homophily

while model.running and model.schedule.steps < 10:
    model.step()

print(model.schedule.steps)
model_out = model.datacollector.get_model_vars_dataframe()
model_out.happy.plot()


# get measure of segregation, prop segregated
def get_segregation(model):
    segregated_agents = 0
    for agent in model.schedule.agents:
        segregated = True
        for neighbor in model.grid.neighbor_iter(agent.pos):  # iterate through agent's neighbors
            if neighbor.type != agent.type:  # if have any neighbors of diff type then not segregated
                segregated = False
                break
        if segregated:
            segregated_agents += 1
    return segregated_agents / model.schedule.get_agent_count()  # num segregated/total agent count


get_segregation(model)

# example test hypo; more density = more iteration?
data = []
for density in range(1, 10):
    density = density / 10
    model = SchellingModel(10, 10, density, 0.4, 3)
    while model.running and model.schedule.steps < 100:
        model.step()
    iterations = model.schedule.steps
    data.append([density, iterations])

# messing with proportion minority
data = []
for minority in range(1, 50):
    minority = minority / 100
    model = SchellingModel(10, 10, 0.6, minority, 3)
    while model.running and model.schedule.steps < 100:
        model.step()
    segregation = get_segregation(model)
    data.append([minority, segregation])

import pandas as pd

df = pd.DataFrame(data, columns=['minority', 'segregation'])
import matplotlib.pyplot as plt

plt.scatter(df.minority, df.segregation)
plt.grid(True)

# messing with grid shape
data = []
for width in range(1, 51):
    model = SchellingModel(50, width, 0.6, 0.4, 3)
    while model.running and model.schedule.steps < 100:
        model.step()
    segregation = get_segregation(model)
    data.append([width, segregation])

import pandas as pd

df = pd.DataFrame(data, columns=['width', 'segregation'])
import matplotlib.pyplot as plt

plt.scatter(df.width, df.segregation)
plt.grid(True)
