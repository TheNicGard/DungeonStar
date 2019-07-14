import json
import os
import shelve

from components.ai import BasicMonster, ConfusedMonster, DummyMonster
from components.equipment import EquipmentSlots
from components.equippable import Equippable
from components.fighter import Fighter
from components.item import Item
from entity import Entity
from game_messages import Message
from item_definition import ItemDefinition
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from monster_definition import MonsterDefinition
from render_functions import RenderOrder

savegame_filename = "savegame.dat"
monster_definitions = "assets/monster_definitions.json"
item_definitions = "assets/item_definitions.json"

def save_game(player, entities, game_map, message_log, game_state):
    if not game_map.test_map:
        with shelve.open(savegame_filename, 'n') as data_file:
            data_file['player_index'] = entities.index(player)
            data_file['entities'] = entities
            data_file['game_map'] = game_map
            data_file['message_log'] = message_log
            data_file['game_state'] = game_state

def load_game():
    if not os.path.isfile(savegame_filename):
        raise FileNotFoundError

    with shelve.open(savegame_filename, 'r') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
        game_map = data_file['game_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']

    player = entities[player_index]
    return player, entities, game_map, message_log, game_state

def load_monsters():
    if not os.path.isfile(monster_definitions):
        raise FileNotFoundError

    monster_defs = {}
    spawn_rates = {}

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
                defense = fighter.get("defense")
                power = fighter.get("power")

                xp = 0
                if fighter.get("xp"):
                    xp = fighter.get("xp")
                    
                golden = False
                if fighter.get("golden"):
                    golden = fighter.get("golden")
                    
                max_gold_drop = 0
                if fighter.get("max_gold_drop"):
                    max_gold_drop = fighter.get("max_gold_drop")

                ai_component = DummyMonster()
                if ai_type == "BasicMonster":
                    ai_component = BasicMonster()
                elif ai_type == "ConfusedMonster":
                    ai_component = ConfusedMonster()
                    
                if hp is not None and defense is not None and power is not None:
                    fighter_component = Fighter(hp, defense, power, xp, golden, max_gold_drop)
                    
                    monster = MonsterDefinition(monster_id, char, color, name, weight=0, fighter=fighter_component, ai=ai_component, spawn_rate=spawn_rate)
                    monster_defs[monster_id] = monster
                    
    return monster_defs

def load_items():
    if not os.path.isfile(item_definitions):
        raise FileNotFoundError

    item_defs = {}
    spawn_rates = {}

    with open(item_definitions, "r") as json_file:
        data = json.load(json_file)
        for item in data:
            item_id = item.get("item_id")
            name = item.get("name")
            char = item.get("symbol")
            color = item.get("color")
            weight = item.get("weight")
            spawn_rate = item.get("spawn_rate")

            if (item_id and name and char and weight and isinstance(color, list) and isinstance(spawn_rate, list) and len(spawn_rate) > 0):
                use_function = None
                if item.get("use_function") == "heal":
                    use_function = heal
                if item.get("use_function") == "cast_fireball":
                    use_function = cast_fireball
                if item.get("use_function") == "cast_lightning":
                    use_function = cast_lightning
                if item.get("use_function") == "cast_confuse":
                    use_function = cast_confuse
                    
                targeting = item.get("targeting")
                positional = item.get("positional")
                if positional and positional.get("targeting_message"):
                    message = positional.get("targeting_message").get("message")
                    message_color = positional.get("targeting_message").get("color")
                    positional["targeting_message"] = Message(message, message_color)

                equipment_component = None
                if item.get("equipment"):
                    slot = None
                    if item.get("equipment").get("slot") == "main_hand":
                        slot = EquipmentSlots.MAIN_HAND
                    elif item.get("equipment").get("slot") == "off_hand":
                        slot = EquipmentSlots.OFF_HAND
                        
                    power_bonus = 0
                    if item.get("equipment").get("power_bonus"):
                        power_bonus = item.get("equipment").get("power_bonus")
                    
                    defense_bonus = 0
                    if item.get("equipment").get("defense_bonus"):
                        defense_bonus = item.get("equipment").get("defense_bonus")

                    if slot:
                        equipment_component = Equippable(slot, power_bonus=power_bonus, defense_bonus=defense_bonus)

                item_component = None
                if positional:
                    item_component = Item(1, use_function=use_function, targeting=targeting, **positional)

                item = ItemDefinition(item_id, char, color, name, weight=weight, item_component=item_component, equippable=equipment_component, spawn_rate=spawn_rate)
                item_defs[item_id] = item
                    
    return item_defs
