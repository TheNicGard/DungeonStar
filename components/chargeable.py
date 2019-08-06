
class Chargeable:
    def __init__(self, charge, max_charge, times_recharged=0):
        self.charge = charge
        self.max_charge = max_charge
        self.times_recharged = times_recharged

    def recharge(self, additional_charge):
        self.charge += additional_charge

        if self.charge > self.max_charge:
            self.charge = self.max_charge
        
