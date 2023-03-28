'''
Resident Functions for the multigrid ABM
'''
################### Table of Contents ######################
'''
0.Required packages
1. calc_gap: Absolute gap (single preference)
2. calc_mean_gap: Mean gap (multi-preference)
3. find_cands_min: Candidate list, minimum gap (single preference) 
4. find_cands_min_mean: Candidate list, minimum mean gap (multi-preference)
'''
#############################################################
#0
import numpy

#1
def calc_gap(self, neighbor):
    return abs(neighbor.spending_level - self.preference)  # calculate absolute gap between preference and spending
#2
def calc_mean_gap(self, neighbor):  # calculates mean gap between city spending and preferences
    mean_gap = numpy.mean(abs(neighbor.spending_levels - self.preferences))  # update model, add current overall spending gap to model tally
        # this is the gap between the agent's preference and the city's most recent spending level
        # the spending level may be different from when the agent first moved here since cities activate second
    return mean_gap

#3
def find_cands_min(self, min_gap):
    return [neighbor for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=True)
            if isinstance(neighbor, City) and neighbor.spending_level == min_gap]

#4
def find_cands_min_mean(self, min_gap):  # creates a list of candidates from neighboring cities based on mean gap and a minimum gap
    return [neighbor for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=True)
                  # find all the cities with the minimum gap
            if isinstance(neighbor, City) and numpy.mean(abs(neighbor.spending_levels - self.preferences)) == min_gap]

