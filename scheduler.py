from mesa.time import RandomActivation
from collections import OrderedDict
from abm_econ.agents import FirmAgent,ConsumerAgent
import random

class CustomScheduler(RandomActivation):
    def __init__(self, model):
        self.model = model
        self.consumer_set = OrderedDict()
        self.firm_set = OrderedDict()
        self.steps = 0
        self.time = 0

    def add(self, agent):
        if type(agent) is ConsumerAgent:
            self.consumer_set[agent.unique_id] = agent
        if type(agent) is FirmAgent:
            self.firm_set[agent.unique_id] = agent

    def remove(self, agent):
        if type(agent) is ConsumerAgent:
            del self.consumer_set[agent.unique_id]
           
        if type(agent) is FirmAgent:
            del self.firm_set[agent.unique_id]

    def step(self):
        """ Executes the step of all agents, one at a time, in
        random order.

        """
        consumer_agent_keys = list(self.consumer_set.keys())
        random.shuffle(consumer_agent_keys)
        firm_agent_keys = list(self.firm_set.keys())
        random.shuffle(firm_agent_keys)

        for agent_key in firm_agent_keys:
            self.firm_set[agent_key].month_begin_step()
        for agent_key in consumer_agent_keys:
            self.consumer_set[agent_key].month_begin_step()
        
        for day in range(0,21):
            random.shuffle(consumer_agent_keys)
            random.shuffle(firm_agent_keys)
            for agent_key in consumer_agent_keys:
                self.consumer_set[agent_key].step()
            for agent_key in firm_agent_keys:
                self.firm_set[agent_key].step()

        random.shuffle(consumer_agent_keys)
        random.shuffle(firm_agent_keys)

        for agent_key in firm_agent_keys:
            self.firm_set[agent_key].month_end_step()
        for agent_key in consumer_agent_keys:
            self.consumer_set[agent_key].month_end_step()

        self.steps += 1
        self.time += 1
       


