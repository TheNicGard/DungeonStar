#!/usr/bin/python3 -Wignore
import tcod as libtcod
from components.animation import Animation
from components.food import Food
from components.hunger import HungerType
from components.item import Item
from death_functions import kill_monster, kill_player
from entity import get_blocking_entities_at_location, Entity, get_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.entity_definitions import get_monster
from loader_functions.initialize_new_game import get_constants, get_game_variables, get_test_map_variables
from loader_functions.data_loaders import load_game, save_game, load_high_scores, save_high_scores
from menus import main_menu, message_box
from render_functions import clear_all, render_all
#from rpg_mechanics import die
from random import randint

def main():
    constants = get_constants()
    
    libtcod.console_set_custom_font('cp437_10x10.png',
                                    libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
    libtcod.console_init_root(constants['screen_width'], constants['screen_height'],
                              constants['window_title'], False)

    con = libtcod.console_new(constants['screen_width'], constants['screen_height'])
    panel = libtcod.console_new(constants['screen_width'], constants['panel_height'])

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None
    global lowest_level
    lowest_level = 1
    global highest_score
    highest_score = 0
    turn = 1

    lowest_level, highest_score = load_high_scores()
    
    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = libtcod.image_load('menu_background.png')

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image, constants['screen_width'],
                      constants['screen_height'], lowest_level, highest_score)

            if show_load_error_message:
                message_box(con, 'No save game to load',
                            constants['screen_width'], constants['screen_height'])

            libtcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            load_test_map = action.get('load_test_map')
            exit_game = action.get('exit')
        
            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, message_log, game_state, turn = get_game_variables(constants)
                game_state = GameStates.PLAYERS_TURN
                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state, turn = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif load_test_map:
                player, entities, game_map, message_log, game_state, turn = get_test_map_variables(constants)
                show_main_menu = False
            elif exit_game:
                save_high_scores(lowest_level, highest_score)
                break

        else:
            libtcod.console_clear(con)
            play_game(player, entities, game_map, turn, message_log, game_state, con, panel, constants)
            show_main_menu = True

def play_game(player, entities, game_map, turn, message_log,
              game_state, con, panel, constants):
    key_cursor = Entity("cursor", player.x, player.y, chr(219), libtcod.white, "Cursor",
                        animation=Animation(cycle_char=[chr(219), ' '], speed=0.25))
    
    fov_recompute = True
    fov_map = initialize_fov(game_map)

    key = libtcod.Key()
    mouse = libtcod.Mouse()
    
    previous_game_state = game_state

    targeting_item = None

    global lowest_level
    global highest_score
    
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y,
                          constants['fov_radius'], constants['fov_light_walls'],
                          constants['fov_algorithm'])

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute,
                   turn, message_log,
                   constants['screen_width'], constants['screen_height'],
                   constants['bar_width'], constants['panel_height'],
                   constants['panel_y'], mouse, constants['colors'], game_state,
                   key_cursor, {"CLASSIC_COLOR": False})
        
        fov_recompute = False
        libtcod.console_flush()
        clear_all(con, entities, key_cursor)
        
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        end = action.get('end')
        fullscreen = action.get('fullscreen')
        pickup = action.get('pickup')
        wait = action.get('wait')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        descend_stairs = action.get('descend_stairs')
        level_up = action.get('level_up')
        show_character_screen = action.get('show_character_screen')
        show_help_screen = action.get('show_help_screen')
        look_at = action.get("look_at")
        look_at_entity = action.get("look_at_entity")
        butcher = action.get("butcher")
 
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
                                fov_map = initialize_fov(game_map)
                                fov_recompute = True
                        else:
                            attack_results = player.fighter.attack(target)
                            player_turn_results.extend(player.hunger.tick(HungerType.EXERT))
                            player_turn_results.extend(attack_results)
                    else:
                        player.move(dx, dy)
                        player_turn_results.extend(player.hunger.tick(HungerType.MOVE))

                        entities_in_loc = get_entities_at_location(entities, destination_x, destination_y)
                        for e in entities_in_loc:
                            if e.sign:
                                message_log.add_message(Message("The sign says, \"" + e.sign.text + "\"", libtcod.white))
                            if e.trap:
                                player_turn_results.append({"stepped_on_trap": e.trap})
                                
                        fov_recompute = True

                    invisible_tick = player.fighter.tick_invisibility()
                    if invisible_tick:
                        message_log.add_message(invisible_tick)

                    game_state = GameStates.ENEMY_TURN
            elif wait:
                player_turn_results.extend(player.hunger.tick(HungerType.STATIC))
                game_state = GameStates.ENEMY_TURN
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
                        entities = game_map.next_floor(player, message_log, constants)
                        fov_map = initialize_fov(game_map)
                        fov_recompute = True
                        libtcod.console_clear(con)
                        lowest_level = game_map.dungeon_level
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
                    
        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if level_up:
            if level_up == 'hp':
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif level_up == 'str':
                player.fighter.base_power += 1
            elif level_up == 'def':
                player.fighter.base_defense += 1
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
                if e.x == key_cursor.x and e.y == key_cursor.y:
                    matching_entities.append(e.name)

            message_log.add_message(Message(", ".join(matching_entities), libtcod.lightest_sepia))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item,
                                                        entities=entities,
                                                        fov_map=fov_map,
                                                        target_x=target_x,
                                                        target_y=target_y)
                player_turn_results.extend(item_use_results)
                player_turn_results.extend(player.hunger.tick(HungerType.STATIC))
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if game_state == GameStates.LOOK_AT:
            if move:
                dx, dy = move
                if key_cursor.x + dx >= 0 and key_cursor.x + dx < constants["map_width"]:
                    key_cursor.x += dx
                if key_cursor.y + dy >= 0 and key_cursor.y + dy < constants["map_height"]:
                    key_cursor.y += dy
                
        if end:
            if game_state in (GameStates.SHOW_INVENTORY,
                              GameStates.DROP_INVENTORY,
                              GameStates.CHARACTER_SCREEN,
                              GameStates.HELP_SCREEN,
                              GameStates.LOOK_AT):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state, turn)
                save_high_scores(lowest_level, highest_score)
                return True
        
        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            gold_added = player_turn_result.get('gold_added')
            item_consumed = player_turn_result.get('consumed')
            food_eaten = player_turn_result.get("food_eaten")
            item_dropped = player_turn_result.get('item_dropped')
            equip = player_turn_result.get('equip')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            xp = player_turn_result.get('xp')
            enemy_gold_dropped = player_turn_result.get('enemy_gold_dropped')
            drop_inventory = player_turn_result.get("drop_inventory")
            stepped_on_trap = player_turn_result.get("stepped_on_trap")
            detect_traps = player_turn_result.get("detect_traps")
            
            if message:
                message_log.add_message(message)
                
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                    if player.inventory.gold_carried > highest_score:
                        highest_score = player.inventory.gold_carried
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)
                
            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if gold_added:
                entities.remove(gold_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed or food_eaten:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN

            if equip:
                equip_results = player.equipment.toggle_equip(equip)
                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    unequipped = equip_result.get('unequipped')
                    if equipped:
                        message_log.add_message(Message(
                            'You equipped the {0}.'.format(equipped.name)))
                    if unequipped:
                        message_log.add_message(Message(
                            'You unequipped the {0}.'.format(unequipped.name)))

                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting
                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled'))

            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

                if leveled_up:
                    message_log.add_message(Message(
                        'Your battle skills grow stronger! You reached level {0}!'.format(
                            player.level.current_level), libtcod.yellow))
                    previous_game_state = game_state
                    game_state = GameStates.LEVEL_UP
                    
            if enemy_gold_dropped:
                entities.append(enemy_gold_dropped)

            if drop_inventory:
                for i in drop_inventory.items:
                    entities.append(drop_inventory.drop_item(i)[0].get("item_dropped"))

            if stepped_on_trap:
                if not stepped_on_trap.revealed:
                    stepped_on_trap.set_reveal(True)
                    """
                    damage_taken = die(stepped_on_trap.trap.damage[0],
                                       stepped_on_trap.trap.damage[1])
                    """
                    damage_taken = randint(1, 4)
                    message_log.add_message(Message(
                        'You step on a trap of hidden spikes, taking {0} points of damage!'.format(
                            damage_taken), libtcod.yellow))
                    player.fighter.take_damage(damage_taken)

            if detect_traps:
                traps_found = False
                for e in entities:
                    if e.trap:
                        e.trap.set_reveal(True)
                        traps_found = True
                if traps_found:
                    message_log.add_message(Message(
                        "You become aware of the presence of traps on this floor!", libtcod.white
                    ))
                    
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)
                    
                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')
                        spawn_enemy = enemy_turn_result.get('spawn_enemy')
                        
                        if message:
                            message_log.add_message(message)
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)
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

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                turn = tick_turn(turn, player, entities)
                game_state = GameStates.PLAYERS_TURN

def tick_turn(turn, player, entities):
    expired = []
    expired_items = []

    for e in entities:
        if e.item and e.item.age is not None:
            e.item.age += 1
            if e.item.age >= e.item.max_age:
                expired.append(e)
        if e.inventory:
            for i in e.inventory.items:
                if i.item and i.item.age is not None:
                    i.item.age += 1
                    if i.item.age >= i.item.max_age:
                        expired_items.append(i)
            for i in expired_items:
                e.inventory.remove_item(i, i.item.count)

    for e in expired:
        entities.remove(e)

    if player.hunger.saturation > player.hunger.hungry_saturation:
        if turn % 10 == 0:
            player.fighter.heal(2)
    elif player.hunger.saturation > player.hunger.starving_saturation:
        if turn % 20 == 0:
            player.fighter.heal(2)
                
    return turn + 1
                
if __name__ == '__main__':
    main()
