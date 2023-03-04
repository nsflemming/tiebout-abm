'''Nathaniel Flemming 28/2/23'''
#  Agent Based Modeling package imports
from mesa import Model, Agent
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random
import numpy as np

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
        self.model.gap += abs(self.current_city.spending_level-self.preference)  # update model, add spending gap to model tally
        # print(self.current_city.spending_level-self.preference)

class City(Agent):
    def __init__(self, id, model, spending_level):  # id, model, spending level
        super().__init__(id, model)
        self.spending_level = spending_level

    def step(self):  # City looks at residents in and around it and adjusts spending to match mean preference
        ## need to add a check to skip calculation if there are no residents
        resident_preferences = []  # initialize resident preferences list
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore = True, include_center=True):  # find preferences of all neighboring residents
            if isinstance(neighbor, Resident):
                resident_preferences.append(neighbor.preference)  # append to list
        self.spending_level = np.mean(resident_preferences)  # calculate mean preference and set spending equal to it


#  initialize model
class multigridmodel(Model):
    def __init__(self, residents, height, width, num_cities, city_spending_range, resident_preference_range):
        self.num_residents = residents
        self.height = height
        self.width = width
        self.num_cities = num_cities
        self.city_spending_range = city_spending_range
        self.resident_preference_range = resident_preference_range
        self.schedule = BaseScheduler(self)  # schedule for which Resident and city moves when, they activate in order
        #self.Cityschedule = SimultaneousActivation(self)  # schedule for which City acts when, they all activate at the same time
        self.grid = MultiGrid(width, height, torus=True)  # set torus so no edge
        self.gap = 0  # start at 0 spending-preference gap, will check agent city gap
        self.datacollector = DataCollector({"gap": lambda m: m.gap})
        #                                      {"spending_level": lambda a: a.spending_level})  # pull preference spending gap from model at each model step
        #             agent_reporters={"Spending_levels": ["unique_id","spending_level"]})  # pull city spending levels from each city agent
        self.running = True  # whether ABM is still running

        #  Create city agents
        for i in range(self.num_cities):
            # set place on grid (sequentially fill every cell)
            x = self.random.randrange(self.grid.width)  # set random coordinates
            y = self.random.randrange(self.grid.height)
            city = City(i, self, self.city_spending_range[i])  # create cities and assign spending
            self.grid.place_agent(city, (x, y))  # place agent on grid at random location
            self.schedule.add(city)  # add agent to schedule

        #  create resident agents
        k = 0
        id = i + 1  # create unique resident ids starting where cities leave off
        for i in range(self.num_residents):
            #  set place on grid (random)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            resident = Resident(id, self, self.resident_preference_range[i])  # agent w/ given params
            self.grid.place_agent(resident, (x, y))  # place agent on grid
            self.schedule.add(resident)  # add agent to schedule
            k += 1  # increment spending index
            id += 1  # increment city id index

    def step(self):  # run model, has agent move and update
        self.gap = 0 #reset gap
        self.schedule.step()  #agents take step
        self.datacollector.collect(self)  # collect data at each step, from instance of class
        if self.gap > 0:  # check if gap is greater than some value
            self.running = False #if gap small enough stop


if __name__ == '__main__':
    num_res = 5
    height = 5
    width = 5
    num_cities = height*width
    preferences = np.random.randint(1,10, num_res)
    spending_lvls = np.random.randint(1,20, num_cities)

    model = multigridmodel(num_res, height, width, num_cities, spending_lvls, preferences)  # residents, height, width, city spending range, resident pref range
#    one city is made per cell

    for step in range(10):
        model.step()
        #print(model.schedule.steps)
        model_out = model.datacollector.get_model_vars_dataframe()
        model_out.gap.plot()
        #city_spending = model.datacollector.get_agent_vars_dataframe()
        #city_spending.head()


    while model.running and model.schedule.steps < 10:
        model.step()
        print('step')

