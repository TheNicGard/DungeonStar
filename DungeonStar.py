#!/usr/bin/python3 -Wignore
import datetime
import os
import tcod as libtcod
from components.animation import Animation
from components.chargeable import Chargeable
from components.food import Food
from components.hunger import HungerType
from components.item import Item
from death_functions import kill_monster, kill_player
from entity import get_blocking_entities_at_location, Entity, get_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_container import GameContainer
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu, handle_confirmation_menu
from loader_functions.entity_definitions import get_monster, get_item
from loader_functions.initialize_new_game import get_constants, get_game_variables, get_test_map_variables, get_tutorial_map_variables
from loader_functions.data_loaders import load_game, save_game, save_game_data, load_game_data, delete_game, game_exists
from menus import main_menu, message_box, confirmation_menu
from menu_cursor import MenuCursor
from plot_gen import Plot
from random import randint, random
from render_functions import clear_all, render_all, render_character_creation
from rpg_mechanics import get_modifier, die, attack_success

def main():
    constants = get_constants()
    
    libtcod.console_set_custom_font('assets/cp437_10x10.png',
                                    libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
    libtcod.console_init_root(constants['screen_width'], constants['screen_height'],
                              constants['window_title'], False, libtcod.RENDERER_OPENGL2)

    con = libtcod.console_new(constants['screen_width'], constants['screen_height'])
    panel = libtcod.console_new(constants['message_width'], constants['panel_height'])
    status_screen = libtcod.console_new(constants['status_screen_width'], constants['status_screen_height'])

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    global max_points_available
    max_points_available= 27
    
    game = GameContainer(lowest_level=1, high_score=0,
                         stat_diffs=[0, 0, 0, 0, 0, 0], points_available=27)
    game = load_game_data()
    turn = 1
    identities = {}
    
    show_main_menu = True
    show_load_error_message = False
    show_delete_save_confirmation = False
    start_new_game = False

    main_menu_background_image = libtcod.image_load('main_menu_background.png')

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image, constants['screen_width'],
                      constants['screen_height'], game)

            if show_load_error_message:
                message_box(con, 'No save game to load',
                            constants['screen_width'], constants['screen_height'])

            if show_delete_save_confirmation:
                confirmation_menu(con, 'Erase saved game?', 35, constants['screen_width'],
                                  constants['screen_height'])
                    
                save_game_action = handle_confirmation_menu(key)
                delete_saved_game = save_game_action.get("confirmation")
                
                if delete_saved_game is not None:
                    start_new_game = delete_saved_game
                    show_delete_save_confirmation = False

            libtcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            load_tutorial_map = action.get('load_tutorial_map')
            load_test_map = action.get('load_test_map')
            exit_game = action.get('exit')
            fullscreen = action.get('fullscreen')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
                
            elif new_game:
                if game_exists():
                    show_delete_save_confirmation = True
                else:
                    start_new_game = True
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state, turn, identities = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif load_tutorial_map:
                player, entities, game_map, message_log, game_state, turn, identities = get_tutorial_map_variables(constants)
                show_main_menu = False
            elif load_test_map:
                player, entities, game_map, message_log, game_state, turn, identities = get_test_map_variables(constants)
                show_main_menu = False
            elif exit_game:
                save_game_data(game)
                break
            elif start_new_game:
                start_new_game = False
                player, entities, game_map, message_log, game_state, turn, identities = get_game_variables(constants)
                game_state = GameStates.CHARACTER_CREATION
                show_main_menu = False
            
            if fullscreen:
                libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        else:
            libtcod.console_clear(con)
            play_game(player, entities, game_map, turn, message_log, game_state, con, panel, status_screen, constants, game, identities)
            show_main_menu = True

def play_game(player, entities, game_map, turn, message_log,
              game_state, con, panel, status_screen, constants, game, identities):
    key_cursor = Entity("cursor", player.x, player.y, chr(0), libtcod.white, "Cursor",
                        animation=Animation(cycle_char=['X', ' '], speed=0.2))

    print(identities)
    
    if hasattr(player, "plot"):
        p = player.plot
    else:
        p = Plot()
        player.plot = p
        player.name = p.protagonist.name
    
    fov_map, fov_recompute = initialize_fov(game_map), True
    
    player_light_sources = []

    key = libtcod.Key()
    mouse = libtcod.Mouse()
    
    previous_game_state = game_state

    targeting_item = None
    search_count = 0

    enable_wizard_mode_confirmation = False
    debug_show_fov = False

    creation_menu_cursor = MenuCursor(max_index=[5, 5])
    stat_boosts = [[3, 4], [2, 5], [1, 2], [6, 3], [5, 6], [4, 1]]
    # This could be coded better
    # s_b[x] selects inspiration, s_b[x][0 to 1] major and minor boost
    # self       provides +2 CON, +1 INT
    # love       provides +2 DEX, +1 WIS
    # peace      provides +2 STR, +1 DEX
    # prosperity provides +2 CHA, +1 CON
    # the arts   provides +2 WIS, +1 CHA
    # the stars  provides +2 INT, +1 STR

    global max_points_available

    show_wizard_mode_confirmation = False
    
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y,
                          game_map.brightness + get_light(player_light_sources),
                          constants['fov_light_walls'], constants['fov_algorithm'])

        if game_state == GameStates.CHARACTER_CREATION:
            render_character_creation(con, panel, constants['screen_width'],
                                      constants['screen_height'], creation_menu_cursor,
                                      game.stat_diffs, game.points_available,
                                      stat_boosts, p)
            libtcod.console_flush()
        else:
            render_all(con, panel, status_screen, entities, player, game_map, fov_map, fov_recompute,
                       turn, message_log,
                       constants['screen_width'], constants['screen_height'],
                       constants['panel_height'], constants['panel_y'], mouse,
                       constants['colors'], game_state, key_cursor,
                       {"CLASSIC_COLOR": False, "DEBUG_SHOW_FOV": debug_show_fov},
                       constants["status_screen_width"], constants["status_screen_height"]
            )

            if show_wizard_mode_confirmation:
                confirmation_menu(con, 'Enable Wizard Mode?', 35, constants['screen_width'],
                                  constants['screen_height'])
                    
                wizard_mode_action = handle_confirmation_menu(key)
                enable_wizard_mode = wizard_mode_action.get("confirmation")

                if enable_wizard_mode is not None:
                    enable_wizard_mode_confirmation = enable_wizard_mode
                    show_wizard_mode_confirmation = False
                    continue
                        
            fov_recompute = False
            libtcod.console_flush()
            clear_all(con, entities, key_cursor)

        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        end = action.get('end')
        save_game_command = action.get('save_game_command')
        quit_game_command = action.get('quit_game_command')
        fullscreen = action.get('fullscreen')
        search = action.get("search")
        pickup = action.get('pickup')
        wait = action.get('wait')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        descend_stairs = action.get('descend_stairs')
        ascend_stairs = action.get('ascend_stairs')
        level_up = action.get('level_up')
        show_character_screen = action.get('show_character_screen')
        show_help_screen = action.get('show_help_screen')
        look_at = action.get("look_at")
        look_at_entity = action.get("look_at_entity")
        butcher = action.get("butcher")
        menu_selection = action.get("menu_selection")
        accept = action.get("accept")
        rest = action.get("rest")
        wizard_mode = action.get("wizard_mode")

        debug_dump_info = None
        debug_dump_to_file = None
        debug_print_fov = None
        if hasattr(player, "wizard_mode") and player.wizard_mode:
            debug_dump_info = action.get("debug_dump_info")
            debug_dump_to_file = action.get("debug_dump_to_file")
            debug_print_fov = action.get("debug_print_fov")
 
        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')
        
        player_turn_results = []

        if game_state == GameStates.PLAYERS_TURN:
            if move:    
                dx, dy = move
                destination_x = player.x + dx
                destination_y = player.y + dy
                
                if not game_map.is_blocked(destination_x, destination_y):
                    target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                    if target:
                        if target.door:
                            if not target.door.ajar:
                                target.door.open_door(game_map.tiles[destination_x][destination_y])
                                player_turn_results.extend(player.hunger.tick(HungerType.EXERT))

                                ### FOV SECTION START
                                recompute_fov(fov_map, player.x, player.y,
                                              game_map.brightness + get_light(player_light_sources),
                                              constants['fov_light_walls'], constants['fov_algorithm'])
                                fov_recompute = True
                                ### FOV SECTION END

                        else:
                            attack_results = player.fighter.attack(target)
                            player_turn_results.extend(player.hunger.tick(HungerType.EXERT))
                            player_turn_results.extend(attack_results)
                    else:
                        if player.fighter.is_effect("stuck"):
                            message_log.add_message(Message("You are stuck!", libtcod.yellow))
                        else:
                            player.move(dx, dy)
                            player_turn_results.extend(player.hunger.tick(HungerType.MOVE))
                            search_count = 0

                            entities_in_loc = get_entities_at_location(entities, destination_x, destination_y)
                            items_in_loc = []
                            for e in entities_in_loc:
                                if e.sign:
                                    message_log.add_message(Message("The sign says, \"" + e.sign.text + "\"", libtcod.white))
                                if e.trap and attack_success(get_modifier(player.fighter.dexterity), 10):
                                    e.trap.set_reveal(True)
                                    player_turn_results.extend(e.trap.trap_function(player, **{"game_map": game_map, "entities": entities, "fov_map": fov_map}))
                                if e.item:
                                    items_in_loc.append(e.get_name)
                            if len(items_in_loc) == 1:
                                message_log.add_message(Message("You see here " + items_in_loc[0] + ".", libtcod.white))
                            elif len(items_in_loc) > 1:
                                temp_str = "You see here "
                                for i in range(len(items_in_loc) - 1):
                                    temp_str += items_in_loc[i] + ", "
                                    temp_str += items_in_loc[len(items_in_loc) - 1] + "."
                                    message_log.add_message(Message(temp_str, libtcod.white))
                                    
                            ### FOV SECTION START
                            recompute_fov(fov_map, player.x, player.y,
                                          game_map.brightness + get_light(player_light_sources),
                                          constants['fov_light_walls'], constants['fov_algorithm'])
                            fov_recompute = True
                            ### FOV SECTION END
                        
                    previous_game_state = game_state
                    game_state = GameStates.ENEMY_TURN
                    
            elif wait:
                player_turn_results.extend(player.hunger.tick(HungerType.STATIC))
                previous_game_state = game_state
                game_state = GameStates.ENEMY_TURN

            elif wizard_mode and not hasattr(player, "wizard_mode"):
                show_wizard_mode_confirmation = True

            if enable_wizard_mode_confirmation:
                message_log.add_message(Message("Initiating wizard mode...", libtcod.red))
                player.wizard_mode = True
                player.fighter.STR = 100
                player.fighter.DEX = 100
                player.fighter.CON = 100
                player.fighter.INT = 100
                player.fighter.WIS = 100
                player.fighter.CHA = 100
                player.fighter.heal(100)

                death_wand = get_item("death_wand", -1, -1)
                death_wand.identity.identify()
                death_wand.item.chargeable = Chargeable(9999, 9999)
                player.inventory.add_item(death_wand)

                enable_wizard_mode_confirmation = False

            elif search:
                player_turn_results.extend(player.hunger.tick(HungerType.EXERT))
                if search_count == 8:
                    message_log.add_message(Message("You can find nothing else here.", libtcod.yellow))
                elif search_count == 7 or player.fighter.is_effect("dowsing"):
                    search_count = 8
                    search_surrounding_tiles(player, entities, True)
                else:
                    search_surrounding_tiles(player, entities, False)
                    search_count += 1
                
            elif pickup:
                pickup_results = []

                for entity in entities:
                    if entity.item or entity.valuable:
                        if entity.x == player.x and entity.y == player.y:
                            pickup_results.extend(player.inventory.add_item(entity))
       
                if len(pickup_results) > 0:
                    player_turn_results.extend(pickup_results)
                    player_turn_results.extend(player.hunger.tick(HungerType.MOVE))
                else:   
                    message_log.add_message(Message('There is nothing here to pickup.', libtcod.yellow))
                    
            elif descend_stairs:
                for entity in entities:
                    if entity.stairs and entity.x == player.x and entity.y == player.y:
                        if not entity.stairs.downwards:
                            message_log.add_message(Message('These stairs go up!', libtcod.yellow))
                        else:
                            if game_map.dungeon_level + 1 > game_map.lowest_level:
                                player_turn_results.append({'dead': player})
                                break
                            else:
                                entities = game_map.next_floor(player, message_log, constants, True)
                                
                                ### FOV SECTION START
                                fov_map = initialize_fov(game_map)
                                recompute_fov(fov_map, player.x, player.y,
                                              game_map.brightness + get_light(player_light_sources),
                                              constants['fov_light_walls'], constants['fov_algorithm'])
                                fov_recompute = True
                                ### FOV SECTION END
                                
                                libtcod.console_clear(con)
                                game.lowest_level = game_map.dungeon_level
                                player_turn_results.extend(player.hunger.tick(HungerType.EXERT))
                                break
                    elif entity.trap and entity.trap.revealed and entity.trap.trap_function.__name__ == "hole_trap" and entity.x == player.x and entity.y == player.y:
                        player_turn_results.append({"downwards_exit": True})
                        
                else:
                    message_log.add_message(Message('There are no stairs here!', libtcod.yellow))

            elif ascend_stairs:
                for entity in entities:
                    if entity.stairs and entity.x == player.x and entity.y == player.y:
                        if entity.stairs.downwards:
                            message_log.add_message(Message('These stairs go down!', libtcod.yellow))
                        else:
                            if game_map.dungeon_level - 1 <= 0:
                                player_turn_results.append({'dead': player})
                                break
                            else:
                                entities = game_map.next_floor(player, message_log, constants, False)

                                ### FOV SECTION START
                                fov_map = initialize_fov(game_map)
                                recompute_fov(fov_map, player.x, player.y,
                                              game_map.brightness + get_light(player_light_sources),
                                              constants['fov_light_walls'], constants['fov_algorithm'])
                                fov_recompute = True
                                ### FOV SECTION END
                                
                                libtcod.console_clear(con)
                                player_turn_results.extend(player.hunger.tick(HungerType.EXERT))
                                break
                else:
                    message_log.add_message(Message('There are no stairs here!', libtcod.yellow))
                    
            elif butcher:
                entities_in_loc = get_entities_at_location(entities, destination_x, destination_y)
                for e in entities_in_loc:
                    if "corpse" in e.classification:
                        item = Entity("flesh_of_" + e.id, e.x, e.y, "%", e.color,
                                    e.name[11:] + " flesh", weight=1,
                                    item=Item(1, max_age=300),
                                    food=Food(300))
                        message_log.add_message(Message("You butcher the flesh of the " +
                                                        e.name[11:] + ".", libtcod.white))
                        e.char = ','
                        e.name = 'bits of ' + e.name[11:]
                        # using 11: as a means to remove "remains of " is messy
                        e.classification.remove("corpse")
                        e.classification.append("corpse_bits")
                        player.inventory.add_item(item)

            elif rest:
                if player.fighter.hp == player.fighter.max_hp:
                    message_log.add_message(Message('You feel too awake to take a rest!', libtcod.yellow))
                elif player.hunger.saturation < player.hunger.starving_saturation:
                    message_log.add_message(Message('You are too hungry to sleep!', libtcod.yellow))
                else:
                    previous_game_state = game_state
                    game_state = GameStates.RESTING
                    
        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map, game_map=game_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))
            elif game_state == GameStates.IDENTIFY_INVENTORY:
                player_turn_results.extend(player.inventory.identify_item(item))
            elif game_state == GameStates.CHARGE_INVENTORY:
                player_turn_results.extend(player.inventory.charge_item(item))

        if level_up:
            if level_up == 'STR':
                player.fighter.STR += 1
            if level_up == 'DEX':
                player.fighter.DEX += 1
            if level_up == 'CON':
                player.fighter.CON += 1
            if level_up == 'INT':
                player.fighter.INT += 1
            if level_up == 'WIS':
                player.fighter.WIS += 1
            if level_up == 'CHA':
                player.fighter.CHA += 1

            game_state = previous_game_state

        if show_character_screen:
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN

        if show_help_screen:
            previous_game_state = game_state
            game_state = GameStates.HELP_SCREEN

        if look_at:
            previous_game_state = game_state
            game_state = GameStates.LOOK_AT
            key_cursor.x, key_cursor.y = player.x, player.y
            message_log.add_message(Message("Use the direction keys to move the cursor, \'.\' to examine an entity, or Esc to exit.", libtcod.white))

        if look_at_entity:
            matching_entities = []
            for e in entities:
                if e.x == key_cursor.x and e.y == key_cursor.y and (fov_map.fov[key_cursor.y][key_cursor.x] or ((e.stairs or e.door or e.sign or e.trap) and game_map.tiles[key_cursor.x][key_cursor.y].explored)):
                    if e.trap and not e.trap.revealed:
                        pass
                    else:
                        matching_entities.append(e.name)

            message_log.add_message(Message(", ".join(matching_entities), libtcod.lightest_sepia))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item,
                                                        entities=entities,
                                                        fov_map=fov_map,
                                                        game_map=game_map,
                                                        target_x=target_x,
                                                        target_y=target_y)
                player_turn_results.extend(item_use_results)
                player_turn_results.extend(player.hunger.tick(HungerType.STATIC))
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if game_state == GameStates.PLAYER_WIN:
            pass
                
        if game_state == GameStates.LOOK_AT:
            if move:
                dx, dy = move
                if key_cursor.x + dx >= 0 and key_cursor.x + dx < constants["map_width"]:
                    key_cursor.x += dx
                if key_cursor.y + dy >= 0 and key_cursor.y + dy < constants["map_height"]:
                    key_cursor.y += dy
                
                ### FOV SECTION START
                recompute_fov(fov_map, player.x, player.y,
                              game_map.brightness + get_light(player_light_sources),
                              constants['fov_light_walls'], constants['fov_algorithm'])
                fov_recompute = True
                ### FOV SECTION END

        if quit_game_command:
            delete_game()
            save_game_data(game)
            return True

        if save_game_command:
            save_game(player, entities, game_map, message_log, game_state, turn, identities)
            save_game_data(game)
            return True

        if end:
            if game_state in (GameStates.SHOW_INVENTORY,
                              GameStates.DROP_INVENTORY,
                              GameStates.CHARACTER_SCREEN,
                              GameStates.HELP_SCREEN,
                              GameStates.LOOK_AT):
                game_state = previous_game_state
                
                ### FOV SECTION START
                fov_map = initialize_fov(game_map)
                recompute_fov(fov_map, player.x, player.y,
                              game_map.brightness + get_light(player_light_sources),
                              constants['fov_light_walls'], constants['fov_algorithm'])
                fov_recompute = True
                ### FOV SECTION END
                
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})

            else:
                if game_state == GameStates.PLAYER_DEAD:
                    delete_game()
                else:
                    save_game(player, entities, game_map, message_log, game_state, turn, identities)
                save_game_data(game)
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if debug_dump_info:
            print_log(debug_dump_to_file, player, entities, game_map, fov_map)

        if debug_print_fov:
            debug_show_fov = not debug_show_fov
            
            ### FOV SECTION START
            fov_map = initialize_fov(game_map)
            recompute_fov(fov_map, player.x, player.y,
                          game_map.brightness + get_light(player_light_sources),
                          constants['fov_light_walls'], constants['fov_algorithm'])
            fov_recompute = True
            ### FOV SECTION END

        if game_state == GameStates.RESTING:
            if player.fighter.hp == player.fighter.max_hp:
                game_state = GameStates.PLAYERS_TURN
            
        if game_state == GameStates.CHARACTER_CREATION:
            menu_selection = action.get("menu_selection")
            increase = action.get("increase")
            decrease = action.get("decrease")
            accept = action.get("accept")

            if menu_selection:
                if menu_selection == "up" and creation_menu_cursor.index[1] > 0:
                    creation_menu_cursor.index[1] -= 1
                if menu_selection == "down" and creation_menu_cursor.index[1] < creation_menu_cursor.max_index[creation_menu_cursor.index[0]]:
                    creation_menu_cursor.index[1] += 1

                if menu_selection == "left" and creation_menu_cursor.index[0] > 0:
                    creation_menu_cursor.index[0] -= 1
                    creation_menu_cursor.index[1] = 0
                if menu_selection == "right" and creation_menu_cursor.index[0] < len(creation_menu_cursor.max_index) - 1:
                    creation_menu_cursor.index[0] += 1
                    creation_menu_cursor.index[1] = 0

            if increase and creation_menu_cursor.index[0] == 0:
                cost = 7 - (game.stat_diffs[creation_menu_cursor.index[1]] + 8)

                if game.points_available + cost >= 0:
                    game.points_available += cost
                    game.stat_diffs[creation_menu_cursor.index[1]] += 1

            if decrease and creation_menu_cursor.index[0] == 0:
                cost = game.stat_diffs[creation_menu_cursor.index[1]]

                if game.points_available + cost <= max_points_available and game.stat_diffs[creation_menu_cursor.index[1]] > 0:    
                    game.points_available += cost
                    game.stat_diffs[creation_menu_cursor.index[1]] -= 1

            # This needs to be separated to a new module
            if accept:            
                if creation_menu_cursor.index[0] == len(creation_menu_cursor.max_index) - 1:
                    player.fighter.STR = 8 + game.stat_diffs[0]
                    player.fighter.DEX = 8 + game.stat_diffs[1]
                    player.fighter.CON = 8 + game.stat_diffs[2]
                    player.fighter.INT = 8 + game.stat_diffs[3]
                    player.fighter.WIS = 8 + game.stat_diffs[4]
                    player.fighter.CHA = 8 + game.stat_diffs[5]

                    if creation_menu_cursor.index[1] == 0:
                        player.fighter.CON += 2
                        player.fighter.INT += 1
                    elif creation_menu_cursor.index[1] == 1:
                        player.fighter.DEX += 2
                        player.fighter.WIS += 1
                    elif creation_menu_cursor.index[1] == 2:
                        player.fighter.STR += 2
                        player.fighter.DEX += 1
                    elif creation_menu_cursor.index[1] == 3:
                        player.fighter.CHA += 2
                        player.fighter.CON += 1
                    elif creation_menu_cursor.index[1] == 4:
                        player.fighter.WIS += 2
                        player.fighter.CHA += 1
                    elif creation_menu_cursor.index[1] == 5:
                        player.fighter.INT += 2
                        player.fighter.STR += 1
                    
                    player.fighter.heal(50)
                    # this needs to dynamic per character's strength
                    player.inventory.capacity += (get_modifier(player.fighter.strength) * 10)

                    dagger = get_item("dagger", -1, -1)
                    armor = get_item("leather_armor", -1, -1)
                    potion = get_item("healing_potion", -1, -1)                    
                    potion.identity.identify()
                    
                    player.inventory.items = []
                    # make item selectable instead of using just an index
                    # self: tower shield
                    if creation_menu_cursor.index[1] == 0:
                        shield = get_item("tower_shield", -1, -1)
                        player.inventory.add_item(shield)
                        player.equipment.toggle_equip(shield)
                    # love: pacify wand and escape scrolls
                    elif creation_menu_cursor.index[1] == 1:
                         pacify_wand = get_item("pacify_wand", -1, -1)
                         escape_scrolls = get_item("escape_scroll", -1, -1, 3)
                         pacify_wand.identity.identify()
                         escape_scrolls.identity.identify()
                         pacify_wand.item.chargeable.recharge(20)
                         player.inventory.add_item(pacify_wand)
                         player.inventory.add_item(escape_scrolls)
                    # peace: +2 dagger and wand of striking
                    elif creation_menu_cursor.index[1] == 2:
                        dagger.equippable.enchantment = 2
                        striking_wand = get_item("striking_wand", -1, -1)
                        striking_wand.identity.identify()
                        striking_wand.item.chargeable.recharge(20)
                        player.inventory.add_item(striking_wand)
                    # prospertiy: greed wand and detect items scrolls
                    elif creation_menu_cursor.index[1] == 3:
                        greed_wand = get_item("greed_wand", -1, -1)
                        detect_items_scrolls = get_item("detect_items_scroll", -1, -1, 3)
                        greed_wand.identity.identify()
                        detect_items_scrolls.identity.identify()
                        greed_wand.item.chargeable.recharge(20)
                        player.inventory.add_item(greed_wand)
                        player.inventory.add_item(detect_items_scrolls)
                    # the arts: lightning wand TODO: find a better item
                    elif creation_menu_cursor.index[1] == 4:
                        lightning_wand = get_item("lightning_wand", -1, -1)
                        lightning_wand.identity.identify()
                        lightning_wand.item.chargeable.recharge(20)
                        player.inventory.add_item(lightning_wand)
                    # the stars: dowsing, mapping, and aura wands
                    elif creation_menu_cursor.index[1] == 5:
                        dowsing_ring = get_item("dowsing_ring", -1, -1)
                        mapping_scrolls = get_item("mapping_scroll", -1, -1, 3)
                        detect_aura_scrolls = get_item("detect_aura_scroll", -1, -1, 3)
                        mapping_scrolls.identity.identify()
                        detect_aura_scrolls.identity.identify()
                        dowsing_ring.identity.identify()
                        player.inventory.add_item(mapping_scrolls)
                        player.inventory.add_item(detect_aura_scrolls)
                        player.inventory.add_item(dowsing_ring)
                        player.equipment.toggle_equip(dowsing_ring)

                    # items across all inspirations
                    player.inventory.add_item(dagger)
                    player.equipment.toggle_equip(dagger)    
                    player.inventory.add_item(armor)
                    player.equipment.toggle_equip(armor)
                    player.inventory.add_item(potion)
                    
                    game_state = GameStates.PLAYERS_TURN
                    libtcod.console_clear(con)
                    libtcod.console_flush()
                elif creation_menu_cursor.index[0] < len(creation_menu_cursor.max_index) - 1:
                    creation_menu_cursor.index[0] += 1
                    creation_menu_cursor.index[1] = 0

        i = 0
        while i < len(player_turn_results):
            player_turn_result = player_turn_results[i]
            
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            gold_added = player_turn_result.get('gold_added')
            item_consumed = player_turn_result.get('consumed')
            food_eaten = player_turn_result.get("food_eaten")
            item_dropped = player_turn_result.get('item_dropped')
            item_identified = player_turn_result.get('item_identified')
            item_charged = player_turn_result.get('item_charged')
            equip = player_turn_result.get('equip')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            xp = player_turn_result.get('xp')
            enemy_gold_dropped = player_turn_result.get('enemy_gold_dropped')
            drop_inventory = player_turn_result.get("drop_inventory")
            teleport = player_turn_result.get("teleport")
            identify_menu = player_turn_result.get("identify_menu")
            charge_menu = player_turn_result.get("charge_menu")
            downwards_exit = player_turn_result.get("downwards_exit")
            light_added = player_turn_result.get("light_added")
            light_removed = player_turn_result.get("light_removed")
            forget_map = player_turn_result.get("forget_map")
            
            if message:
                message_log.add_message(message)
                
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity, game)
                else:
                    message = kill_monster(dead_entity, fov_map)

                message_log.add_message(message)
                
            if item_added:
                entities.remove(item_added)
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.ENEMY_TURN

            if gold_added:
                entities.remove(gold_added)
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.ENEMY_TURN

            if (item_consumed or food_eaten) and game_state is not GameStates.PLAYER_DEAD:
                if item_consumed is not None and isinstance(item_consumed, Entity):
                    item_consumed.identity.identify()
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.ENEMY_TURN

            if item_identified:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.ENEMY_TURN

            if item_charged:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.ENEMY_TURN

            if equip:
                equip_results = player.equipment.toggle_equip(equip)
                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    unequipped = equip_result.get('unequipped')
                    if equipped:
                        message_log.add_message(Message(
                            'You equipped the {0}.'.format(equipped.get_name)))
                    if unequipped:
                        message_log.add_message(Message(
                            'You unequipped the {0}.'.format(unequipped.get_name)))

                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting
                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled.'))

            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

                if leveled_up:
                    message_log.add_message(Message(
                        'Your battle skills grow stronger! You reached level {0}!'.format(
                            player.level.current_level), libtcod.yellow))
                    previous_game_state = GameStates.PLAYERS_TURN
                    game_state = GameStates.LEVEL_UP
                    
            if enemy_gold_dropped:
                entities.append(enemy_gold_dropped)

            if drop_inventory:
                for i in drop_inventory.items:
                    entities.append(drop_inventory.drop_item(i)[0].get("item_dropped"))

            if teleport:
                ### FOV SECTION START
                fov_map = initialize_fov(game_map)
                recompute_fov(fov_map, player.x, player.y,
                              game_map.brightness + get_light(player_light_sources),
                              constants['fov_light_walls'], constants['fov_algorithm'])
                fov_recompute = True
                ### FOV SECTION END

            if identify_menu:
                previous_game_state = game_state
                game_state = GameStates.IDENTIFY_INVENTORY
            
            if charge_menu:
                previous_game_state = game_state
                game_state = GameStates.CHARGE_INVENTORY

            if downwards_exit:
                entities = game_map.next_floor(player, message_log, constants, True, False)
                ### FOV SECTION START
                fov_map = initialize_fov(game_map)
                recompute_fov(fov_map, player.x, player.y,
                              game_map.brightness + get_light(player_light_sources),
                              constants['fov_light_walls'], constants['fov_algorithm'])
                fov_recompute = True
                ### FOV SECTION END
                libtcod.console_clear(con)
                game.lowest_level = game_map.dungeon_level

                message_log.add_message(Message('You fall to the floor below!',
                                                libtcod.yellow))
                player_turn_results.extend(player.fighter.take_damage(player.fighter.max_hp // 5))

            if light_added:
                player_light_sources.append(light_added)

                ### FOV SECTION START
                fov_map = initialize_fov(game_map)
                recompute_fov(fov_map, player.x, player.y,
                              game_map.brightness + get_light(player_light_sources),
                              constants['fov_light_walls'], constants['fov_algorithm'])
                fov_recompute = True
                ### FOV SECTION END
                
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.ENEMY_TURN

            if light_removed and light_removed in player_light_sources:
                player_light_sources.remove(light_removed)
                ### FOV SECTION START
                fov_map = initialize_fov(game_map)
                recompute_fov(fov_map, player.x, player.y,
                              game_map.brightness + get_light(player_light_sources),
                              constants['fov_light_walls'], constants['fov_algorithm'])
                fov_recompute = True
                ### FOV SECTION END
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.ENEMY_TURN

            if forget_map:
                game_map.initialize_tiles()
                for x in range(game_map.width - 1):
                    for y in range(game_map.height - 1):
                        game_map.tiles[x][y].explored = False
                
                ### FOV SECTION START
                fov_map = initialize_fov(game_map)
                recompute_fov(fov_map, player.x, player.y,
                              game_map.brightness + get_light(player_light_sources),
                              constants['fov_light_walls'], constants['fov_algorithm'])
                fov_recompute = True
                ### FOV SECTION END
                                
                libtcod.console_clear(con)
                
            i += 1
                    
        if game_state == GameStates.ENEMY_TURN or game_state == GameStates.RESTING:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)
                    
                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')
                        spawn_enemy = enemy_turn_result.get('spawn_enemy')
                        downwards_exit = enemy_turn_result.get("downwards_exit")
                        
                        if message:
                            message_log.add_message(message)
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity, game)
                            else:
                                message = kill_monster(dead_entity, fov_map)
                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break
                        if spawn_enemy:
                            new_enemy = get_monster(spawn_enemy.get("name"),
                                                    spawn_enemy.get("x"),
                                                    spawn_enemy.get("y"))
                            if spawn_enemy.get("mother"):
                                new_enemy.ai.mother = spawn_enemy.get("mother")
                            entities.append(new_enemy)
                        if downwards_exit:
                            if fov_map.fov[entity.y][entity.x]:
                                message_log.add_message(Message('{0} fell down a hole!'.format(
                                    entity.name.capitalize()),
                                                                libtcod.white))
                            entities.remove(entity)
                            break

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                old_game_state = game_state
                turn, game_state = tick_turn(turn, player, entities, game_state,
                                             message_log, game, fov_map,
                                             player_light_sources)
                if game_state == old_game_state:
                    game_state = previous_game_state

def tick_turn(turn, player, entities, game_state, message_log, game, fov_map, player_light_sources):
    expired = []
    expired_items = []

    if player.hunger.saturation > player.hunger.hungry_saturation:
        if turn % 10 == 0:
            player.fighter.heal(1)
    elif player.hunger.saturation > player.hunger.starving_saturation:
        if turn % 20 == 0:
            player.fighter.heal(1)
    
    for e in entities:
        if e.item:            
            if e.item.age is not None:
                e.item.age += 1
                if e.item.age >= e.item.max_age:
                    expired.append(e)
            elif e.item.light_source is not None and e.item.light_source.lit:
                e.item.light_source.tick(message_log, False)
        if e.inventory:
            for i in e.inventory.items:
                if i.item and i.item.age is not None:
                    i.item.age += 1
                    if i.item.age >= i.item.max_age:
                        expired_items.append(i)
                elif i.item.light_source is not None and i.item.light_source.lit:
                    i.item.light_source.tick(message_log, True)
                    if i.item.light_source.get_light < 0 and i.item.light_source in player_light_sources:
                        player_light_sources.remove(e.item.light_source)
            for i in expired_items:
                e.inventory.remove_item(i, i.item.count)
        if e.fighter:
            results = []
            
            results.extend(e.fighter.effects.tick())
            
            for result in results:
                message = result.get("message")
                poison_damage = result.get("poison_damage")
                regeneration = result.get("regeneration")
                invisible = result.get("invisible")
                stuck = result.get("stuck")
                
                if message:
                    message_log.add_message(message)

                if poison_damage and turn % 10 == 0:
                    death_results = []
                    death_results.extend(e.fighter.take_damage(4))
                    for death_result in death_results:
                        dead_entity = death_result.get('dead')
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(e, game)
                            else:
                                message = kill_monster(e, fov_map)
                            message_log.add_message(message)

                if regeneration and turn % 10 == 0:
                    e.fighter.heal(2)

                if invisible is not None and invisible <= 0:
                    if e.ai:
                        message_log.add_message(Message("The {0} reappears!".format(e.name),
                                                        libtcod.white))
                    else:
                        message_log.add_message(Message("Color starts to reappear on your body!",
                                                    libtcod.yellow))

                if stuck is not None and stuck <= 0:
                    if e.ai and fov_map.fov[e.y][e.x]:
                        message_log.add_message(Message("The {0} is freed!".format(e.name),
                                                        libtcod.white))
                    elif not e.ai:
                        message_log.add_message(Message("You become freed!",
                                                        libtcod.green))

    for e in expired:
        entities.remove(e)
                
    return turn + 1, game_state

def get_light(player_light_sources):
    if len(player_light_sources) > 0:
        return max(light.get_light for light in player_light_sources)
    return 0

def search_surrounding_tiles(player, entities, instant_search):
    for x in range(player.x - 1, player.x + 2):
        for y in range(player.y - 1, player.y + 2):
            ents = get_entities_at_location(entities, x, y)
            if len(ents) > 0:
                for e in ents:
                    if e.trap and not e.trap.revealed:
                        # 10% chance to reveal traps
                        if instant_search or random() < 0.1:
                            e.trap.set_reveal(True)

def print_log(debug_dump_to_file, player, entities, game_map, fov_map):
    current_time = datetime.datetime.now()
    f = open("{0}.txt".format(current_time.strftime("logfile_%Y_%m_%d_%H_%M_%S")), "w+")

    if debug_dump_to_file:
        f.write("Entities:\n")
    else:
        print("Entities:")
    
    for e in entities:
        line = ""
        line += "{0} ({1}): ({2}, {3})".format(e.name, e.id, e.x, e.y)
        if e.item:
            line += ". This is an item."
        elif e.ai and e.fighter:
            line += ".\nThis is monster has {0}/{1} HP.".format(e.fighter.max_hp, e.fighter.hp)
            if fov_map.fov[e.y][e.x]:
                line += " It is in the FOV."
            else:
                line += " It is not in the FOV."
        elif e.trap:
            line += ". This is a trap."
        elif e.sign:
            line += ".\nThis is sign reads \"{0}\".".format(e.sign.text)
        elif e.stairs:
            line += ". These are stairs."
        elif e.door:
            line += ". This is a door."
        if debug_dump_to_file:
            f.write(line + "\n\n")
        else:
            print(line + "\n")
    
    if debug_dump_to_file:
        f.write("\nGame map:\n")
    else:
        print("\nGame map:")

    for r in range(game_map.height):
        line = ""
        for c in range(game_map.width):
            entities_in_loc = get_entities_at_location(entities, c, r)
            
            if player.x == c and player.y == r:
                line += "@"
            elif len(entities_in_loc) > 0:
                top_entity = sorted(entities_in_loc, key=lambda e: e.render_order.value)[0]
                if top_entity.item:
                    line += "*"
                elif top_entity.ai:
                    line += "A"
                elif top_entity.trap:
                    line += "^"
                elif top_entity.sign:
                    line += "|"
                elif top_entity.stairs:
                    line += ">"
                elif top_entity.door:
                    line += "+"
            elif game_map.tiles[c][r].blocked:
                line += "#"
            else:
                line += "."
                
        if debug_dump_to_file:
            f.write(line + "\n")
        else:
            print(line)
    
    if debug_dump_to_file:
        f.write("\nFOV map:\n")
    else:
        print("\nFOV map:")
                
    for r in range(game_map.height):
        line = ""
        for c in range(game_map.width):
            entities_in_loc = get_entities_at_location(entities, c, r)
            
            if player.x == c and player.y == r:
                line += "@"
            elif len(entities_in_loc) > 0:
                if fov_map.fov[r][c]:
                    line += "!"
                else:
                    line += "?"
            elif fov_map.fov[r][c]:
                line += "1"
            else:
                line += "0"
                
        if debug_dump_to_file:
            f.write(line + "\n")
        else:
            print(line)
                    
    if debug_dump_to_file:
        f.close()

if __name__ == '__main__':
    main()
