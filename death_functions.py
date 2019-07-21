import tcod as libtcod
from components.item import Item
from game_messages import Message
from game_states import GameStates
from item_functions import heal
from render_functions import RenderOrder

def kill_player(player):
    player.char = '%'
    player.color = libtcod.dark_red

    return Message('You died with {0} gold!'.format(player.inventory.gold_carried),
                   libtcod.red), GameStates.PLAYER_DEAD

def kill_monster(monster):
    death_message = Message('{0} is dead!'.format(monster.name.capitalize()), libtcod.orange)

    if monster.id == "jelly":
        item_component = Item(1, use_function=heal, amount = 15)
        monster.item = item_component
        monster.item.owner = monster
        monster.char = '%'
        monster.blocks = False
        monster.fighter = None
        monster.ai = None
        monster.name = 'remains of ' + monster.name
        monster.render_order = RenderOrder.CORPSE
    elif monster.id != "dummy":
        monster.char = '%'
        monster.color = libtcod.dark_red
        monster.blocks = False
        monster.fighter = None
        monster.ai = None
        monster.name = 'remains of ' + monster.name
        monster.render_order = RenderOrder.CORPSE

    return death_message
