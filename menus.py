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

        temp_inv = []

        slots = [
            "main_hand", "off_hand", "head",
            "under_torso", "over_torso", "legs",
            "feet", "left_finger", "right_finger"
        ]

        # equipped items
        for i in player.inventory.items:
            for s in slots:
                if player.equipment.slots.get(s) == i:
                    if player.equipment.slots.get("main_hand") == i:
                        options.append('{0} (in main hand)'.format(i.name))
                        temp_inv.append(i)
                    elif player.equipment.slots.get("off_hand") == i:
                        options.append('{0} (in off hand)'.format(i.name))
                        temp_inv.append(i)
                    elif player.equipment.slots.get("head") == i:
                        options.append('{0} (on head)'.format(i.name))
                        temp_inv.append(i)
                    elif player.equipment.slots.get("under_torso") == i:
                        options.append('{0} (on body)'.format(i.name))
                        temp_inv.append(i)
                    elif player.equipment.slots.get("over_torso") == i:
                        options.append('{0} (on body)'.format(i.name))
                        temp_inv.append(i)
                    elif player.equipment.slots.get("legs") == i:
                        options.append('{0} (on legs)'.format(i.name))
                        temp_inv.append(i)
                    elif player.equipment.slots.get("feet") == i:
                        options.append('{0} (on feet)'.format(i.name))
                        temp_inv.append(i)
                    elif player.equipment.slots.get("left_finger") == i:
                        options.append('{0} (on left hand)'.format(i.name))
                        temp_inv.append(i)
                    elif player.equipment.slots.get("right_finger") == i:
                        options.append('{0} (on right hand)'.format(i.name))
                        temp_inv.append(i)
                    break

        # all other items
        for i in player.inventory.items:
            for s in slots:
                if player.equipment.slots.get(s) == i:
                    break
            else:
                temp_option = ""
                
                if i.item.count > 1:
                    if i.item.age is not None:
                        temp_option = "({0}) {1} ({2} turns old)".format(i.item.count, i.name, i.item.age)
                    else:
                        temp_option = "({0}) {1}".format(i.item.count, i.name)
                else:
                    if i.item.age is not None:
                        temp_option = "{0} ({1} turns old)".format(i.name, i.item.age)
                    else:
                        temp_option = i.name

                options.append(temp_option)
                temp_inv.append(i)

        player.inventory.items = temp_inv
        
    menu(con, header, options, inventory_width, screen_width, screen_height)

def main_menu(con, background_image, screen_width, screen_height, lowest_level, highest_score):
    libtcod.image_blit_2x(background_image, 0, 0, 0)

    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4,
                             libtcod.BKGND_NONE, libtcod.CENTER,
                             'Dungeon Star')
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 6),
                             libtcod.BKGND_NONE, libtcod.CENTER, "Deepest level reached: Floor " + str(lowest_level))
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 5),
                             libtcod.BKGND_NONE, libtcod.CENTER, "Largest hoard gained: " + str(highest_score) + " gold")
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 2),
                             libtcod.BKGND_NONE, libtcod.CENTER, 'Nic Gard (C) 2019')

    menu(con, '', ['Play a new game', 'Continue last game', 'Load test map', 'Quit'], 24,
         screen_width, screen_height)
    

def level_up_menu(con, header, player, menu_width, screen_width, screen_height):
    options = ['Constitution (+20 HP, from {0})'.format(player.fighter.max_hp),
               'Strength (+1 attack, from {0})'.format(player.fighter.power),
               'Agility (+1 defense, from {0})'.format(player.fighter.defense)]
    menu(con, header, options, menu_width, screen_width, screen_height)

def message_box(con, header, screen_width, screen_height):
    width = len(header)+ 2
    height = libtcod.console_get_height_rect(con, 0, 0, width, screen_height, header) + 2

    window = libtcod.console_new(width, height)
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_set_background_flag(window, libtcod.BKGND_OVERLAY)
    libtcod.console_set_default_background(window, libtcod.lighter_grey)
    libtcod.console_rect(window, 0, 0, width, height, True)
    libtcod.console_print_rect_ex(window, 1, 1, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.9)

def character_screen(player, character_screen_width, screen_width, screen_height):
    information_items = [
        'Character Information',
        'Level: {0}'.format(player.level.current_level),
        'Experience: {0}'.format(player.level.current_xp),
        'Experience to level up: {0}'.format(player.level.experience_to_next_level),
        '',
        'Maximum HP: {0}'.format(player.fighter.max_hp),
        'Attack: {0}'.format(player.fighter.power),
        'Defense: {0}'.format(player.fighter.defense),
        '',
        'Gold: {0}'.format(player.inventory.gold_carried)
    ]
    
    character_screen_height = len(information_items) + 2
    window = libtcod.console_new(character_screen_width, character_screen_height)
    libtcod.console_set_default_foreground(window, libtcod.white)

    libtcod.console_set_background_flag(window, libtcod.BKGND_OVERLAY)
    libtcod.console_set_default_background(window, libtcod.lighter_grey)
    libtcod.console_rect(window, 0, 0, character_screen_width,
                              character_screen_height, True)
    
    for i in range(len(information_items)):
        libtcod.console_print_rect_ex(window, 1, i + 1, character_screen_width,
                                      character_screen_height, libtcod.BKGND_NONE,
                                      libtcod.LEFT, information_items[i])

    x = screen_width // 2 - character_screen_width // 2
    y = screen_height // 2 - character_screen_height // 2
    libtcod.console_blit(window, 0, 0, character_screen_width,
                         character_screen_height, 0, x, y, 1.0, 0.7)

def help_screen(help_screen_width, screen_width, screen_height):
    help_items = [
        "7 8 9   Y K U",
        "",
        "4   6   H   L   move in all 8 directions",
        "",
        "1 2 3   B J N",
        "",
        '          . 5   wait a turn',
        '            I   open inventory',
        '          , G   pick up item',
        '            D   drop item',
        '            C   show character screen',
        '        SHIFT   descend stairs',
        '        ENTER   (not yet implemented)',
        '            ;   look at entity',
        "            x   butcher corpse (%)"
    ]

    help_screen_height = len(help_items) + 7
    window = libtcod.console_new(help_screen_width, help_screen_height)
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_set_background_flag(window, libtcod.BKGND_OVERLAY)
    libtcod.console_set_default_background(window, libtcod.light_grey)
    libtcod.console_rect(window, 0, 0, help_screen_width,
                              help_screen_height, True)

    libtcod.console_print_rect_ex(window, 1, 1, help_screen_width, help_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT, "Help (press Esc to exit)")
    
    libtcod.console_print_rect_ex(window, 7, 3, help_screen_width, help_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT, chr(24))
    libtcod.console_print_rect_ex(window, 7, 4, help_screen_width, help_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT, chr(25))
    libtcod.console_print_rect_ex(window, 8, 4, help_screen_width, help_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT, chr(26))
    libtcod.console_print_rect_ex(window, 6, 4, help_screen_width, help_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT, chr(27))
    libtcod.console_print_rect_ex(window, 17, 4, help_screen_width, help_screen_height,
                                  libtcod.BKGND_NONE, libtcod.LEFT, "move in cardinal directions")

    libtcod.console_set_default_foreground(window, libtcod.cyan)

    color_index = 0
    for i in range(len(help_items)):
        if color_index % 2 == 0:
            libtcod.console_set_default_foreground(window, libtcod.white)
        else:
            libtcod.console_set_default_foreground(window, libtcod.cyan)
        color_index += 1
            
        libtcod.console_print_rect_ex(window, 1, i + 6,
                                      help_screen_width, help_screen_height,
                                      libtcod.BKGND_NONE, libtcod.LEFT,
                                      help_items[i])

    x = screen_width // 2 - help_screen_width // 2
    y = screen_height // 2 - help_screen_height // 2
    
    libtcod.console_blit(window, 0, 0, help_screen_width,
                         help_screen_height, 0, x, y, 1.0, 0.8)
