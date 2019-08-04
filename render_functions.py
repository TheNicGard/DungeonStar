import tcod as libtcod
from enum import Enum
from game_states import GameStates
from menus import inventory_menu, level_up_menu, character_screen, help_screen
from rpg_mechanics import display_ability

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
    
def render_bar(panel, x, y, total_width, value, maximum, bar_color, back_color):    
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_NONE)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    for tmp_x in range(total_width):
        libtcod.console_put_char(panel, x + tmp_x, y, ' ', libtcod.BKGND_NONE)
    libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}/{1}'.format(value, maximum))
    
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_NONE)

def get_health_color(hp_ratio):
    if hp_ratio <= 0.5:
        r_value = 255
    else:
        r_value = max(0, int((-511 * hp_ratio) + 511))
        
    if hp_ratio >= 0.5:
        g_value = 255
    else:
        g_value = max(0, int(511 * hp_ratio))

    return [r_value, g_value, 0]
    
def render_status_panel(panel, x, y, width, height, player, entities, game_map, fov_map, turn, color_accessibility):
    for tmp_x in range(width):
        for tmp_y in range(height):
            libtcod.console_put_char(panel, x + tmp_x, y + tmp_y, ' ', libtcod.BKGND_NONE)
            
    libtcod.console_set_default_background(panel, libtcod.darkest_grey)
    libtcod.console_rect(panel, x, y, width, height, False, libtcod.BKGND_SET)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER, "The Rogue")

    libtcod.console_print_ex(panel, x + 1, y + 2, libtcod.BKGND_NONE, libtcod.LEFT, "HP")
    render_bar(panel, x + 4, y + 2, width - 5, player.fighter.hp, player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + 1, height - 2, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Dungeon level {0}'.format(game_map.dungeon_level))
    libtcod.console_print_ex(panel, x + 1, height - 3, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Turn {0}'.format(turn))
    if player.hunger.status is not None:
        libtcod.console_print_ex(panel, x + 1, height - 4, libtcod.BKGND_NONE, libtcod.LEFT,
                                 '{0}'.format(player.hunger.status))

    entities_in_fov = entity_in_fov_list(entities, game_map, fov_map)
    index = 0
    for e in entities_in_fov:
        # Entity char
        libtcod.console_set_default_foreground(panel, e.color)
        libtcod.console_put_char(panel, x + 1, y + 5 + index, e.char, libtcod.BKGND_NONE)

        # Entity health
        health_ratio = e.fighter.hp / e.fighter.max_hp
        if not color_accessibility:
            libtcod.console_set_default_foreground(panel, get_health_color(health_ratio))
            libtcod.console_put_char(panel, x + 3, y + 5 + index, chr(219), libtcod.BKGND_NONE)
        else:
            health_char = ' '
            if health_ratio > 0.75:
                health_char = chr(219)
            elif health_ratio > 0.50:
                health_char = chr(178)
            elif health_ratio > 0.25:
                health_char = chr(177)
            else:
                health_char = chr(176)
                
            libtcod.console_set_default_foreground(panel, libtcod.white)
            libtcod.console_put_char(panel, x + 3, y + 5 + index, health_char, libtcod.BKGND_NONE)
            
        # Entity name
        libtcod.console_set_default_foreground(panel, libtcod.white)
        libtcod.console_print_ex(panel, x + 5, y + 5 + index, libtcod.BKGND_NONE, libtcod.LEFT,
                                 e.name)
        index += 1

    libtcod.console_set_default_background(panel, libtcod.black)

def entity_in_fov_list(entities, game_map, fov_map):
    entities_in_fov = []
    
    for entity in entities:
        if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) and game_map.tiles[entity.x][entity.y].explored:
            if entity.fighter and entity.ai:
                if entity.fighter.status.get("invisible") and entity.fighter.status.get("invisible") <= 0:
                    entities_in_fov.append(entity)
                else:
                    entities_in_fov.append(entity)
    # can't get always visible status
    return entities_in_fov
    
def render_all(con, panel, status_screen, entities, player, game_map, fov_map, fov_recompute,
               turn, message_log, screen_width, screen_height, panel_height, panel_y,
               mouse, colors, game_state, cursor, config, status_screen_width, status_screen_height):
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight
                window = game_map.tiles[x][y].window
                
                if config.get("CLASSIC_COLOR"):
                    if visible:
                        if wall:
                            libtcod.console_set_default_foreground(con, colors.get('classic_light_wall'))
                            libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
                        if window:
                            libtcod.console_set_default_foreground(con, colors.get('classic_light_window'))
                            libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
                        else:
                            libtcod.console_set_default_foreground(con, colors.get('classic_light_ground'))
                            libtcod.console_put_char(con, x, y, '.', libtcod.BKGND_NONE)
                        game_map.tiles[x][y].explored = True
                    elif game_map.tiles[x][y].explored:
                        if wall:
                            libtcod.console_set_default_foreground(con, colors.get('classic_dark_wall'))
                            libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
                        if window:
                            libtcod.console_set_default_foreground(con, colors.get('classic_dark_window'))
                            libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
                        else:
                            libtcod.console_set_default_foreground(con, colors.get('classic_dark_ground'))
                            libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)
                else:
                    if visible:
                        if wall:
                            libtcod.console_set_char_background(con, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
                        elif window:
                            libtcod.console_set_char_background(con, x, y, colors.get('light_window'), libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, colors.get('light_ground'), libtcod.BKGND_SET)
                        game_map.tiles[x][y].explored = True
                    elif game_map.tiles[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
                        elif window:
                            libtcod.console_set_char_background(con, x, y, colors.get('dark_window'), libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)

    if game_state == GameStates.LOOK_AT:
        render_cursor(con, cursor)

    # ENTITIES
    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
    
    for entity in entities_in_render_order:
        if entity.animation:
            draw_animated_entity(con, entity, fov_map, game_map, False)
        else:
            draw_entity(con, entity, fov_map, game_map, False)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
    
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # MESSAGE LOG
    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    if game_state == GameStates.LOOK_AT:
        libtcod.console_print_ex(panel, 1, 6, libtcod.BKGND_NONE, libtcod.LEFT,
                                 '({0}, {1})'.format(cursor.x, cursor.y))

    #### DO I STILL WANT TO KEEP THIS FUNCTIONALITY? ###
    """
    libtcod.console_set_default_foreground(panel, libtcod.light_grey)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             get_names_under_mouse(mouse, entities, fov_map))
    """

    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    ### STATUS PANEL ###
    libtcod.console_set_default_background(status_screen, libtcod.black)
    libtcod.console_clear(status_screen)
    render_status_panel(status_screen, 0, 0, status_screen_width, status_screen_height, player, entities, game_map, fov_map, turn, False)
    # THIS IS BUGGY AF, LIBTCOD IS SKETCHY
    status_screen.blit(con, screen_width - status_screen_width, 0, 0, 0, status_screen_width, status_screen_height)
    
    # MENUS
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
        help_screen(45, screen_width, screen_height)

creation_menu = {
        "Ability scores": ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"],
        "Select a starting item": ["(standard kit)", "+1 dagger (1d4)", "+1 leather helmet"]
}
        
def render_character_creation(con, panel, screen_width, screen_height, menu_cursor, stat_diffs, points_available):
    libtcod.console_clear(con)

    libtcod.console_set_default_foreground(con, libtcod.white)
    libtcod.console_print_ex(con, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT, "The Rogue is born...")
    
    header_index = 1
    menu_index = 0
    table_margin = 7
    
    for h, m in creation_menu.items():
    
        index = 0
        libtcod.console_set_default_foreground(con, libtcod.white)
        libtcod.console_print_ex(con, header_index, index + 3, libtcod.BKGND_NONE, libtcod.LEFT, h)
        for item in m:
            if menu_index == menu_cursor.index[0] and index == menu_cursor.index[1]:
                libtcod.console_set_default_foreground(con, libtcod.black)
                draw_background_rect(con, header_index, 4 + menu_cursor.index[1], len(h) + table_margin - 1, 1, libtcod.white)
            else:
                libtcod.console_set_default_foreground(con, libtcod.white)
            if menu_index == 0:
                libtcod.console_print_ex(con, header_index, index + 4, libtcod.BKGND_NONE, libtcod.LEFT, item + ":")
                libtcod.console_print_ex(con, len(h) + table_margin - 1, index + 4, libtcod.BKGND_NONE, libtcod.RIGHT, display_ability(8 + stat_diffs[index]))
            else:
                libtcod.console_print_ex(con, header_index, index + 4, libtcod.BKGND_NONE, libtcod.LEFT, item)
            index += 1

        header_index += len(h) + table_margin
        menu_index += 1

    libtcod.console_set_default_foreground(con, libtcod.white)
    libtcod.console_print_ex(con, 1, 11, libtcod.BKGND_NONE, libtcod.LEFT, "{0} points available".format(points_available))
    libtcod.console_print_ex(con, 1, 13, libtcod.BKGND_NONE, libtcod.LEFT, "+/- to add/subtract points")
    libtcod.console_print_ex(con, 1, 14, libtcod.BKGND_NONE, libtcod.LEFT, "Enter to accept changes")

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

def draw_background_rect(con, x, y, w, h, color):
    for i in range (w):
        for k in range(h):
            libtcod.console_set_char_background(con, x + i, y + k, color, libtcod.BKGND_SET)
    
def clear_all(con, entities, cursor):
    for entity in entities:
        clear_entity(con, entity)
    clear_entity(con, cursor)

def draw_entity(con, entity, fov_map, game_map, always_visible):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or ((entity.stairs or entity.door or entity.sign) and game_map.tiles[entity.x][entity.y].explored) or (entity.trap and entity.trap.revealed):
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
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or ((entity.stairs or entity.door or entity.sign) and game_map.tiles[entity.x][entity.y].explored) or (entity.trap and entity.trap.revealed):
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
