'''Nathaniel Flemming 15/2/23'''
#  Agent Based Modeling package imports
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid, MultiGrid
from mesa.datacollection import DataCollector
import random

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
        self.gap = 10  # start at 10 spending-preference gap, will check agent city gap
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
            resident.step()

        #  Create city agents
        k=1
        for cell in self.grid.coord_iter():  # iterate through grid coords
            # set place on grid (sequentially fill every cell)
            x = cell[1]
            y = cell[2]
            city = City(cell, self, self.city_spending_range[k])  # agent w/ given params
            #couldn't add cities to the schedule for some reason, maybe need 2 schedules?
            self.grid.place_agent(city, (x, y))  # place agent on grid
            k=k+1
    def step(self):  # run model, has agent move and update
        self.gap = 10
        self.schedule.step()
        self.datacollector.collect(self)  # collect data at each step, from instance of class
        if self.gap < 2:  # check if gap is less than some value
            self.running = False

class Resident(Agent):
    def __init__(self, id, model, preference):  # unique id, model,
        super().__init__(id, model)  # super lets you take args from other classes, in this case model
        self.preference = preference
        self.current_city = None

    def step(self):
        current_spending = self.current_city.spending_level
        neighbor_spending = []
        #neighboring cities to iterate over
        for neighbor in self.model.grid.neighbor_iter(self.current_city.pos, moore = True):
            if isinstance(neighbor, City):
                neighbor_spending.append(neighbor.spending_level)
        closest_spending = min(neighbor_spending, key=lambda x: abs(x-self.preference)) #find smallest spending gap
        if abs(closest_spending-self.preference) <= abs(current_spending-self.preference):
            candidates = [neighbor for neighbor in self.model.grid.neighbor_iter(self.current_city.pos, moore=True) if isinstance(neighbor, City) and neighbor.spending_level == closest_spending]
            if candidates:
                new_city = random.choice(candidates)
                self.model.grid.move_agent(self, new_city.pos)
                self.current_city = new_city
       ''' neighborcities = self.model.grid.neighbor_iter(
            self.pos,
            moore=True)
            # include_center=True,
            # radius=1)  # iterate over all neighbors of pos of current agent
        ##  spending gap comparison
        #currentgap = 3 #  initialize current gap?
        for city in neighborcities: #  How do I do this without iterating through all the neighbors?
            if city.pos == self.pos:
                currentgap = self.preference - city.spending #  check current gap between spending and preferences
            elif city.pos != self.pos:
                newgap = self.preference - city.spending #  check gaps for other cities
                if newgap < currentgap: #  if find a city that's a better match...
                    self.model.grid.move_agent(self, pos = city.pos)  # move self to new city
        print(currentgap)
        self.model.gap = currentgap
        '''

class City(Agent):
    def __init__(self, id, model, spending_level):  # id, model
        super().__init__(id, model)
        #  randomize spending (same range as preference)
        self.spending_level = spending_level

model = multigridmodel(1, 3, 3, [1,2,3,4,5,6,7,8,9],[1,2,3])  # residents, height, width, city spending range, resident pref range
# one city is made per cell

for step in range(10):
    model.step()
    print('step')

print(model.schedule.steps)
model_out = model.datacollector.get_model_vars_dataframe()
model_out.gap.plot()


while model.running and model.schedule.steps < 10:
    model.step()
    print('step')

