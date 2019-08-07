import tcod as libtcod
from game_messages import Message

class Effect:
    def __init__(self, temporary, turns_remaining, turn_tick_function):
        self.temporary = temporary
        self.turns_remaining = turns_remaining
        self.turn_tick_function = turn_tick_function

    def tick(self):
        message = None
        
        if self.temporary:
            if self.turns_remaining > 0:
                self.turns_remaining -= 1
                message = self.turn_tick_function(self.turns_remaining)
                
        return message

def tick_invisible(turns_remaining):
    message = None
    
    if turns_remaining <= 0:
        message = Message("Color starts to reappear on your body!",
                          libtcod.yellow)        
    return message

