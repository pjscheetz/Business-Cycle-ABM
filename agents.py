import random

from mesa import Agent

class ConsumerAgent(Agent):              
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        #self.wealth=random.randint(1000,1500)
        self.wealth=500
        self.employed=False
        self.employer = -1
        self.empl_request_max=5
        self.wage=0
        self.floor_wage=0
        self.daily_demand=0
        self.demand=0
        self.firm_avg_price=0
        #list of firms with TypeA connection
        self.firmlist=set(range(1,11))
        #insantiate list of firms
        #print("Initial firms for Consumer "+str(self.unique_id))
        self.typeA=set(random.sample(self.firmlist, 7))
        self.unfilled_demand_firms=list()
        #self.model.total_household_wealth+=self.wealth
        #print(self.typeA)
        self.assign_job()
        self.model.total_household_wealth+=self.wealth

    def assign_job(self):
        new_firm = random.choice(tuple(self.firmlist))
        self.employed=True
        self.employer=new_firm
        self.wage=self.model.schedule.firm_set[new_firm].wage
        self.model.schedule.firm_set[new_firm].typeB.add(self.unique_id)
        self.model.firm_employment[new_firm]+=1
        self.model.employment_numbers+=1

    def calculate_demand(self):
        if(self.wealth<0):
            self.wealth=0

        self.firm_avg_price=0
        for agent_key in self.typeA:
            self.firm_avg_price+=self.model.schedule.firm_set[agent_key].current_price
        self.firm_avg_price=self.firm_avg_price/7
        self.demand=min((self.wealth/self.firm_avg_price),pow((self.wealth/self.firm_avg_price),.9))
        #self.daily_demand=int(round(min((self.wealth/self.firm_avg_price),pow((self.wealth/self.firm_avg_price),.9))/21))
        self.daily_demand=min((self.wealth/self.firm_avg_price),pow((self.wealth/self.firm_avg_price),.9))/21

    def get_fired(self):
        self.employed=False
        self.wage=0
        self.employer=-1

    def request_employment(self):
        #print("Old employer for Consumer "+str(self.unique_id))
        #print(self.employer)
        #get ID of new firm to apply to
        if(self.employed):
            #new_firm = random.sample((self.firmlist-{self.employer}),1)[0]
            new_firm=random.choice(tuple(self.firmlist-{self.employer}))
        else:
            new_firm = int(random.sample((self.firmlist),1)[0])
        if(self.model.schedule.firm_set[new_firm].is_hiring and self.model.schedule.firm_set[new_firm].wage>self.wage):
            if(self.employed):
                self.model.schedule.firm_set[self.employer].typeB.remove(self.unique_id)
                #self.model.firm_employment[self.employer]-=1
            self.employed=True
            self.employer=new_firm
            self.wage=self.model.schedule.firm_set[new_firm].wage
            self.model.schedule.firm_set[new_firm].hire_emp(self.unique_id)
            return True
        else:
            return False
        #print("New employer for Consumer "+str(self.unique_id))
        #print(self.employer)

    def search_for_new_job(self):
        if(self.wage>self.floor_wage):
            if(random.randint(0,100) < 10):
                self.request_employment()
        elif(self.wage<self.floor_wage and self.wage>0):
            self.request_employment()
        else:
            for x in range(0, 5):
                if(self.request_employment()):
                    break

    def purchase_goods(self):
        day_demand=0
        if(self.wealth<self.daily_demand*self.firm_avg_price):
            day_demand=0
            return
        else:
            day_demand=self.daily_demand
        firms_visited=set()
        for x in range(0,7):
            #new_firm = random.sample(self.typeA-firms_visited,1)[0]
            new_firm=random.choice(tuple(self.typeA-firms_visited))
            firms_visited.add(new_firm)
            goods_provided = self.model.schedule.firm_set[new_firm].get_inventory_available(day_demand)
            good_cost = self.model.schedule.firm_set[new_firm].current_price
            if(goods_provided*good_cost>=self.wealth):
                break
            if(goods_provided<day_demand):
                self.model.schedule.firm_set[new_firm].sell_inventory(goods_provided)
                day_demand-=goods_provided
                self.wealth-=(good_cost*goods_provided)
                self.model.total_household_wealth-=(good_cost*goods_provided)
                self.unfilled_demand_firms.append(new_firm)
                if(day_demand<(.05*self.daily_demand)):
                    break
            else:
                self.model.schedule.firm_set[new_firm].sell_inventory(day_demand)
                self.wealth-=(good_cost*goods_provided)
                self.model.total_household_wealth-=(good_cost*goods_provided)
                day_demand=0
                break

    def update_typeA_firms(self):
        if(random.randint(0,100) < 25):
            if(len(self.unfilled_demand_firms)>0):
                firm_to_remove=random.choice(self.unfilled_demand_firms)
                while(True):
                    firm_to_add=self.model.wr.random()
                    if(firm_to_add not in self.typeA):
                        break
                self.typeA.remove(firm_to_remove)
                self.typeA.add(firm_to_add)         
        if(random.randint(0,100) < 25):
            #firm_to_remove=random.sample((self.typeA),1)[0]
            firm_to_remove=random.choice(tuple(self.typeA))
            firm_to_add=0
            while(True):
                firm_to_add=self.model.wr.random()
                if(firm_to_add not in self.typeA):
                    break
            if(self.model.schedule.firm_set[firm_to_add].current_price<self.model.schedule.firm_set[firm_to_remove].current_price*.99):
                self.typeA.remove(firm_to_remove)
                self.typeA.add(firm_to_add)
        self.unfilled_demand_firms.clear()
        

    def update_wage_floor(self):
        if(self.employed):
            if(self.wage>self.floor_wage):
                self.floor_wage=self.wage
        else:
            self.floor_wage=self.floor_wage*.9

    def month_begin_step(self):
        #self.model.total_household_wealth=0
        self.calculate_demand()
        self.search_for_new_job()
        if(self.employed):
            self.model.employment_numbers+=1
        self.update_typeA_firms()
    
    def step(self):
        self.purchase_goods()

    def month_end_step(self):
        self.update_wage_floor()
        #self.model.total_household_wealth+=self.wealth
    

class FirmAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 3000
        self.typeB=set()
        self.wage=random.randint(500,800)
        #self.wage=1000
        self.is_hiring=False
        self.is_firing=False
        self.months_full_employment=0
        self.current_inv=0
        self.top_inv=100
        self.bot_inv=10
        self.current_price=random.randint(15,20)
        self.top_price=0
        self.bot_price=0
        self.prior_demand=10
        self.buffer=0
        self.model.firm_employment[self.unique_id]=0



    def get_inventory_available(self, num):
        self.prior_demand+=num
        if(num<=self.current_inv):
            return num
        else:
            num=self.current_inv
            return num

    def sell_inventory(self,num):
        if(num<=self.current_inv):
            self.current_inv-=num
            self.wealth+=(num*self.current_price)
        else:
            num=self.current_inv
            self.current_inv=0
            self.wealth+=(num*self.current_price)

    def produce_inventory(self):
        self.current_inv+=(2*len(self.typeB))

    def compute_inventory(self):
        self.top_inv=self.prior_demand
        self.bot_inv=self.prior_demand*.25
        self.prior_demand=0
  
    def hire_emp(self, emp_id):
        self.typeB.add(emp_id)
        self.is_hiring=False
        #self.months_full_employment+=1
        self.model.firm_employment[self.unique_id]+=1

    def change_price(self):
        if random.randint(0,100) < 75:
            price_rate_change=random.uniform(0,.02)
            marg_cost=self.wage/2
            self.top_price=marg_cost*1.15
            self.bot_price=marg_cost*1.025
            if(self.current_inv<self.bot_inv):
                if(self.current_price<self.top_price):
                    self.current_price=self.current_price*(1+price_rate_change)
            elif(self.current_inv>self.top_inv):
                if(self.current_price>self.bot_price):
                    self.current_price=self.current_price*(1-price_rate_change)

    def change_wage(self):
        self.months_full_employment+=1
        wage_rate_change=random.uniform(0,.019)
        if(self.is_hiring):
            self.wage=self.wage*(1+wage_rate_change)
            self.months_full_employment=0
        if (self.months_full_employment>24):
            self.wage=self.wage*(1-wage_rate_change)

    def change_employment(self):
        if(self.current_inv<self.bot_inv): 
            self.is_hiring=True
        elif(self.current_inv>self.top_inv):
            self.is_firing=True

    def fire_employee(self):
        #emp_id=random.sample((self.typeB),1)[0]
        if(len(self.typeB)>0):
            emp_id=random.choice(tuple(self.typeB))
            self.typeB.remove(emp_id)
            self.model.schedule.consumer_set[emp_id].get_fired()
            self.model.firm_employment[self.unique_id]-=1
        self.is_firing=False

    def pay_wages(self):
        total_wages=(self.wage*len(self.typeB))
        print("Firm "+str(self.unique_id)+"-- Wages Paid: "+str(total_wages))
        if(total_wages>self.wealth+self.buffer):
            if(len(self.typeB)>0):
                self.wage=((self.wealth+self.buffer)/len(self.typeB))
        for consumer in self.typeB:
            self.model.schedule.consumer_set[consumer].wage=self.wage
            self.model.schedule.consumer_set[consumer].wealth+=self.wage
            self.model.total_household_wealth+=self.wage
            if(self.wealth-self.wage<0):
                self.wealth=self.buffer+self.wealth
                self.buffer=0
                self.wealth-=self.wage
            else:
                self.wealth-=self.wage
            
    def distribute_profits(self):
        self.wealth+=self.buffer
        self.buffer=0
        profits_minus_buffer=self.wealth*.9
        self.buffer+=self.wealth*.1
        self.wealth-=self.buffer
        for x in self.model.schedule.consumer_set:
            self.model.schedule.consumer_set[x].wealth+=((self.model.schedule.consumer_set[x].wealth/self.model.total_household_wealth)*profits_minus_buffer)
            self.model.schedule.consumer_set[x].wealth+=((1/100)*self.wealth)
        self.wealth-=profits_minus_buffer
        self.model.total_household_wealth+=profits_minus_buffer

    def month_begin_step(self):
        #print("Current Inventory: "+str(self.current_inv)+" Prior Demand: "+str(self.prior_demand))
        self.compute_inventory()
        if(self.is_firing):
            self.fire_employee()
        self.change_wage()
        self.change_employment()
        self.change_price()
        

    def step(self):
        #self.change_wage()
        #print(self.model.firm_employment)
        self.produce_inventory()

    def month_end_step(self):
        self.pay_wages()
        self.distribute_profits()
