from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from abm_econ.model import MoneyModel
from mesa.visualization.UserParam import UserSettableParameter

h_slider = UserSettableParameter('slider', "Number of Consumer Agents", 100, 100, 1000, 50)
f_slider = UserSettableParameter('slider', "Number of Firm Agents", 10, 10, 100, 5)

chart = ChartModule([{"Label": "Employment",
                      "Color": "Black"}],
                    data_collector_name='datacollector')

chart2 = ChartModule([{"Label": "Household Wealth",
                      "Color": "Black"}],
                    data_collector_name='datacollector2')

server = ModularServer(MoneyModel,
                       [chart, chart2],
                       "Money Model",
                       {"N1": h_slider, "N2": f_slider})