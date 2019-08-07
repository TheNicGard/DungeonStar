
class Effect:
    def __init__(self, temporary, turns_remaining, turn_tick_function):
        self.temporary = temporary
        self.turns_remianing = turns_remaining
        self.turn_tick_function = turn_ticK_function

    def tick(self):
        if self.temporary:
            if self.turns_remaining > 0:
                turns_remaining -= 1
                self.turn_tick_function(self.turns_remaining)                

def tick_invisible(self, turns_remaining):
    message = None
        
    if turns_remaining <= 0:
        message = Message("Color starts to reappear on your body!",
                          libtcod.yellow)
            
    return message

