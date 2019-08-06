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
from rpg_mechanics import advantage_roll

def get_constants():
    window_title = 'Dungeon Star'

    screen_width = 100
    screen_height = 50

    status_screen_width = 20
    status_screen_height = 50

    panel_height = 6
    panel_y = screen_height - panel_height - 1

    message_x = 1
    message_width = screen_width - status_screen_width - 1
    message_height = panel_height - 1
    
    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10
    
    colors = {
        'dark_wall': libtcod.darkest_sepia,
        'dark_window': libtcod.darker_cyan,
        'dark_ground': libtcod.darker_sepia,
        'light_wall': libtcod.sepia,
        'light_window': libtcod.cyan,
        'light_ground': libtcod.light_sepia,
        'classic_dark_wall': libtcod.lighter_grey,
        'classic_dark_window': libtcod.darker_cyan,
        'classic_dark_ground': libtcod.black,
        'classic_light_wall': libtcod.lightest_grey,
        'classic_light_window': libtcod.cyan,
        'classic_light_ground': libtcod.white
    }

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
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
        'colors': colors,
        'status_screen_width': status_screen_width,
        'status_screen_height': status_screen_height
    }

    return constants


def get_game_variables(constants):
    fighter_component = Fighter(
        advantage_roll(4, 3, 1, 6), advantage_roll(4, 3, 1, 6),
        advantage_roll(4, 3, 1, 6), advantage_roll(4, 3, 1, 6),
        advantage_roll(4, 3, 1, 6), advantage_roll(4, 3, 1, 6),
        advantage_roll(4, 3, 1, 6)
    )
    inventory_component = Inventory(26)
    level_component = Level()
    
    hunger_component = Hunger()

    equipment_component = Equipment({"main_hand": None, "off_hand": None, "head": None,
                                     "under_torso": None, "over_torso": None, "legs": None,
                                     "feet": None, "left_finger": None, "right_finger": None,
                                     "cloak": None})
    player = Entity("player", 0, 0, '@', libtcod.white, 'Player', blocks=True,
                    render_order=RenderOrder.ACTOR, fighter=fighter_component,
                    inventory=inventory_component, level=level_component,
                    equipment=equipment_component, hunger=hunger_component)
    entities = [player]

    equippable_component = Equippable("main_hand", hit_dice=[1, 4], enchantment=0)
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
    fighter_component = Fighter(11, 11, 11, 11, 11, 11, 1)
    
    inventory_component = Inventory(26)
    level_component = Level()
    hunger_component = Hunger()

    equipment_component = Equipment({"main_hand": None, "off_hand": None, "head": None,
                                     "under_torso": None, "over_torso": None, "legs": None,
                                     "feet": None, "left_finger": None, "right_finger": None,
                                     "cloak": None})    
    player = Entity("player", 0, 0, '@', libtcod.white, 'Player', blocks=True,
                    render_order=RenderOrder.ACTOR, fighter=fighter_component,
                    inventory=inventory_component, level=level_component,
                    equipment=equipment_component, hunger=hunger_component)
    entities = [player]

    equippable_component = Equippable("main_hand", hit_dice=[1, 4], enchantment=0)
    dagger = Entity("dagger", 0, 0, ')', libtcod.silver, 'dagger',
                    weight=2, equippable=equippable_component)

    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)
    
    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_test_map(constants['map_width'], constants['map_height'], player, entities, "test_map")

    message_log = MessageLog(constants['message_x'], constants['message_width'],
                             constants['message_height'])
    
    game_state = GameStates.PLAYERS_TURN
    turn = 1

    return player, entities, game_map, message_log, game_state, turn

def get_tutorial_map_variables(constants):
    fighter_component = Fighter(11, 11, 11, 11, 11, 11, 1)
    
    inventory_component = Inventory(26)
    level_component = Level()
    hunger_component = Hunger()

    equipment_component = Equipment({"main_hand": None, "off_hand": None, "head": None,
                                     "under_torso": None, "over_torso": None, "legs": None,
                                     "feet": None, "left_finger": None, "right_finger": None,
                                     "cloak": None})    
    player = Entity("player", 0, 0, '@', libtcod.white, 'Player', blocks=True,
                    render_order=RenderOrder.ACTOR, fighter=fighter_component,
                    inventory=inventory_component, level=level_component,
                    equipment=equipment_component, hunger=hunger_component)
    entities = [player]

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_test_map(constants['map_width'], constants['map_height'], player, entities, "tutorial_map")

    message_log = MessageLog(constants['message_x'], constants['message_width'],
                             constants['message_height'])
    
    game_state = GameStates.PLAYERS_TURN
    turn = 1

    return player, entities, game_map, message_log, game_state, turn
