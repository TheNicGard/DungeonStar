import tcod as libtcod

from rpg_mechanics import display_ability

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

def format_weight(weight_int, count):
    weight = weight_int * count
    return str(weight // 10) + "." + str(weight % 10) + chr(169)
    
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
                    temp_str = ""
                    if i.equippable.enchantment > 0:
                        temp_str += ("+" + str(i.equippable.enchantment) + " ")
                    elif i.equippable.enchantment < 0:
                        temp_str += str(i.equippable.enchantment) + " "
                    temp_str += i.get_name
                    if player.equipment.slots.get("main_hand") == i:
                        temp_str +=  " (in main hand)"
                    elif player.equipment.slots.get("off_hand") == i:
                        temp_str +=  " (in off hand)"
                    elif player.equipment.slots.get("head") == i:
                        temp_str +=  " (on head)"
                    elif player.equipment.slots.get("under_torso") == i:
                        temp_str +=  " (on body)"
                    elif player.equipment.slots.get("over_torso") == i:
                        temp_str +=  " (over body)"
                    elif player.equipment.slots.get("legs") == i:
                        temp_str +=  " (on legs)"
                    elif player.equipment.slots.get("feet") == i:
                        temp_str +=  " (on feet)"
                    elif player.equipment.slots.get("left_finger") == i:
                        temp_str +=  " (on left hand)"
                    elif player.equipment.slots.get("right_finger") == i:
                        temp_str +=  " (on right hand)"

                    #weight = str(i.weight) + chr(169)
                    weight = format_weight(i.weight, i.item.count)
                    offset = inventory_width - (4 + len(temp_str) + len(weight))
                    temp_str += (' ' * offset) + weight
                    
                    options.append(temp_str)
                    temp_inv.append(i)
                    break

        # all other items
        for i in player.inventory.items:
            for s in slots:
                if player.equipment.slots.get(s) == i:
                    break
            else:
                temp_str = ""
                
                if i.item.count > 1:
                    if i.item.age is not None:
                        temp_str = "({0}) {1} ({2} turns old)".format(i.item.count, i.get_name, i.item.age)
                    else:
                        temp_str = "({0}) {1}".format(i.item.count, i.get_name)
                else:
                    if i.item.age is not None:
                        temp_str = "{0} ({1} turns old)".format(i.get_name, i.item.age)
                    else:
                        if i.item.chargeable:
                            temp_str = i.get_name + " *" + str(i.item.chargeable.charge) + ":" + str(i.item.chargeable.max_charge) + '*'
                        elif i.item.light_source:
                            temp_str = i.get_name + " ("
                            if i.item.light_source.get_light > 0:
                                temp_str += "lit)"
                            else:
                                temp_str += "unlit)"
                        else:
                            temp_str = i.get_name

                weight = format_weight(i.weight, i.item.count)
                offset = inventory_width - (4 + len(temp_str) + len(weight))
                temp_str += (' ' * offset) + weight

                options.append(temp_str)
                temp_inv.append(i)

        player.inventory.items = temp_inv
        
    menu(con, header, options, inventory_width, screen_width, screen_height)

def main_menu(con, background_image, screen_width, screen_height, game):
    libtcod.image_blit_2x(background_image, 0, 0, 0)

    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4,
                             libtcod.BKGND_NONE, libtcod.CENTER,
                             'Dungeon Star')
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 6),
                             libtcod.BKGND_NONE, libtcod.CENTER, "Deepest level reached: Floor " + str(game.lowest_level))
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 5),
                             libtcod.BKGND_NONE, libtcod.CENTER, "Largest hoard gained: " + str(game.high_score) + " gold")
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 2),
                             libtcod.BKGND_NONE, libtcod.CENTER, 'Nic Gard (C) 2019')

    menu(con, '', ['Play a new game', 'Continue last game', "Play Tutorial", 'Quit'], 24,
         screen_width, screen_height)
    

def level_up_menu(con, header, player, menu_width, screen_width, screen_height):
    options = [
        'Strength (from {0})'.format(player.fighter.strength),
        'Dexterity (from {0})'.format(player.fighter.dexterity),
        'Constitution (from {0})'.format(player.fighter.constitution),
        'Intelligence (from {0})'.format(player.fighter.intelligence),
        'Wisdom (from {0})'.format(player.fighter.wisdom),
        'Charisma (from {0})'.format(player.fighter.charisma)
    ]
    menu(con, header, options, menu_width, screen_width, screen_height)

def confirmation_menu(con, header, menu_width, screen_width, screen_height):
    header_height = libtcod.console_get_height_rect(con, 0, 0, menu_width, screen_height, header)
    height = 2 + header_height

    x = int(screen_width / 2 - menu_width / 2)
    y = int(screen_height / 2 - height / 2)

    window = libtcod.console_new(menu_width, height)
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_set_background_flag(window, libtcod.BKGND_OVERLAY)
    libtcod.console_set_default_background(window, libtcod.lighter_grey)
    libtcod.console_rect(window, 0, 0, menu_width, height, True)
    
    libtcod.console_print_rect_ex(window, 0, 0, menu_width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
    libtcod.console_print_ex(window, 0, header_height, libtcod.BKGND_NONE, libtcod.LEFT, '(y) Yes')
    libtcod.console_print_ex(window, 0, header_height + 1, libtcod.BKGND_NONE, libtcod.LEFT, '(n) No')

    libtcod.console_blit(window, 0, 0, menu_width, height, 0, x, y, 1.0, 0.9)

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
        'Maximum HP: {0}'.format(player.fighter.max_hp),
        '',
        "Strength:     {0}".format(display_ability(player.fighter.strength)),
        "Dexterity:    {0}".format(display_ability(player.fighter.dexterity)),
        "Constitution: {0}".format(display_ability(player.fighter.constitution)),
        "Intelligence: {0}".format(display_ability(player.fighter.intelligence)),
        "Wisdom:       {0}".format(display_ability(player.fighter.wisdom)),
        "Charisma:     {0}".format(display_ability(player.fighter.charisma)),
        '',
        "Armor class: {0}".format(player.fighter.armor_class),
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
                         character_screen_height, 0, x, y, 1.0, 1.0)

def help_screen(help_screen_width, screen_width, screen_height):
    help_items = [
        "7 8 9   y k u",
        "",
        "4   6   h   l   move in all 8 directions",
        "",
        "1 2 3   b j n",
        "",
        '          . 5   wait a turn',
        '            i   open inventory',
        '          , g   pick up item',
        '            d   drop item',
        '          TAB   show character screen',
        '            >   descend stairs',
        '            <   ascend stairs',
        '            ;   look at entity',
        "            x   butcher corpse (%)"
        "",
        "     Ctrl + f   toggle fullscreen"
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
