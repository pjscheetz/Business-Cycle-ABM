from mesa import Model
import random
import time
from abm_econ.agents import FirmAgent,ConsumerAgent
from abm_econ.scheduler import CustomScheduler
from mesa.datacollection import DataCollector

class MoneyModel(Model):
    """A model with some number of agents."""
    def __init__(self, N1, N2):
        self.num_consumer_agents = N1
        self.num_firm_agents = N2
        self.firm_employment=dict()
        self.employment_numbers=0
        self.schedule = CustomScheduler(self)
        self.wr=WeightedRandomizer(self.firm_employment)
        self.total_household_wealth=0
        # Create agents
        for i in range(self.num_firm_agents):
            a = FirmAgent(i+1, self)
            self.schedule.add(a)
        for i in range(self.num_consumer_agents):
            a = ConsumerAgent(i+1, self)
            self.schedule.add(a)
        self.wr.update_weights(self.firm_employment)
        self.datacollector = DataCollector(
            model_reporters={"Employment": "employment_numbers"}  # A function to call
            )
        self.datacollector2 = DataCollector(
            model_reporters={"Household Wealth": "total_household_wealth"}  # A function to call
            )
        self.running = True


    def step(self):
        '''Advance the model by one step.'''
        #self.total_household_wealth=0
        self.employment_numbers=0
        start = time.time()
        self.schedule.step()
        print("Total household wealth - "+str(self.total_household_wealth))
        end = time.time()
        self.datacollector.collect(self)
        self.datacollector2.collect(self)
        self.wr.update_weights(self.firm_employment)

    def run_model(self, n):
        for i in range(n):
            self.step()

class WeightedRandomizer:
    def __init__ (self, weights):
        self.__max = .0
        self.__weights = []

    def update_weights(self, weights):
        self.__max = .0
        self.__weights = []
        for value, weight in weights.items ():
            self.__max += weight
            self.__weights.append ( (self.__max, value) )
        
    def get_max(self):
        return self.__max

    def random (self):
        r = random.random () * self.__max
        for ceil, value in self.__weights:
            if ceil > r: return value