from enum import Enum

class DoorPosition(Enum):
    VERTICAL = 0
    HORIZONTAL = 1

class Door:
    def __init__(self, ajar=True, position=DoorPosition.VERTICAL):
        self.ajar = ajar
        self.position = position

    def open_door(self, tile):
        self.ajar = True
        if self.position == DoorPosition.VERTICAL:
            self.owner.char = '-'
        if self.position == DoorPosition.HORIZONTAL:
            self.owner.char = '|'
        self.owner.blocks = False
        tile.block_sight = False

    def close_door(self, tile):
        self.ajar = False
        self.owner.char = "+"
        self.owner.blocks = True
        tile.block_sight = True
