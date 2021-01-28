'''
Zero-Intelligence Traders Dummy Code
==========================================
This is an example of writing our own scheduler, and not using agent-level
step() methods.
'''
from mesa import Model, Agent
from mesa.time import BaseScheduler

class SellerAgent(Agent):
    def __init__(self, max_cost):
        self.cost = random.random() * max_cost

class BuyerAgent(Agent):
    def __init__(self, max_value):
        self.value = random.random() * max_value

class TradeScheduler(BaseScheduler):
    def __init__(self, model):
        self.model = model
        self.buyer_set = set()
        self.seller_set = set()
        self.steps = 0

    def add(self, agent):
        if type(agent) is SellerAgent:
            self.seller_set.add(agent)
        if type(agent) is BuyerAgent:
            self.buyer_set.add(agent)

    def remove(self, agent):
        if type(agent) is SellerAgent:
            self.seller_set.remove(agent)
        if type(agent) is BuyerAgent:
            self.buyer_set.remove(agent)

    def is_running(self):
        if len(self.seller_set) > 0 and len(self.buyer_set) > 0:
            return True
        else:
            return False


    def step(self):
        '''
        Randomly activate a buyer and a seller
        '''

        active_buyer = random.choice(list(self.buyer_set))
        active_seller = random.choice(list(self.seller_set))
        self.steps += 1
        return (active_buyer, active_seller)


class ZIModel(Model):

    def __init__(self, max_price, num_agents):
        '''
        Assume the same number of buyers and sellers, and a shared max price
        '''

        self.max_price = max_price
        self.N = num_agents
        self.schedule = TradeScheduler(self)
        self.trades = []

        # Create the agents
        for i in range(self.N):
            self.schedule.add(BuyerAgent(self.max_price))
            self.schedule.add(SellerAgent(self.max_price))


    def go(self):
        active_buyer, active_seller = self.schedule.step()
        ask_price = active_seller.cost + random.random() * (self.max_price - active_seller.cost)
        offer_price = random.random() * active_buyer.value
        if offer_price > ask_price:
            close_price = ask_price + random.random() * (offer_price - ask_price)
            self.trades.append(close_price)
            self.schedule.remove(active_buyer)
            self.schedule.remove(active_seller)
        else:
            self.trades.append(None)


if __name__ == "__main__":
    model = ZIModel(100, 20)
    while model.schedule.is_running():
        model.go()

