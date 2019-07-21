
class Equipment:
    def __init__(self, slots={}):
        self.slots = slots

    def __str__(self):
        temp_str = ""
        
        for v, k in self.slots.items():
            if not k:
                temp_str += "Nothing is equipped to the \"" + v + "\". "
            else:
                temp_str += "Equipped to the \"" + v + "\" is a " + k.name + ". "
                
        return temp_str
                
    @property
    def max_hp_bonus(self):
        bonus = 0

        for slot in self.slots.values():
            if slot and slot.equippable:
                bonus += slot.equippable.max_hp_bonus

        return bonus

    @property
    def power_bonus(self):
        bonus = 0

        for slot in self.slots.values():
            if slot and slot.equippable:
                bonus += slot.equippable.power_bonus

        return bonus

    @property
    def defense_bonus(self):
        bonus = 0

        for slot in self.slots.values():
            if slot and slot.equippable:
                bonus += slot.equippable.defense_bonus

        return bonus

    def toggle_equip(self, equippable_entity):
        results = []

        for k, s in self.slots.items():
            # unequip item
            if s is equippable_entity:
                self.slots[k] = None
                results.append({'unequipped': s})
                break
            # equip item
            elif equippable_entity.equippable.slot == k:
                results.append({'unequipped': s})
                self.slots[k] = equippable_entity
                results.append({'equipped': equippable_entity})
                break
        
        return results

    def is_equipped(self, equippable_entity):
        for k, s in self.slots.items():
            if s is equippable_entity:
                return True
        return False
