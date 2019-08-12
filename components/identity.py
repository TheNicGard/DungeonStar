
class Identity:
    def __init__(self, name, char, color, identify_on_use):
        self.name = name
        self.char = char
        self.color = color
        self.identified = False
        self.identify_on_use = identify_on_use
