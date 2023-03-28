'''
City Functions for the multigrid ABM
'''
################### Table of Contents ######################
'''
0.Required packages
1. get_prefs: Extract resident preferences from resident neighbors
2. calc_mean_prefs: (multi-preference) Calculate mean preferences over all neighboring residents
3. Minimum decision (single preference)
4. Candidate list, minimum mean gap (multi-preference)
'''
#############################################################
#0
import numpy

#1
def get_prefs(neighbor):
    if isinstance(neighbor, Resident):
        return neighbor.preferences

#2
def calc_mean_prefs (resident_preferences, num_prefs):
    spending_levels = []
    for i in range(1, num_prefs):
        spending_levels[i] = numpy.mean(resident_preferences[:i])
    return spending_levels

#3
def calc_mean_pref (resident_preferences):
    return numpy.mean(resident_preferences)