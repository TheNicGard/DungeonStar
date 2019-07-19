import tcod as libtcod

class Animation:
    def __init__(self, cycle_char=['X'], cycle_color=[libtcod.white]):
        self.char_frame = 0
        self.color_frame = 0
        self.cycle_char = cycle_char
        self.cycle_color = cycle_color

    def tick(self):
        if self.char_frame < len(cycle_char):
            self.char_frame += 1
        else:
            self.char_frame = 0

        if self.color_frame < len(cycle_color):
            self.color_frame += 1
        else:
            self.color_frame = 0

    def get_char(self):
        return self.cycle_char[self.char_frame]

    def get_color(self):
        return self.cycle_color[self.color_frame]
