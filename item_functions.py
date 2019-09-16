import tcod as libtcod
from components.ai import ConfusedMonster, StaticMonster, HardStoppedMonster, SoftStoppedMonster, NeutralMonster
from effect import Effect, tick_invisible, tick_poison, tick_regeneration, tick_detect_aura, tick_detect_items, tick_stuck
from fov_functions import initialize_fov
from game_messages import Message
from random import randint
from rpg_mechanics import attack_success, die, get_modifier

def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False,
                        'message': Message('You are already at full health!',
                                           libtcod.yellow)})
    else:
        entity.fighter.heal(amount)
        results.append({"consumed": item,
                        'message': Message('Your wounds start to feel better!',
                                           libtcod.green)})
    return results

def poison(*args, **kwargs):
    entity = args[0]
    turns = kwargs.get('turns')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    # TODO: change this to be a general roll later
    if attack_success(get_modifier(entity.fighter.constitution), 10) or entity.fighter.is_effect("poison_resistance"):
        if not entity.ai:
            results.append({"consumed": True, "message": Message(
                'You resisted the poison!', libtcod.green)})
    else:
        entity.fighter.effects.effects["poison"] = Effect(True, turns, tick_poison)
        if not entity.ai:
            results.append({"consumed": item,
                            'message': Message('You start to feel ill!',
                                               libtcod.dark_purple)})
        
    return results

def poison_resistance(*args, **kwargs):
    entity = args[0]
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    entity.fighter.effects.effects["poison_resistance"] = Effect(False, 0, None)
    results.append({"consumed": item,
                    'message': Message('Your blood feels thick!',
                                       libtcod.green)})
    return results

def cure_poison(*args, **kwargs):
    entity = args[0]
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    entity.fighter.effects.effects["poison"] = Effect(True, 0, tick_poison)
    results.append({"consumed": item,
                    'message': Message('Your sickness dissipates!',
                                       libtcod.green)})
    return results

def invisible(*args, **kwargs):
    entity = args[0]
    turns = kwargs.get('turns')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    entity.fighter.effects.effects["invisible"] = Effect(True, turns, tick_invisible)
    results.append({"consumed": item,
                    'message': Message('Light starts to pass through your body!',
                                       libtcod.green)})
    return results

def regeneration(*args, **kwargs):
    entity = args[0]
    turns = kwargs.get('turns')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    entity.fighter.effects.effects["regeration"] = Effect(True, turns, tick_regeneration)
    results.append({"consumed": item})
    
    return results

def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and fov_map.fov[entity.y][entity.x]:
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({"consumed": item, 'target': target, 'message': Message('A lightning bolt strikes the {0} with a loud thunder! The damage is {1}.'.format(target.name, damage))})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({'consumed': False, 'target': None, 'message': Message('No enemy is close enough to strike.', libtcod.red)})

    return results

def cast_fireball(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    if not fov_map.fov[target_y][target_x]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    results.append({"consumed": item, 'message': Message('The fireball explodes, burning everything within {0} tiles!'.format(radius), libtcod.orange)})

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'message': Message('The {0} gets burned for {1} hit points.'.format(entity.name, damage), libtcod.orange)})
            results.extend(entity.fighter.take_damage(damage))

    return results

def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    if not fov_map.fov[target_y][target_x]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            if isinstance(entity.ai, StaticMonster):
                results.append({"consumed": item, 'message': Message('The {0} cannot be confused!'.format(entity.name), libtcod.yellow)})
                break
            else:
                confused_ai = ConfusedMonster(entity.ai, 10)

                confused_ai.owner = entity
                entity.ai = confused_ai

                results.append({"consumed": item, 'message': Message('The eyes of the {0} look vacant, as he starts to stumble around!'.format(entity.name), libtcod.light_green)})
                break
    else:
        results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results

def cast_stun(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    if not fov_map.fov[target_y][target_x]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            if isinstance(entity.ai, StaticMonster):
                results.append({"consumed": item, 'message': Message('The {0} cannot be stunned!'.format(entity.name), libtcod.yellow)})
                break
            else:
                stopped_ai = HardStoppedMonster(entity.ai, number_of_turns=5, resume_text="stunned")
                
                stopped_ai.owner = entity
                entity.ai = stopped_ai

                results.append({"consumed": item, 'message': Message('The eyes of the {0} look shocked, as he stops in his tracks!'.format(entity.name), libtcod.light_green)})
                break
    else:
        results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results

def cast_sleep(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    if not fov_map.fov[target_y][target_x]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            if isinstance(entity.ai, StaticMonster):
                results.append({"consumed": item, 'message': Message('The {0} cannot be put to sleep!'.format(entity.name), libtcod.yellow)})
                break
            else:
                stopped_ai = SoftStoppedMonster(entity.ai, number_of_turns=10, resume_text="asleep")

                stopped_ai.owner = entity
                entity.ai = stopped_ai

                results.append({"consumed": item, 'message': Message('The eyelids of the {0} look drop, as he falls over cold!'.format(entity.name), libtcod.light_green)})
                break
    else:
        results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results

def cast_greed(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    if not fov_map.fov[target_y][target_x]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai and entity.fighter:
            entity.fighter.effects.effects["golden"] = Effect(False, -1, None)
            results.append({"consumed": item, 'message': Message(
                'The body of the {0} glimmers!'.format(entity.name), libtcod.light_green)})
            break
    else:
        results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results

def cast_detect_traps(*args, **kwargs):
    entities = kwargs.get('entities')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")
    
    results = []

    traps_found = False
    
    for e in entities:
        if e.trap and not e.trap.revealed:
            e.trap.set_reveal(True)
            traps_found = True
    if traps_found:
        results.append({"consumed": True, "message": Message("You become aware of the presence of traps on this floor!", libtcod.white)})
    else:
        results.append({"consumed": True, "message": Message("You couldn't detect any traps!", libtcod.white)})
    
    return results

def cast_detect_stairs(*args, **kwargs):
    entities = kwargs.get('entities')
    game_map = kwargs.get('game_map')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")
    
    results = []

    stairs_found = False
    
    for e in entities:
        if e.stairs and not game_map.tiles[e.x][e.y].explored:
            game_map.tiles[e.x][e.y].explored = True
            stairs_found = True
    if stairs_found:
        results.append({"consumed": True, "message": Message("You become aware of the stairs on this floor!", libtcod.white)})
    else:
        results.append({"consumed": True, "message": Message("You couldn't detect any stairs!", libtcod.white)})
    
    return results

def cast_random_teleportation(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    game_map = kwargs.get('game_map')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")
    
    results = []

    while True:
        x = randint(0, game_map.width - 1)
        y = randint(0, game_map.height - 1)

        if not game_map.is_blocked(x, y) and not any([entity for entity in entities if entity.x == x and entity.y == y]):
            caster.x = x
            caster.y = y
            results.append({"consumed": item, 'message': Message('You teleported!', libtcod.purple), "teleport": True})
            break

    return results

def cast_blink(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    game_map = kwargs.get("game_map")
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")
    
    results = []

    if not fov_map.fov[target_y][target_x]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
    elif game_map.is_blocked(target_x, target_y) or any([entity for entity in entities if entity.x == target_x and entity.y == target_y]):
        results.append({'consumed': False, 'message': Message("You can't seem to blink there.", libtcod.yellow)})
    else:
        caster.x = target_x
        caster.y = target_y
        results.append({"consumed": item, 'message': Message('You blinked!', libtcod.purple), "teleport": True})

    return results

def cast_pacify(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    if not fov_map.fov[target_y][target_x]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            if entity.fighter.can_be_pacified == False:
                results.append({"consumed": item, 'message': Message('The {0} cannot be pacified!'.format(entity.name), libtcod.yellow)})
                break
            else:
                neutral_ai = NeutralMonster(entity.ai)
                neutral_ai.owner = entity
                entity.ai = neutral_ai

                results.append({"consumed": item, 'message': Message('The {0} has been pacified!'.format(entity.name), libtcod.light_green)})
                break
    else:
        results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results

def cast_force_bolt(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    if not fov_map.fov[target_y][target_x]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            damage = die(1, 12)
            results.append({"consumed": item, 'message': Message('The magic bolt deals {1} hit points of damage to {0}.'.format(entity.name, damage), libtcod.crimson)})
            results.extend(entity.fighter.take_damage(damage))
            break
    else:
        results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results

def cast_death(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    if not fov_map.fov[target_y][target_x]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            damage = 9999
            results.append({"consumed": item, 'message': Message('The {0} turns to dust!'.format(entity.name, damage), [143, 191, 0])})
            results.extend(entity.fighter.take_damage(damage))
            break
    else:
        results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results

def cast_mapping(*args, **kwargs):
    game_map = kwargs.get('game_map')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    all_tiles_explored = True
    
    for x in range(0, game_map.width):
        for y in range(0, game_map.height):
            if not game_map.tiles[x][y].explored:
                all_tiles_explored = False
                break

    if all_tiles_explored:
        results.append({"message": Message("You've already explored the whole map!", libtcod.yellow)})
    else:
        for x in range(0, game_map.width):
            for y in range(0, game_map.height):
                game_map.tiles[x][y].explored = True

    results.append({"consumed": True, "teleport": True})

    return results

def cast_identify_item(*args, **kwargs):
    results = []

    results.append({"identify_menu": True, "consumed": True})

    return results

def cast_charge_item(*args, **kwargs):
    results = []
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results.append({"charge_menu": True, "consumed": True})

    return results

def cast_detect_aura(*args, **kwargs):
    entity = args[0]
    turns = kwargs.get('turns')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    entity.fighter.effects.effects["detect_aura"] = Effect(True, turns, tick_detect_aura)
    results.append({"consumed": item})

    return results

def cast_detect_items(*args, **kwargs):
    entity = args[0]
    turns = kwargs.get('turns')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    entity.fighter.effects.effects["detect_items"] = Effect(True, turns, tick_detect_items)
    results.append({"consumed": item})

    return results

def cast_make_invisible(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')
    turns = kwargs.get('turns')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    if not fov_map.fov[target_y][target_x]:
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.fighter:
            entity.fighter.effects.effects["invisible"] = Effect(True, turns, tick_invisible)
            if not entity.ai:
                results.append({"consumed": item,
                                'message': Message('Light starts to pass through your body!',
                                                   libtcod.green)})
                break
            else:
                results.append({"consumed": item,
                                'message': Message('The {0} disappears!'.format(entity.name),
                                                   libtcod.yellow)})
                break
    else:
        results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results

def cast_downwards_exit(*args, **kwargs):
    caster = args[0]
    game_map = kwargs.get('game_map')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")
    
    results = []

    results.append({"consumed": item, "downwards_exit": True})

    return results

def stuck(*args, **kwargs):
    entity = args[0]
    turns = kwargs.get('turns')
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    attack_success(get_modifier(entity.fighter.constitution), 10)
    
    entity.fighter.effects.effects["stuck"] = Effect(True, turns, tick_stuck)
    results.append({"consumed": item})
    if not entity.ai:
        results.append({'message': Message('You are caught in the trap!',
                                           libtcod.dark_grey)})
        
    return results

def amnesia(*args, **kwargs):
    target = args[0]
    item = None
    if kwargs.get("item"):
        item = kwargs.get("item")

    results = []

    # TODO: change this to be a general roll later
    if attack_success(get_modifier(target.fighter.wisdom), 10):
        results.append({"consumed": item, 'message': Message("You feel... buzzed?", libtcod.white)})
    else:
        results.append({"consumed": item, 'message': Message("Your memory gets fuzzy...", [240, 0, 190]), "forget_map": True})

    return results
