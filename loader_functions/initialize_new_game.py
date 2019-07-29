import tcod as libtcod

from components.equipment import Equipment
from components.equippable import Equippable
from components.fighter import Fighter
from components.hunger import Hunger
from components.inventory import Inventory
from components.level import Level
from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from render_functions import RenderOrder


def get_constants():
    window_title = 'Dungeon Star'

    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1
    
    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10
    
    max_monsters_per_room = 3
    max_items_per_room = 2

    colors = {
        'dark_wall': libtcod.darkest_sepia,
        'dark_ground': libtcod.darker_sepia,
        'light_wall': libtcod.sepia,
        'light_ground': libtcod.light_sepia,
        'classic_dark_wall': libtcod.lighter_grey,
        'classic_dark_ground': libtcod.black,
        'classic_light_wall': libtcod.lightest_grey,
        'classic_light_ground': libtcod.white
    }

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'colors': colors
    }

    return constants


def get_game_variables(constants):
    fighter_component = Fighter(11, 11, 11, 11, 11, 11)
    inventory_component = Inventory(26)
    level_component = Level()
    
    hunger_component = Hunger()

    equipment_component = Equipment({"main_hand": None, "off_hand": None, "head": None,
                                     "under_torso": None, "over_torso": None, "legs": None,
                                     "feet": None, "left_finger": None, "right_finger": None})
    player = Entity("player", 0, 0, '@', libtcod.white, 'Player', blocks=True,
                    render_order=RenderOrder.ACTOR, fighter=fighter_component,
                    inventory=inventory_component, level=level_component,
                    equipment=equipment_component, hunger=hunger_component)
    entities = [player]

    equippable_component = Equippable("main_hand", power_bonus=2)
    dagger = Entity("dagger", 0, 0, ')', libtcod.silver, 'dagger',
                    weight=2, equippable=equippable_component)
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_rooms'], constants['room_min_size'],
                      constants['room_max_size'], constants['map_width'],
                      constants['map_height'], player, entities)

    message_log = MessageLog(constants['message_x'], constants['message_width'],
                             constants['message_height'])
    
    game_state = GameStates.PLAYERS_TURN
    turn = 1

    return player, entities, game_map, message_log, game_state, turn

def get_test_map_variables(constants):
    fighter_component = Fighter(11, 11, 11, 11, 11, 11)
    inventory_component = Inventory(26)
    level_component = Level()
    hunger_component = Hunger()

    equipment_component = Equipment({"main_hand": None, "off_hand": None, "head": None,
                                     "under_torso": None, "over_torso": None, "legs": None,
                                     "feet": None, "left_finger": None, "right_finger": None})    
    player = Entity("player", 0, 0, '@', libtcod.white, 'Player', blocks=True,
                    render_order=RenderOrder.ACTOR, fighter=fighter_component,
                    inventory=inventory_component, level=level_component,
                    equipment=equipment_component, hunger=hunger_component)
    entities = [player]

    equippable_component = Equippable("main_hand", power_bonus=2)
    dagger = Entity("dagger", 0, 0, ')', libtcod.silver, 'dagger',
                    weight=2, equippable=equippable_component)

    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)
    

    
    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_test_map(constants['map_width'], constants['map_height'], player, entities)

    message_log = MessageLog(constants['message_x'], constants['message_width'],
                             constants['message_height'])
    
    game_state = GameStates.PLAYERS_TURN
    turn = 1

    return player, entities, game_map, message_log, game_state, turn
