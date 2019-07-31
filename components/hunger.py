from enum import Enum
from game_messages import Message
from random import choice

class HungerType(Enum):
    MOVE = 0
    EXERT = 1
    STATIC = 2

class Hunger:
    def __init__(self, saturation=4000, emaciated_saturation=200,
                 starving_saturation=1000, hungry_saturation=2000,
                 full_saturation=6000, maximum_saturation=8000,
                 movement_hunger=2, exertion_hunger=6, static_hunger=1):
        self.saturation = saturation
        self.starving_saturation = starving_saturation
        self.emaciated_saturation = emaciated_saturation
        self.hungry_saturation = hungry_saturation
        self.full_saturation = full_saturation
        self.maximum_saturation = maximum_saturation
        self.movement_hunger = movement_hunger
        self.exertion_hunger = exertion_hunger
        self.static_hunger = static_hunger

    def __str__(self):
        return "Saturation: {0} out of {1}".format(self.saturation, self.maximum_saturation)

    def eat(self, item):
        results = []

        if item and item.item is not None and item.food is not None:
            food_sat = item.food.nutrition
            if food_sat + self.saturation > self.maximum_saturation:
                results.append({
                'message': Message(
                    choice([
                        "You're stuffed!", "You couldn't eat another bite!",
                        "Any more food would give you a really bad tummy ache!"
                    ])
                )})
            else:
                results.append({"food_eaten": item})
                results.append({"message": Message("You eat the {0}!".format(item.name))})
                self.saturation += food_sat
                    
        return results

    def tick(self, hunger_type):
        results = []

        if hunger_type == HungerType.MOVE:
            self.saturation -= self.movement_hunger
        elif hunger_type == HungerType.EXERT:
            self.saturation -= self.exertion_hunger
        elif hunger_type == HungerType.STATIC:
            self.saturation -= self.static_hunger

        if self.saturation <= 0:
            results.append({"dead": self.owner})
        
        return results

    @property
    def status(self):
        if self.saturation > self.full_saturation:
            return "Full"
        elif self.saturation < self.emaciated_saturation:
            return "Emaciated"
        elif self.saturation < self.starving_saturation:
            return "Starving"
        elif self.saturation < self.hungry_saturation:
            return "Hungry"
        
        else:
            return None
