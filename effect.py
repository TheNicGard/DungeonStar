import tcod as libtcod
from game_messages import Message

effects_list = ["poison_resistance", "strength_boost",
                "dexterity_boost", "constitution_boost",
                "intelligence_boost", "wisdom_boost",
                "charisma_boost", "see_invisible",
                "slow_digestion", "fast_digestion",
                "dowsing"]

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

    def is_active(self):
        return not self.temporary or self.turns_remaining > 0
        
    def tick(self):
        results = []
        
        if self.temporary:
            if self.turns_remaining > 0:
                self.turns_remaining -= 1
                results.extend(self.turn_tick_function(self.turns_remaining))
                
        return results

def tick_invisible(turns_remaining):
    results = []
    
    results.append({"invisible": turns_remaining})
        
    return results

def tick_poison(turns_remaining):
    results = []
    
    if turns_remaining > 0:
        results.append({"poison_damage": str(turns_remaining)})        
        
    return results

def tick_stuck(turns_remaining):
    results = []

    results.append({"stuck": turns_remaining})
        
    return results

def tick_regeneration(turns_remaining):
    results = []
    
    if turns_remaining > 0:
        results.append({"regeneration": str(turns_remaining)})        
        
    return results

def tick_detect_aura(turns_remaining):
    return []

def tick_detect_items(turns_remaining):
    return []
