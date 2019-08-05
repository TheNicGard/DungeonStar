import csv
import json
import os
import shelve

import tcod as libtcod
from components.ai import BasicMonster, ConfusedMonster, DummyMonster, AggressiveMonster, HardStoppedMonster, SoftStoppedMonster, StaticMonster, MotherDoughAI, SourdoughAI
from components.animation import Animation
from components.equippable import Equippable
from components.fighter import Fighter
from components.food import Food
from components.inventory import Inventory
from components.item import Item
from entity import Entity
from game_messages import Message
from item_functions import heal, invisible, cast_lightning, cast_fireball, cast_confuse, cast_stun, cast_sleep, cast_greed
from render_functions import RenderOrder

savegame_filename = "savegame.dat"
test_map_filename = "assets/test_map.csv"
tutorial_map_filename = "assets/tutorial_map.csv"
high_scores_filename = "high_scores.dat"

def save_game(player, entities, game_map, message_log, game_state, turn):
    if not game_map.test_map:
        with shelve.open(savegame_filename, 'n') as data_file:
            data_file['player_index'] = entities.index(player)
            data_file['entities'] = entities
            data_file['game_map'] = game_map
            data_file['message_log'] = message_log
            data_file['game_state'] = game_state
            data_file['turn'] = turn

def load_game():
    if not os.path.isfile(savegame_filename):
        raise FileNotFoundError

    with shelve.open(savegame_filename, 'r') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
        game_map = data_file['game_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']
        turn = data_file['turn']

    player = entities[player_index]
    return player, entities, game_map, message_log, game_state, turn

def load_test_map_tiles():
    datafile = open(test_map_filename, 'r')
    datareader = csv.reader(datafile, delimiter='|')
    data = []
    for row in datareader:
        data.append(row)
    return data

def load_tutorial_map_tiles():
    datafile = open(tutorial_map_filename, 'r')
    datareader = csv.reader(datafile, delimiter='|')
    data = []
    for row in datareader:
        data.append(row)
    return data

def load_game_data():
    if not os.path.isfile(high_scores_filename):
        with shelve.open(high_scores_filename, 'n') as data_file:
            data_file['lowest_level'] = 1
            data_file['highest_score'] = 0
            data_file['stat_diffs'] = [0, 0, 0, 0, 0, 0]
            data_file['points_available'] = 27
            return 1, 0
    else:
        with shelve.open(high_scores_filename, 'r') as data_file:
            lowest_level = data_file['lowest_level']
            highest_score = data_file['highest_score']
            stat_diffs = data_file['stat_diffs']
            points_available = data_file['points_available']
            return lowest_level, highest_score, stat_diffs, points_available

def save_game_data(lowest_level, highest_score, stat_diffs, points_available):
    with shelve.open(high_scores_filename, 'n') as data_file:
        data_file['lowest_level'] = lowest_level
        data_file['highest_score'] = highest_score
        data_file['stat_diffs'] = stat_diffs
        data_file['points_available'] = points_available
