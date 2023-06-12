import mesa
from Multigrid_Tiebout_ABM import multigridmodel

def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Color": "red",
        "Filled": "true",
        "Layer": 0,
        "r": 0.5,
    }
    return portrayal

grid = mesa.visualization.CanvasGrid(agent_portrayal, 10, 10, 500, 500)
server = mesa.visualization.ModularServer(
    multigridmodel, [grid], "Multigrid Model", {"N": 100, "width": 10, "height": 10}
)