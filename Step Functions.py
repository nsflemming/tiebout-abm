'''
Step Functions for the multigrid ABM
'''
################### Table of Contents ######################
'''
1. Single preference step function 
2. Multi-preference step function
3. Minimum decision (single preference)
4. Minimum Mean decision (multi-preference)
'''
#############################################################

#1
#2
def multi_pref_step(neighbor):
    if isinstance(neighbor, City) and neighbor.pos == self.pos:  # set current city and current spending
        self.current_city = neighbor  # current city = neighbor with same position
        self.model.gap += np.mean(
            abs(self.current_city.spending_levels - self.preferences))  # update model, add current overall spending gap to model tally
        # this is the gap between the agent's preference and the city's most recent spending level
        # the spending level may be different from when the agent first moved here since cities activate second

#3
#4
