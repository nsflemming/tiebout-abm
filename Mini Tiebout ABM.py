'''Nathaniel Flemming 28/2/23'''
#  Agent Based Modeling package imports
from mesa import Model, Agent
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random
import numpy as np
import pandas as pd

class Resident(Agent):
    def __init__(self, id, model, preference):  # unique id, model,
        super().__init__(id, model)  # super lets you take args from other classes, in this case model
        self.preference = preference
        self.current_city = None #need to start w/ city at current position

    def step(self):
        neighbor_spending = []
        current_spending = 999 #doesn't work if variable is unassigned before for loop, set arbitrarily high
        #neighboring cities to iterate over
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore = True, include_center=True):
            if isinstance(neighbor, City) and neighbor.pos == self.pos: #set current city and current spending
                self.current_city = neighbor #current city = neighbor with same position
                current_spending = self.current_city.spending_level #current spending = that city's spending
                self.model.gap += abs(self.current_city.spending_level - self.preference)  # update model, add current spending gap to model tally
                # this is the gap between the agent's preference and the city's most recent spending level
                # the spending level may be different from when the agent first moved here since cities activate second
            if isinstance(neighbor, City):
                neighbor_spending.append(neighbor.spending_level)
        closest_spending = min(neighbor_spending, key=lambda x: abs(x-self.preference)) #find smallest spending gap
        if abs(closest_spending-self.preference) < abs(current_spending-self.preference): #if there's a city with a smaller gap than the current one...
            candidates = [neighbor for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=True)
                          if isinstance(neighbor, City) and neighbor.spending_level == closest_spending]
            if candidates:
                new_city = random.choice(candidates)
                self.model.grid.move_agent(self, new_city.pos)
                self.current_city = new_city


class City(Agent):
    def __init__(self, id, model, spending_level):  # id, model, spending level
        super().__init__(id, model)
        self.spending_level = spending_level

    def step(self):  # City looks at residents in and around it and adjusts spending to match mean preference, if there are residents
        resident_preferences = []  # initialize resident preferences list
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore = True, include_center=True):  # find preferences of all neighboring residents
            if isinstance(neighbor, Resident):
                resident_preferences.append(neighbor.preference)  # append to list
        if resident_preferences:  # if resident preferences list isn't empty (i.e. there's at least 1 neighboring resident)
            self.spending_level = np.mean(resident_preferences)  # calc mean preference and set spending equal to it
        self.model.spending_levels.append(self.spending_level)  # add spending to model level list of spending levels


#  initialize model
class MiniModel(Model):
    def __init__(self, residents, height, width, num_cities, city_spending, resident_preferences, min_gap):
        self.num_residents = residents
        self.height = height
        self.width = width
        self.num_cities = num_cities
        self.city_spending = city_spending
        self.resident_preferences = resident_preferences
        self.min_gap = min_gap
        self.schedule = BaseScheduler(self)  # schedule for which Resident and city moves when, they activate in order
        self.grid = MultiGrid(width, height, torus=True)  # set torus so no edge
        self.gap = 0  # start at 0 spending-preference gap, will check agent city gap
        self.spending_levels = [] #create empty spending levels list
        self.datacollector = DataCollector({"gap": lambda m: m.gap, "spending_levels": lambda m: m.spending_levels})
        self.running = True  # whether ABM is still running

        #  Create Resident agents
        #  Because residents are added to the schedule first, they will move first, since agents activate in order
        for i in range(self.num_residents):
            #  set place on grid (random)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            resident = Resident(i, self, self.resident_preferences[i])  # create resident and assign preference
            self.grid.place_agent(resident, (x, y))  # place agent on grid
            self.schedule.add(resident)  # add agent to schedule

        #  Create City agents
        k = 0  # create new variable to increment
        id = i + 1  # create unique City ids starting where Residents leave off
        for cell in self.grid.coord_iter():
            # set place on grid, iterating through grid coordinates
            x = cell[1]
            y = cell[2]
            city = City(id, self, self.city_spending[k])  # create cities and assign spending
            self.grid.place_agent(city, (x, y))  # place agent on grid at next location
            self.schedule.add(city)  # add agent to schedule
            k += 1  # increment spending index
            id += 1  # increment city id index

    def step(self):  # run model, has agent move, updates gap, checks if gap is small enough to stop
        self.gap = 0  # reset spending-preference gap
        self.schedule.step()   # agents all take a step
        self.datacollector.collect(self)  # collect data at each step, from instance of class
        if self.gap < self.min_gap:  # check if gap is greater than some set value
            self.running = False  # If the gap between spending and preferences is small enough, stop


if __name__ == '__main__':
    num_res = 5  # desired number of residents
    height = 5  # height of grid
    width = 5  # width of grid
    num_cities = height*width  # desired number of cities (currently one city per cell)
    preferences = np.random.randint(1,21, num_res)  # resident preferences
    spending_lvls = np.random.randint(1,21, num_cities)  # city spending levels
    min_gap = 5  # minimum total gap between spending and preferences that will make the model stop
# create model
    model = MiniModel(num_res, height, width, num_cities, spending_lvls, preferences, min_gap)

    steps = 100  # max number of steps the model will take
    for step in range(10):  # take 10 steps
        model.step()
        #print(model.schedule.steps)
        model_out = model.datacollector.get_model_vars_dataframe()
        #print(model_out.gap)
        model_out.gap.plot()
        # spending levels is a series of identical lists, one for each step with every spending level that occurred
    df = pd.DataFrame(model_out.spending_levels)  # extract spending levels from model output as a data frame
    row1 = pd.DataFrame(df['spending_levels'].iloc[0])  # get just the first row, since all rows are identical
    spending_matrix = np.reshape(row1.values, (steps, num_cities))  # reshape that row into a num of steps by num of cities array
    spending_matrix = np.vstack([spending_lvls, spending_matrix])  # add original spending preferences as first row of matrix

    while model.running and model.schedule.steps < steps:  # run until gap falls below a threshold, or for N steps
        model.step()
        model_out = model.datacollector.get_model_vars_dataframe()
        # print(model_out.gap)
        model_out.gap.plot()
    print(model.schedule.steps)  # how many steps did the model take
    df = pd.DataFrame(model_out.spending_levels)  # extract spending levels from model output as a data frame
    row1 = pd.DataFrame(df['spending_levels'].iloc[0])  # get just the first row, since all rows are identical
    spending_matrix = np.reshape(row1.values, (steps, num_cities))  # reshape that row into a num of steps by num of cities array
    spending_matrix = np.vstack([spending_lvls, spending_matrix])  # add original spending preferences as first row of matrix
