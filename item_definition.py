from entity import Entity
from render_functions import RenderOrder

class ItemDefinition:
    def __init__(self, id, char, color, name, weight=0, item_component=None, equippable=None, spawn_rate=[[0, 0]]):
        self.id = id
        self.char = char
        self.color = color
        self.name = name
        self.item_component = item_component
        self.equippable = equippable
        self.weight = weight
        self.spawn_rate = spawn_rate

    def get_item(self, x, y):
        item = Entity(self.id, x, y, self.char, self.color, self.name, weight=self.weight,
                      blocks=False, render_order=RenderOrder.ITEM,
                      item=self.item_component, equippable=self.equippable)
        return item
