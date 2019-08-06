
class Trap:
    def __init__(self, revealed=False):
        self.revealed = revealed
        self.damage = [1, 4] #d20 combat NYI
        # update later to include different trap types

    def set_reveal(self, reveal):
        if reveal:
            if self.owner:
                self.owner.char = "^"
            self.revealed = True
        else:
            if self.owner:
                self.owner.char = " "
            self.revealed = False
