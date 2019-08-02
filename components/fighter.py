import tcod as libtcod

from components.valuable import Valuable
from entity import Entity
from game_messages import Message
from random import choice, randint
from render_functions import RenderOrder
from rpg_mechanics import attack_success, die, get_modifier

class Fighter:
    def __init__(self, strength, dexterity, constitution,
                 intelligence, wisdom, charisma, determination,
                 fixed_max_hp=None, xp=0, golden=False, chance_to_drop_corpse=0,
                 max_gold_drop=0, attack_list=None):
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma
        self.determination = determination
        
        self.fixed_max_hp = fixed_max_hp
        self.hp = self.max_hp
        self.attack_list = []
        self.proficiency = 2 #needs to scale with level

        # self.size = size, adjusts attack bonus
        
        self.xp = xp
        self.max_gold_drop = max_gold_drop
        self.status = {}
        self.status["golden"] = golden
        self.chance_to_drop_corpse = chance_to_drop_corpse
        self.attack_list = attack_list

    def __str__(self):
        return "... NYI ..."

    @property
    def max_hp(self):
        # for now the hit dice for any rogue will be 12, to be adjusted (?)
        if self.fixed_max_hp is not None:
            hp = self.fixed_max_hp
        else:
            hp = 12 + get_modifier(self.constitution)
        return hp

    @property
    def attack_bonus(self):
        return get_modifier(self.strength) + self.proficiency

    @property
    def armor_class(self):
        if self.owner and self.owner.equipment:
            return 10 + get_modifier(self.dexterity) + self.owner.equipment.armor_bonus
        else:
            return 10 + get_modifier(self.dexterity)

    def select_attack(self):
        return choice(self.attack_list)
            
    def take_damage(self, amount):
        results = []
        
        self.hp -= amount

        if self.hp <= 0:
            results.append({
                'dead': self.owner,
                'xp': self.xp
            })
            if self.owner.ai:
                results.append({
                    'enemy_gold_dropped': self.get_gold(),
                    'drop_inventory': self.owner.inventory
                })

        return results

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []

        success = attack_success(self.attack_bonus, target.fighter.armor_class)

        if success:
            damage = get_modifier(self.strength)
            if self.owner.equipment:
                equipment_damage = self.owner.equipment.make_attack()
                damage += equipment_damage
            elif len(self.attack_list) > 0:
                dice = self.select_attack()
                roll = die(dice.count, dice.side_count)
                damage += roll
            if damage <= 0:
                damage = 1

            results.append({
                'message': Message('{0} attacks {1} for {2} hit points.'.format(
                    self.owner.name.capitalize(), target.name, str(damage)),
                                   libtcod.white)})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({
                'message': Message('{0} attacks {1} but misses.'.format(
                    self.owner.name.capitalize(), target.name), libtcod.white)})
        return results

    def get_gold(self):
        initial_gold = randint(0, self.max_gold_drop)
        
        if self.status["golden"]:
            gold = initial_gold
            second_roll = randint(0, self.max_gold_drop)
            if second_roll > gold:
                gold = second_roll
        else:   
            gold = choice([0, 0, 0, initial_gold]) # 1/4 chance of gold drop

        if gold > 0:
            valuable_component = Valuable(gold)
            gold_item = Entity("gold", self.owner.x, self.owner.y, '$', libtcod.gold,
                               'Gold', render_order=RenderOrder.GOLD,
                               valuable=valuable_component)
            return gold_item
        else:
            return None

    def tick_invisibility(self):
        message = None
        
        if self.status.get("invisible") and self.status.get("invisible") > 0:
            self.status["invisible"] -= 1
            if self.status["invisible"] <= 0:
                message = Message("Color starts to reappear on your body!",
                                  libtcod.yellow)
                    
        return message
