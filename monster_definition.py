from entity import Entity
from render_functions import RenderOrder

class MonsterDefinition:
    def __init__(self, id, char, color, name, weight=0, fighter=None, ai=None, spawn_rate=[[0, 0]]):
        self.id = id
        self.char = char
        self.color = color
        self.name = name
        self.fighter = fighter
        self.ai = ai
        self.weight = weight
        self.spawn_rate = spawn_rate

    def get_monster(self, x, y):
        monster = Entity(self.id, x, y, self.char, self.color, self.name, weight=self.weight,
                         blocks=True, render_order=RenderOrder.ACTOR,
                         fighter=self.fighter, ai=self.ai)
        return monster
