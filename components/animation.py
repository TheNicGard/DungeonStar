import datetime, time
import tcod as libtcod

class Animation:
    def __init__(self, cycle_char=['X'], cycle_color=[libtcod.white], speed=1):
        self.char_frame = 0
        self.color_frame = 0
        self.cycle_char = cycle_char
        self.cycle_color = cycle_color
        self.last_time = self.current_time
        self.speed = speed

    def tick(self):
        if self.current_time > self.last_time + self.speed:
            if self.char_frame < len(self.cycle_char) - 1:
                self.char_frame += 1
            else:
                self.char_frame = 0
                
            if self.color_frame < len(self.cycle_color) - 1:
                self.color_frame += 1
            else:
                self.color_frame = 0
                
            self.last_time = self.current_time
            
    def get_char(self):
        return self.cycle_char[self.char_frame]

    def get_color(self):
        return self.cycle_color[self.color_frame]

    @property
    # current time in seconds
    def current_time(self):
        t = datetime.datetime.now()
        return time.mktime(t.timetuple()) + (t.microsecond / 1000000)
