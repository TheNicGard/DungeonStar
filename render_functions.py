import tcod as libtcod
from enum import Enum
from game_states import GameStates
from menus import inventory_menu, level_up_menu, character_screen, help_screen

class RenderOrder(Enum):
    STAIRS = 1
    DOOR = 2
    SIGN = 3
    TRAP = 4
    CORPSE = 5
    GOLD = 6
    ITEM = 7
    ACTOR = 8

def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)

    return names.capitalize()
    
def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_NONE)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))
    
def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, turn,
               message_log, screen_width, screen_height, bar_width, panel_height, panel_y,
               mouse, colors, game_state, cursor, config):
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if config.get("CLASSIC_COLOR"):
                    if visible:
                        if wall:
                            libtcod.console_set_default_foreground(con, colors.get('classic_light_wall'))
                            libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
                        else:
                            libtcod.console_set_default_foreground(con, colors.get('classic_light_ground'))
                            libtcod.console_put_char(con, x, y, '.', libtcod.BKGND_NONE)
                        game_map.tiles[x][y].explored = True
                    elif game_map.tiles[x][y].explored:
                        if wall:
                            libtcod.console_set_default_foreground(con, colors.get('classic_dark_wall'))
                            libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
                        else:
                            libtcod.console_set_default_foreground(con, colors.get('classic_dark_ground'))
                            libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)
                else:
                    if visible:
                        if wall:
                            libtcod.console_set_char_background(con, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, colors.get('light_ground'), libtcod.BKGND_SET)
                        game_map.tiles[x][y].explored = True
                    elif game_map.tiles[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)

    if game_state == GameStates.LOOK_AT:
        render_cursor(con, cursor)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
    
    for entity in entities_in_render_order:
        if entity.animation:
            draw_animated_entity(con, entity, fov_map, game_map, False)
        else:
            draw_entity(con, entity, fov_map, game_map, False)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)
    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Dungeon level {0}'.format(game_map.dungeon_level))
    libtcod.console_print_ex(panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Turn {0}'.format(turn))
    if player.hunger.status is not None:
        libtcod.console_print_ex(panel, 1, 5, libtcod.BKGND_NONE, libtcod.LEFT,
                                 '{0}'.format(player.hunger.status))
    if game_state == GameStates.LOOK_AT:
        libtcod.console_print_ex(panel, 1, 6, libtcod.BKGND_NONE, libtcod.LEFT,
                                 '({0}, {1})'.format(cursor.x, cursor.y))

    libtcod.console_set_default_foreground(panel, libtcod.light_grey)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             get_names_under_mouse(mouse, entities, fov_map))

    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Inventory ({0}{2}/{1}{2})\n'.format(player.inventory.current_weight, player.inventory.capacity, chr(169))
        elif game_state == GameStates.DROP_INVENTORY:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'
        inventory_menu(con, inventory_title, player, 50, screen_width, screen_height)
    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40,
                      screen_width, screen_height)
    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, screen_width, screen_height)
    elif game_state == GameStates.HELP_SCREEN:
        help_screen(50, screen_width, screen_height)
    
def clear_all(con, entities, cursor):
    for entity in entities:
        clear_entity(con, entity)
    clear_entity(con, cursor)

def draw_entity(con, entity, fov_map, game_map, always_visible):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or ((entity.stairs or entity.door or entity.sign or entity.trap) and game_map.tiles[entity.x][entity.y].explored):
        libtcod.console_set_default_foreground(con, entity.color)
        if entity.fighter and entity.ai and entity.fighter.status.get("invisible"):
            if entity.fighter.status.get("invisible") <= 0:
                libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)
        else:
            libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)
    elif always_visible:
        libtcod.console_set_default_foreground(con, entity.color)
        libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)

def draw_animated_entity(con, entity, fov_map, game_map, always_visible):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or ((entity.stairs or entity.door or entity.sign or entity.trap) and game_map.tiles[entity.x][entity.y].explored):
        libtcod.console_set_default_foreground(con, entity.animation.get_color)
        if entity.fighter and entity.ai and entity.fighter.status.get("invisible"):
            if entity.fighter.status.get("invisible") <= 0:
                libtcod.console_put_char(con, entity.x, entity.y, entity.animation.get_char, libtcod.BKGND_NONE)
        else:
            libtcod.console_put_char(con, entity.x, entity.y, entity.animation.get_char, libtcod.BKGND_NONE)
    elif always_visible:
        libtcod.console_set_default_foreground(con, entity.animation.get_color)
        libtcod.console_put_char(con, entity.x, entity.y, entity.animation.get_char, libtcod.BKGND_NONE)
    entity.animation.tick()

def clear_entity(con, entity):
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)

def render_cursor(con, cursor):
    libtcod.console_set_default_foreground(con, cursor.animation.get_color)
    libtcod.console_put_char(con, cursor.x, cursor.y, cursor.animation.get_char, libtcod.BKGND_NONE)
    cursor.animation.tick()
