from random import randint

def get_modifier(score):
    return (score // 2) - 5

def display_ability(score):
    if get_modifier(score) >= 0:
        return str(score) + " (+" + str(get_modifier(score)) + ")"
    else:
        return str(score) + " (" + str(get_modifier(score)) + ")"

def die(count, side_count):
    if side_count >= 1 and count >= 1:
        total = 0
        for i in range(count):
            total += randint(1, side_count)
        return total
    else:
        return 0

def attack_success(attack_bonus, armor_class):
    roll = die(1, 20)
    if roll != 1:
        if (roll + attack_bonus) >= armor_class or roll == 20:
            return True
    return False

def str_to_dice(dice_string):
    # use later for converting values in item loading, regex
    return [[0, 0]]

def dice_to_str(dice):
    dice_string = ""
    for d in dice:
        dice_string += d[0] + "d" + d[1] + " "
    return dice_string
        
    
