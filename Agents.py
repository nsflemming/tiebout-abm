'''
Agent Classes and Functions for the multigrid ABM
'''
################### Table of Contents ######################
'''
0.Required packages
1. Define agent Classes
    1.1 Resident Class
    1.2 City Class

####### Resident Functions
2. calc_gap: Absolute gap (single preference)
3. calc_mean_gap: Mean gap (multi-preference)
4. find_cands_min: Candidate list, minimum gap (single preference) 
5. find_cands_min_mean: Candidate list, minimum mean gap (multi-preference)

####### City Functions
6. get_prefs: Extract resident preferences from resident neighbors
7. calc_mean_prefs: (multi-preference) Calculate mean preferences over neighboring residents
8. calc_mean_pref: (single preference) Calculate mean preference over neighboring residents (just repackages np.mean)

'''
#############################################################
# 0 Required Packages
from mesa import Agent
import random
import numpy as np

##### 1
#1.1 Resident Class
class Resident(Agent):
    def __init__(self, id, model, preferences):  # unique id, model,
        super().__init__(id, model)  # super lets you take args from other classes, in this case model
        self.preferences = preferences #assign preference values, store as array?
        self.current_city = None #need to start w/ city at current position

    def step(self):
        ''' turn this into a setup function?'''
        mean_gaps = []  # initialize list of overall gaps b/t pref and cities' spending
        #neighboring cities to iterate over
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=True):
            if isinstance(neighbor, City) and neighbor.pos == self.pos:  # calculate metric for current city
                current_gap = calc_mean_gap(self, neighbor)  # currently calculating mean gap
            if isinstance(neighbor, City):  # calculate metrics for all other neighboring cities
                mean_gaps.append(calc_mean_gap(self, neighbor))  # currently calculating mean gap
        self.model.gap += current_gap  # add current gap to model level tally
        min_gap = min(mean_gaps)  # find smallest spending gap
        if min_gap < current_gap:  # if there's a city with a smaller overall gap than the current one...
            candidates = find_cands_min_mean(self, min_gap)
            if candidates:  # if there are cities with closer spending, move to one
                new_city = random.choice(candidates)
                self.model.grid.move_agent(self, new_city.pos)
                self.current_city = new_city

# 1.2 City Class
class City(Agent):
    def __init__(self, id, model, spending_levels):  # id, model, spending level
        super().__init__(id, model)
        self.spending_levels = spending_levels

    def step(self):  # City looks at residents in and around it and adjusts spending to match mean preference, if there are residents
        resident_preferences = [] #initialize list to hold preferences, convert to array later
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore = True, include_center=True): # find preferences of all neighboring residents
            if isinstance(neighbor, Resident):  # check if neighbor is a Resident
                resident_preferences.append(neighbor.preferences)  # append to list
        if resident_preferences:  # if resident preferences list isn't empty (i.e. there's at least 1 neighboring resident)
            num_prefs = np.size(resident_preferences[0])  # Get the number of preferences in each preference array
            self.spending_levels = calc_mean_prefs(resident_preferences, num_prefs)  # calc mean preferences over all residents and set spending levels equal to it
        self.model.spending_levels.append(self.spending_levels)  # add spending to model level array of spending levels


############################################################################### Resident Functions
##### 2 calc_gap: Absolute gap (single preference)
def calc_gap(self, neighbor):
    return abs(neighbor.spending_level - self.preference)  # calculate absolute gap between preference and spending

##### 3. calc_mean_gap: Mean gap (multi-preference)
def calc_mean_gap(self, neighbor):  # calculates mean gap between city spending and preferences
    mean_gap = np.mean(abs(neighbor.spending_levels - self.preferences))  # update model, add current overall spending gap to model tally
        # this is the gap between the agent's preference and the city's most recent spending level
        # the spending level may be different from when the agent first moved here since cities activate second
    return mean_gap

##### 4. find_cands_min: Candidate list, minimum gap (single preference)
def find_cands_min(self, min_gap):
    return [neighbor for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=True)
            if isinstance(neighbor, City) and neighbor.spending_level == min_gap]

##### 5. find_cands_min_mean: Candidate list, minimum mean gap (multi-preference)
def find_cands_min_mean(self, min_gap):  # creates a list of candidates from neighboring cities based on mean gap and a minimum gap
    return [neighbor for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=True)
                  # find all the cities with the minimum gap
            if isinstance(neighbor, City) and np.mean(abs(neighbor.spending_levels - self.preferences)) == min_gap]


############################################################################### City functions
# 6. get_prefs: Extract resident preferences from resident neighbors (no need for dedicated function yet)
def get_prefs(neighbor):
    return neighbor.preferences

# 7. calc_mean_prefs: (multi-preference) Calculate mean preferences over neighboring residents
def calc_mean_prefs (resident_preferences, num_prefs):
    spending_levels = [None] * num_prefs  # create empty list to fill with mean preferences
    for i in range(0, num_prefs):
        ithelements = [arr[i] for arr in resident_preferences]  # get ith element of each array
        spending_levels[i] = np.mean(ithelements)  # take mean of ith elements of the arrays
    return spending_levels

# 8. calc_mean_pref: (single preference) Calculate mean preference over neighboring residents (just repackages np.mean)
def calc_mean_pref (resident_preferences):
    return np.mean(resident_preferences)




