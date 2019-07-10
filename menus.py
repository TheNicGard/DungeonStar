import tcod as libtcod

def menu(con, header, options, width, screen_width, screen_height):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options')

    header_height = libtcod.console_get_height_rect(con, 0, 0, width, screen_height, header)
    height = len(options) + header_height

    window = libtcod.console_new(width, height)

    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

def inventory_menu(con, header, player, inventory_width, screen_width, screen_height):
    if len(player.inventory.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in player.inventory.items:
            if player.equipment.main_hand == item:
                options.append('{0} (on main hand)'.format(item.name))
            elif player.equipment.off_hand == item:
                options.append('{0} (on off hand)'.format(item.name))
            else:
                options.append(item.name)
    menu(con, header, options, inventory_width, screen_width, screen_height)

def main_menu(con, background_image, screen_width, screen_height):
    libtcod.image_blit_2x(background_image, 0, 0, 0)

    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4,
                             libtcod.BKGND_NONE, libtcod.CENTER,
                             'Dungeon Star')
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 2),
                             libtcod.BKGND_NONE, libtcod.CENTER, 'Nic Gard (C) 2019')

    menu(con, '', ['Play a new game', 'Continue last game', 'Quit'], 24,
         screen_width, screen_height)

def level_up_menu(con, header, player, menu_width, screen_width, screen_height):
    options = ['Constitution (+20 HP, from {0})'.format(player.fighter.max_hp),
               'Strength (+1 attack, from {0})'.format(player.fighter.power),
               'Agility (+1 defense, from {0})'.format(player.fighter.defense)]
    menu(con, header, options, menu_width, screen_width, screen_height)

def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)

def character_screen(player, character_screen_width, character_screen_height,
                     screen_width, screen_height):
    window = libtcod.console_new(character_screen_width, character_screen_height)
    libtcod.console_set_default_foreground(window, libtcod.white)

    libtcod.console_print_rect_ex(window, 0, 1, character_screen_width, character_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT,
                                  'Character Information')
    libtcod.console_print_rect_ex(window, 0, 2, character_screen_width, character_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT,
                                  'Level: {0}'.format(player.level.current_level))
    libtcod.console_print_rect_ex(window, 0, 3, character_screen_width, character_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT,
                                  'Experience: {0}'.format(player.level.current_xp))
    libtcod.console_print_rect_ex(window, 0, 4, character_screen_width, character_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT,
                                  'Experience to level up: {0}'.format(player.level.experience_to_next_level))
    libtcod.console_print_rect_ex(window, 0, 6, character_screen_width, character_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT,
                                  'Maximum HP: {0}'.format(player.fighter.max_hp))
    libtcod.console_print_rect_ex(window, 0, 7, character_screen_width, character_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT,
                                  'Attack: {0}'.format(player.fighter.power))
    libtcod.console_print_rect_ex(window, 0, 8, character_screen_width, character_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT,
                                  'Defense: {0}'.format(player.fighter.defense))

    x = screen_width // 2 - character_screen_width // 2
    y = screen_height // 2 - character_screen_height // 2
    libtcod.console_blit(window, 0, 0, character_screen_width,
                         character_screen_height, 0, x, y, 1.0, 0.7)

def help_screen(help_screen_width, screen_width, screen_height):
    help_items = [
        'Help (press Esc to exit)',
        '8 2 4 6 (or J K H L)   move N S W E',
        '7 9 1 3 (or Y U B N)   move diagonally',
        '. (or 5)               wait a turn',
        'I                      open inventory',
        ', (or G)               pick up item',
        'D                      drop item',
        'C                      show character screen',
        'SHIFT                  descend stairs',
        'ENTER                  (not yet implemented)'
    ]

    help_screen_height = len(help_items) + 2
    window = libtcod.console_new(help_screen_width, help_screen_height)
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_set_background_flag(window, libtcod.BKGND_OVERLAY)
    libtcod.console_set_default_background(window, libtcod.darker_grey)
    libtcod.console_rect(window, 0, 0, help_screen_width,
                              help_screen_height, True)

    for i in range(len(help_items)):
        libtcod.console_print_rect_ex(window, 1, i + 1,
                                      help_screen_width, help_screen_height,
                                      libtcod.BKGND_NONE, libtcod.LEFT,
                                      help_items[i])

    x = screen_width // 2 - help_screen_width // 2
    y = screen_height // 2 - help_screen_height // 2
    
    libtcod.console_blit(window, 0, 0, help_screen_width,
                         help_screen_height, 0, x, y, 1.0, 0.8)
