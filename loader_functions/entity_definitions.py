import copy
import json
import os

import tcod as libtcod
from components.ai import BasicMonster, AggressiveMonster, DummyMonster, ConfusedMonster, SoftStoppedMonster, HardStoppedMonster, MotherDoughAI, SourdoughAI, StaticMonster, NeutralMonster
from components.animation import Animation
from components.attacks import Attack
from components.chargeable import Chargeable
from components.equippable import Equippable
from components.fighter import Fighter
from components.food import Food
from components.inventory import Inventory
from components.item import Item
from entity import Entity
from game_messages import Message
from item_functions import heal, invisible, cast_lightning, cast_fireball, cast_confuse, cast_stun, cast_sleep, cast_greed, cast_detect_traps, cast_random_teleportation, cast_blink, cast_detect_stairs, cast_pacify, cast_force_bolt
from random import random, randint
from render_functions import RenderOrder

monster_definitions = "assets/monster_definitions.json"
item_definitions = "assets/item_definitions.json"

class ItemDefinition:
    def __init__(self, id, char, color, name, weight=0, item_component=None,
                 equippable=None, food=None, animation=None, spawn_rate=[[0, 0]],
                 classification=[]):
        self.id = id
        self.char = char
        self.color = color
        self.name = name
        self.item_component = item_component
        self.equippable = equippable
        self.weight = weight
        self.animation = animation
        self.food = food
        self.spawn_rate = spawn_rate
        self.classification = classification

    def get_item(self, x, y, count=1):
        if count > 1:
            self.item_component.count = count

        item = Entity(self.id, x, y, self.char, self.color, self.name, weight=self.weight,
                      blocks=False, render_order=RenderOrder.ITEM,
                      item=self.item_component, equippable=self.equippable, animation=self.animation,
                      food=self.food, classification=self.classification)
        return item

def get_ai(ai_type, patience=0, min_spread_time=0, max_spread_time=0, aggressive_ai="DummyMonster"):
    if ai_type == "BasicMonster":
        ai_component = BasicMonster()
    elif ai_type == "ConfusedMonster":
        ai_component = ConfusedMonster(BasicMonster(), 10)
    elif ai_type == "AggressiveMonster":
        ai_component = AggressiveMonster(patience)
    elif ai_type == "HardStoppedMonster":
        ai_component = HardStoppedMonster(BasicMonster())
    elif ai_type == "SoftStoppedMonster":
        ai_component = SoftStoppedMonster(BasicMonster())
    elif ai_type == "StaticMonster":
        ai_component = StaticMonster()
    elif ai_type == "MotherDoughAI":
        ai_component = MotherDoughAI()
    elif ai_type == "SourdoughAI":
        if min_spread_time == 0 and max_spread_time == 0:
            ai_component = SourdoughAI(40, 40)
        else:
            ai_component = SourdoughAI(min_spread_time, max_spread_time)
    elif ai_type == "NeutralMonster":
        ai_component = NeutralMonster(get_ai(aggressive_ai, patience, min_spread_time, max_spread_time, aggressive_ai))
    else:
        ai_component = DummyMonster()
    return ai_component
    
class MonsterDefinition:
    def __init__(self, id, char, color, name, weight=0, fighter=None, ai=None, inventory=None, spawn_rate=[[0, 0]]):
        self.id = id
        self.char = char
        self.color = color
        self.name = name
        self.fighter = fighter
        self.ai = ai
        self.weight = weight
        self.spawn_rate = spawn_rate
        self.inventory = inventory

    def get_monster(self, x, y):
        monster = Entity(self.id, x, y, self.char, self.color, self.name, weight=self.weight,
                         blocks=True, render_order=RenderOrder.ACTOR,
                         fighter=self.fighter, ai=self.ai, inventory=self.inventory)
        return monster

def load_monsters():
    if not os.path.isfile(monster_definitions):
        raise FileNotFoundError

    monster_defs = {}

    with open(monster_definitions, "r") as json_file:
        data = json.load(json_file)
        for monster in data:
            monster_id = monster.get("monster_id")
            name = monster.get("name")
            char = monster.get("symbol")
            if isinstance(char, int):
                char = chr(char)
            color = monster.get("color")
            fighter = monster.get("fighter")
            ai_type = monster.get("ai")
            spawn_rate = monster.get("spawn_rate")
            
            if (monster_id and name and char and isinstance(color, list) and fighter and isinstance(spawn_rate, list) and len(spawn_rate) > 0):
                hp = fighter.get("hp")
                
                strength = fighter.get("STR")
                dexterity = fighter.get("DEX")
                constitution = fighter.get("CON")
                intelligence = fighter.get("INT")
                wisdom = fighter.get("WIS")
                charisma = fighter.get("CHA")
                determination = fighter.get("DET")

                xp = 0
                if fighter.get("xp"):
                    xp = fighter.get("xp")
                    
                golden = False
                if fighter.get("golden"):
                    golden = fighter.get("golden")
                    
                max_gold_drop = 0
                if fighter.get("max_gold_drop"):
                    max_gold_drop = fighter.get("max_gold_drop")

                ai_details = monster.get("ai_details")
                patience = 0
                min_spread_time = 0
                max_spread_time = 0
                aggressive_ai = "DummyMonster"
                can_be_pacified = False
                
                if ai_details:
                    if ai_details.get("patience"):
                        patience = ai_details.get("patience")
                    if ai_details.get("min_spread_time"):
                        min_spread_time = ai_details.get("min_spread_time")
                    if ai_details.get("max_spread_time"):
                        max_spread_time = ai_details.get("max_spread_time")
                    if ai_details.get("aggressive_ai"):
                        aggressive_ai = ai_details.get("aggressive_ai")
                    if ai_details.get("can_be_pacified"):
                        can_be_pacified = ai_details.get("can_be_pacified")

                inventory_component = None
                if monster.get("inventory"):
                    inventory = monster.get("inventory")
                    inventory_component = Inventory(500)
                    for key, value in inventory.items():
                        # accomodate for weights greater than 1
                        if random() < value:
                            inventory_component.add_item(get_item(key, -1, -1))

                ai_component = get_ai(ai_type, patience, min_spread_time, max_spread_time, aggressive_ai)

                attack_list = None
                if fighter.get("attacks"):
                    attack_list = []
                    for a in fighter.get("attacks"):
                        attack_list.append(Attack(a[0], a[1], a[2]))

                if all (v is not None for v in [strength, dexterity, constitution, intelligence, wisdom, charisma, determination]):
                    chance_to_drop = 0.25
                    fighter_component = Fighter(strength, dexterity, constitution, intelligence,
                                                wisdom, charisma, determination, fixed_max_hp=hp, xp=xp,
                                                golden=golden, chance_to_drop_corpse=chance_to_drop,
                                                max_gold_drop=max_gold_drop, attack_list=attack_list,
                                                can_be_pacified=can_be_pacified)
                    
                    monster = MonsterDefinition(monster_id, char, color, name, weight=0, fighter=fighter_component, ai=ai_component, inventory=inventory_component, spawn_rate=spawn_rate)
                    
                    monster_defs[monster_id] = monster
                    
    return monster_defs

def load_items():
    if not os.path.isfile(item_definitions):
        raise FileNotFoundError

    item_function_names = [
        heal, cast_fireball, cast_lightning,
        cast_confuse, cast_stun, cast_sleep,
        cast_greed, invisible, cast_detect_traps,
        cast_random_teleportation, cast_blink,
        cast_detect_stairs, cast_pacify,
        cast_force_bolt
    ]

    equipment_types = [
        "main_hand", "off_hand", "head",
        "under_torso", "over_torso", "legs",
        "feet", "left_finger", "right_finger"
    ]
    
    item_defs = {}

    with open(item_definitions, "r") as json_file:
        data = json.load(json_file)
        for item in data:
            item_id = item.get("item_id")
            name = item.get("name")
            char = item.get("symbol")
            color = item.get("color")
            weight = item.get("weight")
            spawn_rate = item.get("spawn_rate")
            
            classification = []
            for c in item.get("classification"):
                classification.append(c)
            
            if item_id == "dungeon_star":
                equipment_component = Equippable("head", armor_bonus=1)
                animation_component = Animation(['['], [libtcod.white, libtcod.red,
                                                        libtcod.green, libtcod.blue], 0.333)
                
                item = ItemDefinition(item_id, char, color, name, weight=weight,
                                      equippable=equipment_component, animation=animation_component,
                                      spawn_rate=spawn_rate, classification=classification)
                item_defs[item_id] = item
                
            elif (item_id and name and char and weight and isinstance(color, list) and isinstance(spawn_rate, list) and len(spawn_rate) > 0):
                food_component = None
                if item.get("nutrition"):
                    food_component = Food(item.get("nutrition"))
                
                max_age = None
                if item.get("max_age"):
                    max_age = item.get("max_age")

                chargeable_component = None
                if item.get("max_charges"):
                    max_charge = item.get("max_charges")
                    chargeable_component = Chargeable(max_charge)
                    
                use_function = None
                use_function_name = item.get("use_function")                

                for f in item_function_names:
                    if f.__name__ == use_function_name:
                        use_function = f
                        break

                targeting = item.get("targeting")
                positional = item.get("positional")
                if positional and positional.get("targeting_message"):
                    message = positional.get("targeting_message").get("message")
                    message_color = positional.get("targeting_message").get("color")
                    positional["targeting_message"] = Message(message, message_color)

                equipment_component = None
                if item.get("equipment"):
                    slot = None
                    potential_slot = item.get("equipment").get("slot")
                    if potential_slot in equipment_types:
                        slot = potential_slot
                        
                    hit_dice = [0, 0]
                    if item.get("equipment").get("hit_dice_count") and item.get("equipment").get("hit_dice_side_count"):
                        count = item.get("equipment").get("hit_dice_count")
                        side_count = item.get("equipment").get("hit_dice_count")
                        hit_dice = [count, side_count]
                    
                    armor_bonus = 0
                    if item.get("equipment").get("armor_bonus"):
                        armor_bonus = item.get("equipment").get("armor_bonus")

                    if slot:
                        equipment_component = Equippable(slot, hit_dice=hit_dice,
                                                         armor_bonus=armor_bonus)

                item_component = None
                if positional or food_component:
                    item_component = Item(1, max_age=max_age, use_function=use_function,
                                          targeting=targeting, chargeable=chargeable_component, **positional)

                item = ItemDefinition(item_id, char, color, name, weight=weight, item_component=item_component, equippable=equipment_component, food=food_component, spawn_rate=spawn_rate)
                item_defs[item_id] = item
                    
    return item_defs

def get_item(item_choice, x, y, count=1):
    item = copy.deepcopy(item_defs.get(item_choice).get_item(x, y, count))
    if item.item.chargeable:
        item.item.chargeable.init_charge()
    return item

def get_monster(monster_choice, x, y):
    monster = copy.deepcopy(monster_defs.get(monster_choice).get_monster(x, y))
    if monster.ai and hasattr(monster.ai, 'reroll'):
        monster.ai.reroll()
    return monster

item_defs = load_items()
monster_defs = load_monsters()
