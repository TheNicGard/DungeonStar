from components.ai import BasicMonster
from components.fighter import Fighter
from entity import Entity
from render_functions import RenderOrder

class MonsterDefinition:
    def __init__(self, char, color, name, weight=0, fighter=None, ai=None, spawn_rate=[[0, 0]]):
        self.char = char
        self.color = color
        self.name = name
        self.fighter = fighter
        self.ai = ai
        self.weight = weight
        self.spawn_rate = spawn_rate

    def get_monster(self, x, y):
        monster = Entity(x, y, self.char, self.color, self.name, weight=self.weight,
                         blocks=True, render_order=RenderOrder.ACTOR,
                         fighter=self.fighter, ai=self.ai)
        return monster
