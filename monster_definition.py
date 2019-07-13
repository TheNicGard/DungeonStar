from components.fighter import Fighter
from render_functions import RenderOrder

class MonsterDefinition:
    def __init__(self, char, color, name, fighter, ai, spawn_rate=[[0, 0]]):
        self.char = char
        self.color = color
        self.name = name
        self.fighter = fighter
        self.ai = ai
        self.spawn_rate = spawn_rate

    def get_monster(self, x, y):
        return Entity(x, y, self.char, self.color, self.name,
                      blocks=True, render_order=RenderOrder.ACTOR,
                      fighter=self.fighter, ai=self.ai)

    def get_rate(self):
        return self.spawn_rate
