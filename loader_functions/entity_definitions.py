import copy
import json
import os

import tcod as libtcod
from components.ai import BasicMonster, AggressiveMonster, DummyMonster, ConfusedMonster, SoftStoppedMonster, HardStoppedMonster, MotherDoughAI, SourdoughAI, StaticMonster, NeutralMonster, IntelligentMonster
from components.animation import Animation
from components.attacks import Attack
from components.chargeable import Chargeable
from components.equippable import Equippable
from components.fighter import Fighter
from components.food import Food
from components.identity import Identity
from components.inventory import Inventory
from components.item import Item
from components.light_source import LightSource
from effect import Effect, effects_list
from entity import Entity
from game_messages import Message
from item_functions import heal, invisible, cast_lightning, cast_fireball, cast_confuse, cast_stun, cast_sleep, cast_greed, cast_detect_traps, cast_random_teleportation, cast_blink, cast_detect_stairs, cast_pacify, cast_force_bolt, poison, cure_poison, regeneration, cast_mapping, cast_identify_item, cast_charge_item, cast_detect_aura, cast_detect_items, cast_make_invisible, cast_death, cast_downwards_exit, amnesia, cast_enchant_item
from random import random, randint, choice
from render_functions import RenderOrder

monster_definitions = "assets/monster_definitions.json"
item_definitions = "assets/item_definitions.json"
identity_definitions = "assets/identity_definitions.json"

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
        new_item_component = copy.deepcopy(self.item_component)

        if count > 1:
            new_item_component.count = count
            
        item = Entity(self.id, x, y, self.char, self.color, self.name, weight=self.weight,
                      blocks=False, render_order=RenderOrder.ITEM,
                      item=new_item_component, equippable=self.equippable, animation=self.animation,
                      food=self.food, classification=self.classification)
        return item

def get_ai(ai_type, patience=0, min_spread_time=0, max_spread_time=0,
           health_threshold=0, safe_range=0, aggressive_ai="DummyMonster"):
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
    elif ai_type == "IntelligentMonster":
        ai_component = IntelligentMonster(patience, health_threshold, safe_range)
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
                    
                golden = None
                if fighter.get("golden"):
                    if fighter.get("golden"):
                        golden = Effect(False, -1, None)
                    
                max_gold_drop = 0
                if fighter.get("max_gold_drop"):
                    max_gold_drop = fighter.get("max_gold_drop")

                ai_details = monster.get("ai_details")
                patience = 0
                min_spread_time = 0
                max_spread_time = 0
                aggressive_ai = "DummyMonster"
                can_be_pacified = False
                health_threshold = 0
                safe_range = 0
                
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
                    if ai_details.get("health_threshold"):
                        health_threshold = ai_details.get("health_threshold")
                    if ai_details.get("saf_range"):
                        safe_range = ai_details.get("safe_range")

                inventory_component = None
                if monster.get("inventory"):
                    inventory = monster.get("inventory")
                    inventory_component = Inventory(500)
                    for key, value in inventory.items():
                        # accomodate for weights greater than 1
                        if random() < value:
                            inventory_component.add_item(get_item(key, -1, -1))

                ai_component = get_ai(ai_type, patience, min_spread_time, max_spread_time,
                                      health_threshold, safe_range, aggressive_ai)

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
        cast_confuse, cast_stun, cast_sleep, regeneration,
        cast_greed, invisible, cast_detect_traps,
        cast_random_teleportation, cast_blink,
        cast_detect_stairs, cast_pacify, cast_mapping,
        cast_force_bolt, poison, cure_poison, cast_identify_item,
        cast_charge_item, cast_detect_aura, cast_detect_items,
        cast_make_invisible, cast_death, cast_downwards_exit,
        amnesia, cast_enchant_item
    ]

    equipment_types = [
        "main_hand", "off_hand", "head",
        "under_torso", "over_torso", "legs",
        "feet", "left_finger", "right_finger"
    ]
    
    item_defs = {}
    item_identified_on_use = {}

    with open(item_definitions, "r") as json_file:
        data = json.load(json_file)
        for item in data:
            item_id = item.get("item_id")
            name = item.get("name")
            char = item.get("symbol")
            color = item.get("color")
            weight = item.get("weight")
            spawn_rate = item.get("spawn_rate")
            
            classification_list = []
            if item.get("classification"):
                classification_list = item.get("classification")
            
            if item_id == "dungeon_star":
                equipment_component = Equippable("head", armor_bonus=1)
                animation_component = Animation(['['], [libtcod.white, libtcod.red,
                                                        libtcod.green, libtcod.blue], 0.333)
                
                item = ItemDefinition(item_id, char, color, name, weight=weight,
                                      equippable=equipment_component, animation=animation_component,
                                      spawn_rate=spawn_rate, classification=classification_list)
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

                light_source_component = None
                if item.get("light_source") and item.get("positional"):
                    light_amount = item.get("positional").get("light_amount")
                    max_duration = item.get("positional").get("max_duration")
                    permanent_light = item.get("positional").get("permanent_light")

                    light_source_component = LightSource(light_amount, max_duration,
                                                         duration=max_duration,
                                                         permanent=permanent_light)
                    
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

                    effects = {}
                    if item.get("equipment").get("effect"):
                        ef = item.get("equipment").get("effect")

                        if ef in effects_list:
                            effects[ef] = Effect(False, 0, None)
                        
                    if slot:
                        equipment_component = Equippable(slot, hit_dice=hit_dice,
                                                         armor_bonus=armor_bonus)
                        equipment_component.effects = effects

                item_component = None
                if positional or food_component or light_source_component:
                    item_component = Item(1, max_age=max_age, use_function=use_function,
                                          targeting=targeting, chargeable=chargeable_component, light_source=light_source_component, **positional)
                if light_source_component is not None:
                    light_source_component.owner = item_component

                item_defs[item_id] = ItemDefinition(item_id, char, color, name, weight=weight,
                                                    item_component=item_component, equippable=equipment_component,
                                                    food=food_component, spawn_rate=spawn_rate, classification=classification_list)
                    
        return item_defs

def load_identities():
    if not os.path.isfile(identity_definitions):
        raise FileNotFoundError
    
    identity_defs = {"potion": [], "scroll": [], "wand": [], "ring": []}

    with open(identity_definitions, "r") as json_file:
        data = json.load(json_file)
        
        potion_defs = data.get("potion")
        for i in potion_defs:
            name = i.get("name")
            color = i.get("color")
            if name and color:
                identity_defs["potion"].append(Identity(name, color, True))
            
        scroll_defs = data.get("scroll")
        for i in scroll_defs:
            name = i.get("name")
            color = i.get("color")
            if name and color:
                identity_defs["scroll"].append(Identity(name, color, True))

        wand_defs = data.get("wand")    
        for i in wand_defs:
            name = i.get("name")
            color = i.get("color")
            if name and color:
                identity_defs["wand"].append(Identity(name, color, True))
            
        ring_defs = data.get("ring")
        for i in ring_defs:
            name = i.get("name")
            color = i.get("color")
            if name and color:
                identity_defs["ring"].append(Identity(name, color, True))
                
    return identity_defs

def associate_identities():
    for t in ["potion", "scroll", "ring", "wand"]:
        item_ids[t] = [i.id for i in item_defs.values() if (t in i.classification)]
        for i in range(0, len(item_ids[t])):
            tentative_choice = choice(identities[t])
            while True:
                if not tentative_choice in identity_associations[t]:
                    identity_associations[t].append(tentative_choice)
                    break
                else:
                    tentative_choice = choice(identities[t])

def get_identity(item):
    if "potion" in item.classification:
        return identity_associations["potion"][item_ids["potion"].index(item.id)]
    elif "scroll" in item.classification:
        return identity_associations["scroll"][item_ids["scroll"].index(item.id)]
    elif "ring" in item.classification:
        return identity_associations["ring"][item_ids["ring"].index(item.id)]
    elif "wand" in item.classification:
        return identity_associations["wand"][item_ids["wand"].index(item.id)]

def get_item(item_choice, x, y, count=1):
    item = copy.deepcopy(item_defs.get(item_choice).get_item(x, y, count))
    if item.item.chargeable:
        item.item.chargeable.init_charge()
    item.identity = get_identity(item)
    return item

def get_monster(monster_choice, x, y):
    monster = copy.deepcopy(monster_defs.get(monster_choice).get_monster(x, y))
    if monster.ai and hasattr(monster.ai, 'reroll'):
        monster.ai.reroll()
    return monster

item_defs = load_items()
monster_defs = load_monsters()

item_ids = {"potion": [], "scroll": [], "ring": [], "wand": []}
identity_associations = {"potion": [], "scroll": [], "ring": [], "wand": []}

identities = load_identities()
associate_identities()

