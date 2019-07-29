class Equippable:
    def __init__(self, slot, hit_dice=[0, 0], armor_bonus=0):
        self.slot = slot
        self.hit_dice = hit_dice 
        self.armor_bonus = armor_bonus

    def __str__(self):
        temp_str = "This item can be equipped to \"" + self.slot
        temp_str += "\" and has the following properties: dice: "
        temp_str += str(hit_dice[0]) + "d" + str(hit_dice[1])
        temp_str += ", armor bonus: " + str(self.armor_bonus)
        return temp_str
