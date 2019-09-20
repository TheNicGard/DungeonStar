import tcod as libtcod
from game_messages import Message

class LightSource:
    def __init__(self, light, max_duration, duration=0, permanent=False, enchantment=0):
        self.light = light
        self.max_duration = max_duration
        self.duration = duration
        self.permanent = permanent
        self.enchantment = enchantment

        self.lit = False

    @property
    def get_light(self):
        if self.lit and (self.duration > 0  or self.permanent):
            return self.light + self.enchantment
        else:
            return 0

    def tick(self, message_log, in_inventory):
        if self.lit and self.duration > 0 and not self.permanent:
            self.duration -= 1
            if self.duration <= 0:
                if in_inventory and self.lit and self.owner and self.owner.owner:
                    message_log.add_message(Message("The {0} went out!".format(self.owner.owner.get_name), libtcod.yellow))
                self.lit = False
                

    @property
    def get_char(self):
        if self.get_light > 0:
            return 254
        else:
            return 255
