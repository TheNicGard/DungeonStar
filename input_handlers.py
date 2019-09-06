import tcod as libtcod
from game_states import GameStates

def handle_keys(key, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY,
                        GameStates.IDENTIFY_INVENTORY, GameStates.CHARGE_INVENTORY):
        return handle_inventory_keys(key)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(key)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key)
    elif game_state == GameStates.HELP_SCREEN:
        return handle_help_screen(key)
    elif game_state == GameStates.LOOK_AT:
        return handle_key_targeting(key)
    elif game_state == GameStates.CHARACTER_CREATION:
        return handle_creation_screen(key)
    return {}

def handle_player_turn_keys(key):
    key_char = chr(key.c)
    
    if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8 or key_char == 'k':
        return {'move': (0, -1)}
    elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2 or key_char == 'j':
        return {'move': (0, 1)}
    elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4 or key_char == 'h':
        return {'move': (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6 or key_char == 'l':
        return {'move': (1, 0)}
    elif key.vk == libtcod.KEY_KP7 or key_char == 'y':
        return {'move': (-1, -1)}
    elif key.vk == libtcod.KEY_KP9 or key_char == 'u':
        return {'move': (1, -1)}
    elif key.vk == libtcod.KEY_KP1 or key_char == 'b':
        return {'move': (-1, 1)}
    elif key.vk == libtcod.KEY_KP3 or key_char == 'n':
        return {'move': (1, 1)}
    
    elif key.vk == libtcod.KEY_KP5 or key_char == '.':
        return {'wait': True}
    elif key.text == ">":
        return {'descend_stairs': True}
    elif key.text == "<":
        return {'ascend_stairs': True}
    elif key.text == "R":
        return {'rest': True}
    
    elif key.text == 'g' or key.text == ',':
        return {'pickup': True}
    elif key_char == 'i':
        return {'show_inventory': True}
    elif key_char == 'd':
        return {'drop_inventory': True}
    elif key.vk == libtcod.KEY_TAB:
        return {'show_character_screen': True}
    elif key.text == '?':
        return {'show_help_screen': True}
    elif key_char == ';':
        return {'look_at': True}
    elif key_char == 'x':
        return {'butcher': True}
    elif key_char == 'w' and key.lctrl:
        return {'wizard_mode': True}
    
    elif key.vk == libtcod.KEY_ESCAPE:
        return {'end': True}
    elif key_char == 'f' and key.lctrl:
        return {'fullscreen': True}

    elif key.vk == libtcod.KEY_F1:
        return {"debug_print_fov": True}

    return {}

def handle_player_dead_keys(key):
    key_char = chr(key.c)

    if key_char == 'i':
        return {'show_inventory': True}
    elif key.vk == libtcod.KEY_TAB:
        return {'show_character_screen': True}
    elif key_char == 'q':
        return {'show_help_screen': True}
    elif key.vk == libtcod.KEY_ESCAPE:
        return {'end': True}
    elif key_char == 'f' and key.lctrl:
        return {'fullscreen': True}

    return {}

def handle_inventory_keys(key):
    index = key.c - ord('a')

    if index >= 0:
        return {'inventory_index': index}
    elif key.vk == libtcod.KEY_ESCAPE:
        return {'end': True}
    elif chr(key.c) == 'f' and key.lctrl:
        return {'fullscreen': True}

    return {}

def handle_targeting_keys(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}
    elif chr(key.c) == 'f' and key.lctrl:
        return {'fullscreen': True}
    return {}

def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'left_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'right_click': (x, y)}

    return {}

def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {'new_game': True}
    elif key_char == 'b':
        return {'load_game': True}
    elif key_char == 'c':
        return {'load_tutorial_map': True}
    elif key_char == 'd' or key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}
    elif key_char == 'q':
        return {'load_test_map': True}
    elif key_char == 'f' and key.lctrl:
        return {'fullscreen': True}

    return {}

def handle_level_up_menu(key):
    if key:
        key_char = chr(key.c)

        if key_char == 'a':
            return {'level_up': 'STR'}
        elif key_char == 'b':
            return {'level_up': 'DEX'}
        elif key_char == 'c':
            return {'level_up': 'CON'}
        elif key_char == 'd':
            return {'level_up': 'INT'}
        elif key_char == 'e':
            return {'level_up': 'WIS'}
        elif key_char == 'f':
            return {'level_up': 'CHA'}
        elif key_char == 'f' and key.lctrl:
            return {'fullscreen': True}
    return {}

def handle_character_screen(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {'end': True}
    elif chr(key.c) == 'f' and key.lctrl:
        return {'fullscreen': True}
    elif key.vk == libtcod.KEY_TAB:
        return {'end': True}
    return {}

def handle_help_screen(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {'end': True}
    elif chr(key.c) == 'f' and key.lctrl:
        return {'fullscreen': True}
    
    if key:
        if key.text == "?":
            return {'end': True}
    return {}

def handle_key_targeting(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {'end': True}
    elif chr(key.c) == 'f' and key.lctrl:
        return {'fullscreen': True}
    
    if key:
        key_char = chr(key.c)

        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8 or key_char == 'k':
            return {'move': (0, -1)}
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2 or key_char == 'j':
            return {'move': (0, 1)}
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4 or key_char == 'h':
            return {'move': (-1, 0)}
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6 or key_char == 'l':
            return {'move': (1, 0)}
        elif key.vk == libtcod.KEY_KP7 or key_char == 'y':
            return {'move': (-1, -1)}
        elif key.vk == libtcod.KEY_KP9 or key_char == 'u':
            return {'move': (1, -1)}
        elif key.vk == libtcod.KEY_KP1 or key_char == 'b':
            return {'move': (-1, 1)}
        elif key.vk == libtcod.KEY_KP3 or key_char == 'n':
            return {'move': (1, 1)}
    
        elif key.vk == libtcod.KEY_KP5 or key_char == '.':
            return {'look_at_entity': True}

        if key_char == ';':
            return {'end': True}

    return {}

def handle_creation_screen(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {'end': True}

    if key:
        key_char = chr(key.c)

        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8 or key_char == 'k':
            return {"menu_selection": "up"}
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2 or key_char == 'j':
            return {"menu_selection": "down"}
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4 or key_char == 'h':
            return {"menu_selection": "left"}
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6 or key_char == 'l':
            return {"menu_selection": "right"}
        elif key.text == "+":
            return {"increase": True}
        elif key.text == '-':
            return {"decrease": True}
        elif key.vk == libtcod.KEY_ENTER:
            return {"accept": True}
        
    return {}

def handle_confirmation_menu(key):
    key_char = chr(key.c)

    if key_char == 'y':
        return {'confirmation': True}
    if key_char == 'n':
        return {'confirmation': False}

    return {}
