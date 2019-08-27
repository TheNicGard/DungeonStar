import csv
import os
import shelve

from game_container import GameContainer

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

def delete_game():
    if os.path.isfile(savegame_filename):
        os.remove(savegame_filename)

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
            data_file['high_score'] = 0
            data_file['stat_diffs'] = [0, 0, 0, 0, 0, 0]
            data_file['points_available'] = 27
            return GameContainer(lowest_level=1, high_score=0,
                                 stat_diffs=[0, 0, 0, 0, 0, 0], points_available=27)
    else:
        with shelve.open(high_scores_filename, 'r') as data_file:
            lowest_level = data_file['lowest_level']
            high_score = data_file['high_score']
            stat_diffs = data_file['stat_diffs']
            points_available = data_file['points_available']
            return GameContainer(lowest_level=lowest_level, high_score=high_score,
                                 stat_diffs=stat_diffs, points_available=points_available)

def save_game_data(game):
    with shelve.open(high_scores_filename, 'n') as data_file:
        data_file['lowest_level'] = game.lowest_level
        data_file['high_score'] = game.high_score
        data_file['stat_diffs'] = game.stat_diffs
        data_file['points_available'] = game.points_available
