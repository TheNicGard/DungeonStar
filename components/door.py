from enum import Enum

class DoorPosition(Enum):
    VERTICAL = 0
    HORIZONTAL = 1

class Door:
    def __init__(self, ajar=True, position=DoorPosition.VERTICAL):
        self.ajar = ajar
        self.position = position

    def open_door(self, tile_map):
        self.ajar = True
        if self.position == DoorPosition.VERTICAL:
            self.owner.char = '-'
        if self.position == DoorPosition.HORIZONTAL:
            self.owner.char = '|'
        self.owner.blocks = False
        tile_map[self.owner.x][self.owner.y].block_sight = False

    def close_door(self, tile_map):
        self.ajar = False
        self.owner.char = "+"
        self.owner.blocks = True
        tile_map[self.owner.x][self.owner.y].block_sight = True
