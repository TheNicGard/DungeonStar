from components.ai import BasicMonster, ConfusedMonster
import json
import os
import shelve

from components.fighter import Fighter
from monster_definition import MonsterDefinition

savegame_filename = "savegame.dat"
monster_definitions = "assets/monster_definitions.json"

def save_game(player, entities, game_map, message_log, game_state):
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

    with open(monster_definitions, "r") as json_file:
        data = json.load(json_file)
        for monster in data:
            monster_id = monster.get("monster_id")
            name = monster.get("name")
            char = monster.get("symbol")
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

                ai_component = BasicMonster()
                if ai_type == "ConfusedMonster":
                    ai_component = ConfusedMonster()
                    
                if hp is not None and defense is not None and power is not None:
                    fighter_component = Fighter(hp, defense, power, xp, golden, max_gold_drop)
                    
                    monster = MonsterDefinition(char, color, name, fighter=fighter_component, ai=ai_component, spawn_rate=spawn_rate)
                    monster_defs[monster_id] = monster

    return monster_defs
