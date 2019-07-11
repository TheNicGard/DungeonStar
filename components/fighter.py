import tcod as libtcod

from components.valuable import Valuable
from entity import Entity
from game_messages import Message
from random import choice, randint
from render_functions import RenderOrder

class Fighter:
    def __init__(self, hp, defense, power, xp=0, golden=False, max_gold_drop=0):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp
        self.golden = golden
        self.max_gold_drop = max_gold_drop

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0
        return self.base_max_hp + bonus

    @property
    def power(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0
        return self.base_power + bonus

    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0
        return self.base_defense + bonus
            
    def take_damage(self, amount):
        results = []
        
        self.hp -= amount

        if self.hp <= 0:
            results.append({
                'dead': self.owner,
                'xp': self.xp,
                'gold_dropped': self.get_gold()
            })
            
        return results

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []
        
        damage = self.power - target.fighter.defense

        if damage > 0:
            target.fighter.take_damage(damage)
            results.append({
                'message': Message('{0} attacks {1} for {2} hit points.'.format(
                    self.owner.name.capitalize(), target.name, str(damage)),
                                   libtcod.white)})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({
                'message': Message('{0} attacks {1} but does no damage.'.format(
                    self.owner.name.capitalize(), target.name),
                libtcod.white)})
        return results

    def get_gold(self):
        initial_gold = randint(0, self.max_gold_drop)
        
        if self.golden:
            gold = initial_gold
        else:   
            gold = choice([0, 0, 0, initial_gold]) # 1/4 chance of gold drop

        if gold > 0:
            print("I generated {0} gold.".format(gold))
            valuable_component = Valuable(gold)
            gold_item = Entity(self.owner.x, self.owner.y, '$', libtcod.gold,
                               'Gold', render_order=RenderOrder.GOLD,
                               valuable=valuable_component)
            return gold_item
        else:
            return None
        

        

        
            
