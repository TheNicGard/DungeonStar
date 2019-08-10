from random import choice
from rpg_mechanics import die

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

    def get_effects(self):
        effects = {}
        for k, v in self.slots.items():
            if v and v.equippable and v.equippable.get_effects() is not None:
                effects.update(v.equippable.get_effects())
        return effects

    def make_attack(self):
        damage = 0

        if self.slots.get("main_hand") is None and self.slots.get("off_hand") is None:
            damage = die(1, 3)
        elif hasattr(self.owner, "attack_list"):
            attack = choice(self.owner.attack_list)
            damage = die(attack.count, attack.side_count) + attack.enchantment
        else:
            if self.slots.get("main_hand") and self.slots.get("main_hand").equippable:
                damage += die(self.slots.get("main_hand").equippable.hit_dice[0],
                              self.slots.get("main_hand").equippable.hit_dice[1])
                damage += self.slots.get("main_hand").equippable.enchantment
            if self.slots.get("off_hand") and self.slots.get("off_hand").equippable:
                damage += die(self.slots.get("off_hand").equippable.hit_dice[0],
                              self.slots.get("off_hand").equippable.hit_dice[1])
                damage += self.slots.get("off_hand").equippable.enchantment
        return damage

    @property
    def armor_bonus(self):
        bonus = 0

        for slot in self.slots.values():
            if slot and slot.equippable and slot.equippable.armor_bonus != 0:
                bonus += slot.equippable.armor_bonus + slot.equippable.enchantment

        return bonus

    def toggle_equip(self, equippable_entity):
        results = []

        # unequip item
        if equippable_entity in self.slots.values():
            for slot_name, slot_item in self.slots.items():
                if equippable_entity == slot_item:
                    self.slots[slot_name] = None
                    results.append({'unequipped': slot_item})
                    break
        else:
            for slot_name, slot_item in self.slots.items():
                # equip item
                if equippable_entity.equippable.slot == slot_name:
                    results.append({'unequipped': slot_item})
                
                    if equippable_entity.equippable.slot == "left_finger" and self.slots["left_finger"] is not None and self.slots["right_finger"] is None:
                        self.slots["right_finger"] = equippable_entity
                        results.append({'equipped': equippable_entity})
                    elif equippable_entity.equippable.slot == "right_finger" and self.slots["right_finger"] is not None and self.slots["left_finger"] is None:
                        self.slots["left_finger"] = equippable_entity
                        results.append({'equipped': equippable_entity})
                    else:
                        self.slots[slot_name] = equippable_entity
                        results.append({'equipped': equippable_entity})
                    break
        
        return results

    def is_equipped(self, equippable_entity):
        for k, s in self.slots.items():
            if s is equippable_entity:
                return True
        return False
