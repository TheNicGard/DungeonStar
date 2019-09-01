import tcod as libtcod
from item_functions import poison, stuck
from game_messages import Message
from random import randint
from rpg_mechanics import attack_success, die, get_modifier

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

def spike_trap(target, **kwargs):
    results = []
    
    damage_taken = die(1, 4)
    if not target.ai:
        results.append({"message": Message(
            'You step on a trap of hidden spikes, taking {0} points of damage!'.format(
                damage_taken), libtcod.yellow)})
    results.extend(target.fighter.take_damage(damage_taken))

    return results

def poison_trap(target, **kwargs):
    results = []
    
    damage_taken = 1
    if not target.ai:
        results.append({"message": Message(
            'You step on a trap of hidden poisoned spikes, taking {0} point of damage!'.format(
                damage_taken), libtcod.yellow)})
    results.extend(target.fighter.take_damage(damage_taken))
        
    results.extend(poison(target, **{"turns": 50}))
    
    return results

def teleport_trap(target, **kwargs):
    results = []

    entities = kwargs.get('entities')
    game_map = kwargs.get('game_map')

    results = []

    while True:
        x = randint(0, game_map.width - 1)
        y = randint(0, game_map.height - 1)

        if not game_map.is_blocked(x, y) and not any([entity for entity in entities if entity.x == x and entity.y == y]):
            target.x = x
            target.y = y
            if not target.ai:
                results.append({'message': Message('You teleported!', libtcod.purple)})
            break

    return results

def hole_trap(target, **kwargs):
    results = []

    results.append({'consumed': True, "downwards_exit": True})

    return results

def bear_trap(target, **kwargs):
    results = []

    fov_map = kwargs.get('fov_map')
    
    damage_taken = die(1, 6)
    if not target.ai:
        results.append({"message": Message(
            'You step into a bear trap, taking {0} points of damage!'.format(
                damage_taken), libtcod.yellow)})
    elif libtcod.map_is_in_fov(fov_map, target.x, target.y):
        results.append({"message": Message(
            '{0} stepped into a bear trap!'.format(
                target.name.capitalize(), damage_taken), libtcod.white)})
    results.extend(target.fighter.take_damage(damage_taken))

    turns_remaining = max(max(0, randint(20, 30) - target.fighter.dexterity), 1)
    
    results.extend(stuck(target, **{"turns": turns_remaining}))

    return results
