import tcod as libtcod
from components.item import Item
from game_messages import Message
from game_states import GameStates
from item_functions import heal
from random import random
from render_functions import RenderOrder

def kill_player(player, game):
    player.char = '%'
    player.color = libtcod.dark_red
    new_high_score = game.high_score
    if player.inventory.gold_carried > game.high_score:
        new_high_score = player.inventory.gold_carried

    game.high_score = new_high_score

    for i in player.inventory.items:
        if i.identity:
            i.identity.identify()

    return Message('You died with {0} gold!'.format(player.inventory.gold_carried),
                   libtcod.red), GameStates.PLAYER_DEAD

def kill_monster(monster, fov_map):
    death_message = None

    if fov_map.fov[monster.y][monster.x]:
        death_message = Message('{0} is dead!'.format(monster.name.capitalize()), libtcod.orange)

    if monster.id == "jelly":
        item_component = Item(1, max_age=100, use_function=heal, amount = 15)
        monster.item = item_component
        monster.item.owner = monster
        monster.char = '%'
        monster.blocks = False
        monster.fighter = None
        monster.ai = None
        monster.name = 'remains of ' + monster.name
        monster.render_order = RenderOrder.CORPSE
    elif monster.id != "dummy":        
        if random() < monster.fighter.chance_to_drop_corpse:
            monster.char = '%'
            monster.color = libtcod.dark_red
            monster.blocks = False
            monster.fighter = None
            monster.ai = None
            monster.name = 'remains of ' + monster.name
            monster.render_order = RenderOrder.CORPSE
            monster.classification.append("corpse")
        else:
            monster.char = ','
            monster.color = libtcod.dark_red
            monster.blocks = False
            monster.fighter = None
            monster.ai = None
            monster.name = 'bits of ' + monster.name
            monster.render_order = RenderOrder.CORPSE
            monster.classification.append("corpse_bits")

    return death_message
