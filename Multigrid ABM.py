'''Nathaniel Flemming 28/2/23'''
#  Agent Based Modeling package imports
from mesa import Model, Agent
from mesa.time import RandomActivation
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
        #current_spending = self.current_city.spending_level
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


#  initialize model
class multigridmodel(Model):
    def __init__(self, residents, height, width, city_spending_range, resident_preference_range):
        self.num_residents = residents
        self.height = height
        self.width = width
        self.city_spending_range = city_spending_range
        self.resident_preference_range = resident_preference_range
        self.schedule = RandomActivation(self)  # schedule for which agent moves when
        self.grid = MultiGrid(width, height, torus=True)  # set torus so no edge
        self.gap = 0  # start at 0 spending-preference gap, will check agent city gap
        self.datacollector = DataCollector({"gap": lambda m: m.gap})  # pull preference spending gap
        self.running = True  # whether ABM is still running
        #  create resident agents
        for i in range(self.num_residents):
            #  set place on grid (random)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            resident = Resident(i, self, self.resident_preference_range[i])  # agent w/ given params
            self.grid.place_agent(resident, (x, y))  # place agent on grid
            self.schedule.add(resident)  # add agent to schedule

        #  Create city agents
        k=0
        for cell in self.grid.coord_iter():  # iterate through grid coords, use coords as id so no doubling up with residents
            # set place on grid (sequentially fill every cell)
            x = cell[1]
            y = cell[2]
            city = City(cell, self, self.city_spending_range[k])  # agent w/ given params, need another set of unique ids
            #couldn't add cities to the schedule for some reason, maybe need 2 schedules?
            self.grid.place_agent(city, (x, y))  # place agent on grid
            k=k+1
    def step(self):  # run model, has agent move and update
        self.gap = 0 #reset gap
        self.schedule.step() #take step
        self.datacollector.collect(self)  # collect data at each step, from instance of class
        if self.gap > 0:  # check if gap is greater than some value
            self.running = False #if gap small enough stop


if __name__ == '__main__':
    num_res = 3
    height = 10
    width = 10
    num_cities = height*width
    preferences = np.random.randint(1,10, num_res)
    spending_lvls = np.random.randint(1,200, num_cities)

    model = multigridmodel(num_res, height, width, spending_lvls, preferences)  # residents, height, width, city spending range, resident pref range
#    one city is made per cell

    for step in range(10):
        model.step()
        #print(model.schedule.steps)
        model_out = model.datacollector.get_model_vars_dataframe()
        model_out.gap.plot()


    while model.running and model.schedule.steps < 10:
        model.step()
        print('step')

