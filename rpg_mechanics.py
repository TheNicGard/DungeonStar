from random import randint

def get_modifier(score):
    return (score // 2) - 5

def display_ability(score):
    if get_modifier(score) >= 0:
        return str(score) + " (+" + str(get_modifier(score)) + ")"
    else:
        return str(score) + " (" + str(get_modifier(score)) + ")"

def d20():
    return randint(1, 20)

def attack_success(attack_bonus, armor_class):
    roll = d20()
    if roll != 1:
        if (roll + attack_bonus) >= armor_class or roll == 20:
            return True
    return False
        
        
    
