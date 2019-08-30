
class LightSource:
    def __init__(self, light, max_duration, duration=0, permanent=False):
        self.light = light
        self.max_duration = max_duration
        self.duration = duration
        self.permanent = permanent

        self.lit = False

    @property
    def get_light(self):
        if (self.duration > 0 and self.lit) or self.permanent:
            return self.light
        else:
            return 0

    def tick(self):
        if (self.lit and self.duration > 0) or self.permanent:
            self.duration -= 1
            if self.duration <= 0:
                self.lit = False

    @property
    def get_char(self):
        if self.get_light > 0:
            return 254
        else:
            return 255
