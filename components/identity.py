
class Identity:
    def __init__(self, name, color, identify_on_use):
        self.name = name
        self.color = color
        self.identified = False
        self.identify_on_use = identify_on_use

    def identify(self):
        self.identified = True
