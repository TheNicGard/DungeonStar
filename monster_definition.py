from components.ai import BasicMonster
from components.fighter import Fighter
from entity import Entity
from render_functions import RenderOrder

class MonsterDefinition:
    def __init__(self, char, color, name, fighter=None, ai=None, spawn_rate=[[0, 0]]):
        self.char = char
        self.color = color
        self.name = name
        self.fighter = fighter
        self.ai = ai
        self.spawn_rate = spawn_rate

    def get_monster(self, x, y):
        ai_component = BasicMonster()

        
        monster = Entity(x, y, self.char, self.color, self.name,
                         blocks=True, render_order=RenderOrder.ACTOR,
                         fighter=self.fighter, ai=self.ai)

        monster.ai = ai_component
        monster.ai.owner = monster

        return monster

    def get_rate(self):
        return self.spawn_rate
