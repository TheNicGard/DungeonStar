from random import randint

class Chargeable:
    def __init__(self, max_charge, charge=0, times_recharged=0):
        self.charge = charge
        self.max_charge = max_charge
        self.times_recharged = times_recharged

    def init_charge(self):
        self.charge = randint(self.max_charge / 2, self.max_charge)

    def recharge(self, additional_charge):
        self.charge += additional_charge

        if self.charge > self.max_charge:
            self.charge = self.max_charge
        
