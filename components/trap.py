import tcod as libtcod
from game_messages import Message
from rpg_mechanics import die

class Trap:
    def __init__(self, trap_function=None, revealed=False):
        self.revealed = revealed
        self.damage = [1, 4]
        self.trap_function = trap_function
        if self.trap_function == None:
            self.trap_function = spike_trap

    def set_reveal(self, reveal):
        if reveal:
            if self.owner:
                self.owner.char = "^"
            self.revealed = True
        else:
            if self.owner:
                self.owner.char = " "
            self.revealed = False

def spike_trap(target):
    results = []
    
    damage_taken = die(1, 4)
    results.append({"message": Message(
        'You step on a trap of hidden spikes, taking {0} points of damage!'.format(
        damage_taken), libtcod.yellow)})
    results.extend(target.fighter.take_damage(damage_taken))

    return results
