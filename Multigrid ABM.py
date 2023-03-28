'''Nathaniel Flemming 28/2/23'''
import numpy
#  Agent Based Modeling package imports
from mesa import Model, Agent
from mesa.time import BaseScheduler, RandomActivation, SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random
import numpy as np
import pandas as pd
import ResidentFunctions as rf
import CityFunctions as cf

'''
def calc_mean_gap(self, neighbor):  # calculates mean gap over multiple preferences
    mean_gap = np.mean(abs(neighbor.spending_levels - self.preferences))  # update model, add current overall spending gap to model tally
        # this is the gap between the agent's preference and the city's most recent spending level
        # the spending level may be different from when the agent first moved here since cities activate second
    return mean_gap


def find_cands_min_mean(self, min_gap):  # creates a list of candidates from neighboring cities based on mean gap and a minimum gap
    candidates = [neighbor for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=True)
                  # find all the cities with the minimum gap
                  if isinstance(neighbor, City) and np.mean(abs(neighbor.spending_levels - self.preferences)) == min_gap]
    return(candidates)
'''
class Resident(Agent):
    def __init__(self, id, model, preferences):  # unique id, model,
        super().__init__(id, model)  # super lets you take args from other classes, in this case model
        self.preferences = preferences #assign preference values, store as array?
        self.current_city = None #need to start w/ city at current position

    def step(self):
        ''' turn this into a setup function?'''
        mean_gap = []  # initialize list of overall gaps b/t pref and cities' spending
        #neighboring cities to iterate over
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=True):
            if isinstance(neighbor, City) and neighbor.pos == self.pos:  # calculate metric for current city
                current_gap = rf.calc_mean_gap(self, neighbor)  # currently calculating mean gap
            if isinstance(neighbor, City):  # calculate metrics for all other neighboring cities
                mean_gap.append(rf.calc_mean_gap(self, neighbor))  # currently calculating mean gap
        self.model.gap += current_gap # add current gap to model level tally
        min_gap = min(mean_gap) #find smallest mean spending gap
        if min_gap < current_gap: #if there's a city with a smaller overall gap than the current one...
            candidates = rf.find_cands_min_mean(self, min_gap)
            if candidates:  # if there are cities with closer spending, move to one
                new_city = random.choice(candidates)
                self.model.grid.move_agent(self, new_city.pos)
                self.current_city = new_city


class City(Agent):
    def __init__(self, id, model, spending_lvls):  # id, model, spending level
        super().__init__(id, model)
        self.spending_levels = spending_lvls

    def step(self):  # City looks at residents in and around it and adjusts spending to match mean preference, if there are residents
        resident_preferences = [] #initialize list to hold preferences, convert to array later
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore = True, include_center=True):  # find preferences of all neighboring residents
            resident_preferences.append(cf.get_prefs(neighbor))  # append to list
        if resident_preferences:  # if resident preferences list isn't empty (i.e. there's at least 1 neighboring resident)
            self.spending_levels = cf.calc_mean_prefs(resident_preferences)  # calc mean preferences over all residents and set spending levels equal to it
        self.model.spending_levels.append(self.spending_levels)  # add spending to model level array of spending levels


#  initialize model
class multigridmodel(Model):
    def __init__(self, residents, height, width, num_cities, city_spending_lvls, resident_preferences, min_gap):
        self.num_residents = residents
        self.height = height
        self.width = width
        self.num_cities = num_cities
        self.city_spending_lvls = city_spending_lvls
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
            resident = Resident(i, self, self.resident_preferences[i])  # agent w/ given params
            self.grid.place_agent(resident, (x, y))  # place agent on grid
            self.schedule.add(resident)  # add agent to schedule

        #  create City agents
        k = 0
        id = i + 1  # create unique resident ids starting where cities leave off
        for cell in self.grid.coord_iter():  # iterate through grid coords
            x = cell[1]
            y = cell[2]
            city = City(id, self, self.city_spending_lvls[k])  # create cities and assign spending
            self.grid.place_agent(city, (x, y))  # place agent on grid at random location
            self.schedule.add(city)  # add agent to schedule
            k += 1  # increment spending index
            id += 1  # increment city id index

    def step(self):  # run model, has agents move and update
        self.gap = 0 #reset gap
        self.schedule.step()  #agents take step
        self.datacollector.collect(self)  # collect data at each step, from instance of class
        if self.gap < self.min_gap:  # check if gap is greater than some value
            self.running = False #if gap small enough stop


if __name__ == '__main__':
    num_res = 1  # desired number of residents
    height = 4  # height of grid
    width = 4  # width of grid
    num_cities = height*width  # desired number of cities
    preferences = np.random.randint(1,21, size=[num_res,4])  # resident preference array
    spending_lvls = np.random.randint(1,21, size=[num_cities,4])  # city spending levels array
    min_gap = 5  # minimum total gap between spending and preferences that will make the model stop
# create model
    model = multigridmodel(num_res, height, width, num_cities, spending_lvls, preferences, min_gap) 
#    one city is made per cell (grid width x height)

    steps = 100  # max number of steps the model will take
    for step in range(10):  # take 10 steps
        model.step()
        #print(model.schedule.steps)
        model_out = model.datacollector.get_model_vars_dataframe()
        #print(model_out.gap)
        model_out.gap.plot()
        # spending levels is a series of identical lists, one for each step with every spending level that occurred
    df = pd.DataFrame(model_out.spending_levels)  # extract spending levels from model output as a data frame
    #row1 = pd.DataFrame(df['spending_levels'].iloc[0])  # get just the first row, since all rows are identical
    #spending_matrix = np.reshape(row1.values, (steps, num_cities))  # reshape that row into a num of steps by num of cities array
    #spending_matrix = np.vstack([spending_lvls, spending_matrix])  # add original spending preferences as first row of matrix

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
