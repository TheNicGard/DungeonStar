from entity import Entity
from render_functions import RenderOrder

class ItemDefinition:
    def __init__(self, char, color, name, item_component=None, spawn_rate=[[0, 0]]):
        self.char = char
        self.color = color
        self.name = name
        self.item_component = item_component
        self.spawn_rate = spawn_rate

    def get_item(self, x, y):
        item = Entity(x, y, self.char, self.color, self.name,
                      blocks=False, render_order=RenderOrder.ITEM,
                      item=self.item_component)
        return item
