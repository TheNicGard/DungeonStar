import tcod as libtcod
from game_messages import Message

class EffectGroup:
    def __init__(self):
        self.effects = {}

    def get(self, key):
        return self.effects.get(key)

    def tick(self):
        results = []

        for e in self.effects.values():
            if e and e.temporary:
                results.extend(e.tick())

        return results

class Effect:
    def __init__(self, temporary, turns_remaining, turn_tick_function):
        self.temporary = temporary
        self.turns_remaining = turns_remaining
        self.turn_tick_function = turn_tick_function

    def tick(self):
        results = []
        
        if self.temporary:
            if self.turns_remaining > 0:
                self.turns_remaining -= 1
                results.extend(self.turn_tick_function(self.turns_remaining))
                
        return results

def tick_invisible(turns_remaining):
    results = []
    
    if turns_remaining <= 0:
        results.append({"message": Message("Color starts to reappear on your body!",
                          libtcod.yellow)})
    return results

def tick_poison(turns_remaining):
    results = []
    
    if turns_remaining > 0:
        results.append({"poison_damage": str(turns_remaining)})        
        
    return results

