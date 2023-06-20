import mesa
import numpy as np
from Multigrid_Tiebout_ABM import multigridmodel

# set model parameters
if __name__ == '__main__':
    num_res = 5  # desired number of residents
    height = 5  # height of grid
    width = 5  # width of grid
    num_cities = height*width  # desired number of cities
    preferences = np.random.randint(1,21, size=[num_res,4])  # resident preference array
    resources = np.random.randint(0,2, size=num_res) # resident resources array
    init_spending_lvls = np.random.randint(1,21, size=[num_cities,4])  # city spending levels array
    min_gap = 5  # minimum total gap between spending and preferences that will make the model stop

#set agent portrayal rules
def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "r": 0.5}
    # use id # to color cities and residents differently
    if agent.unique_id > num_res-1:  #city portrayal
        portrayal["Color"] = "navy"
        portrayal["Layer"] = 0
    else: #resident portrayal
        portrayal["Color"] = "white"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    return portrayal

grid = mesa.visualization.CanvasGrid(agent_portrayal, height, width, 500, 500)
chart = mesa.visualization.ChartModule([{"Label": "gap",
                      "Color": "Black"}],
                    data_collector_name='datacollector')
server = mesa.visualization.ModularServer(
    multigridmodel, [grid, chart], "Multigrid Model", {'residents':num_res, 'height':height, 'width':width,
                                                'num_cities':num_cities, 'init_spending_lvls':init_spending_lvls,
                                                'resident_preferences':preferences, 'resident_resources':resources,
                                                'min_gap':min_gap}
)
server.port = 8521 #default
server.launch()