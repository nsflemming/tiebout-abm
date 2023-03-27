'''
Resident Functions for the multigrid ABM
'''
################### Table of Contents ######################
'''
0.Required packages
1. Single preference step function 
2. Mean gap (multi-preference)
3. Minimum decision (single preference)
4. Candidate list, minimum mean gap (multi-preference)
'''
#############################################################
#0
import numpy

#1
#2
def calc_mean_gap(self, neighbor):  # calculates mean gap between city spending and preferences
    mean_gap = numpy.mean(abs(neighbor.spending_levels - self.preferences))  # update model, add current overall spending gap to model tally
        # this is the gap between the agent's preference and the city's most recent spending level
        # the spending level may be different from when the agent first moved here since cities activate second
    return mean_gap

#3
#4
def find_cands_min_mean(self, min_gap):  # creates a list of candidates from neighboring cities based on mean gap and a minimum gap
    candidates = [neighbor for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=True)
                  # find all the cities with the minimum gap
                  if isinstance(neighbor, City) and numpy.mean(abs(neighbor.spending_levels - self.preferences)) == min_gap]
    return(candidates)
