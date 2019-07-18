class Equippable:
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

    def __str__(self):
        temp_str = "This item can be equipped to \"" + self.slot
        temp_str += "\" and has the following bonuses: power: " + str(self.power_bonus)
        temp_str += ", defense: " + str(self.defense_bonus)
        temp_str += ", max HP: " + str(self.max_hp_bonus)
        return temp_str
