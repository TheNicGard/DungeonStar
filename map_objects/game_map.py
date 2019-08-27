import tcod as libtcod
from components.door import Door, DoorPosition

from effect import Effect
from components.equippable import Equippable

from components.identity import Identity
from components.sign import Sign
from components.stairs import Stairs
from components.trap import Trap, poison_trap, teleport_trap, hole_trap
from components.valuable import Valuable
from entity import Entity, get_entities_at_location
from game_messages import Message
from loader_functions.data_loaders import load_test_map_tiles, load_tutorial_map_tiles
from loader_functions.entity_definitions import get_item, get_monster, item_defs, monster_defs
from map_objects.rectangle import Rect
from map_objects.tile import Tile
from random import randint, random, choice
from random_utils import from_dungeon_level, random_choice_from_dict
from render_functions import RenderOrder

class GameMap:    
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level
        self.lowest_level = 64

        self.dungeon_star_level = 48
        self.spawned_dungeon_star = False
        
    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False

    def place_entities(self, room, entities):
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 15], [4, 20]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1]], self.dungeon_level)
        max_traps_per_room = from_dungeon_level([[1, 1], [2, 5]], self.dungeon_level)
        # update later to have traps per floor instead

        chance_to_spawn_monsters = 0.33
        chance_to_spawn_items = 0.40
        
        number_of_monsters = randint(1, max_monsters_per_room)
        number_of_items = randint(1, max_items_per_room)
        number_of_traps = randint(1, max_traps_per_room)
        amount_of_gold = randint(0, 20 + (10 * self.dungeon_level)) + 2

        gold_passes = 0
        if random() < 0.02:
            gold_passes = 2
        elif random() < 0.12:
            gold_passes = 1

        monster_chances = {}
        for key, value in monster_defs.items():
            monster_chances[key] = from_dungeon_level(value.spawn_rate, self.dungeon_level)

        item_chances = {}
        for key, value in item_defs.items():
            item_chances[key] = from_dungeon_level(value.spawn_rate, self.dungeon_level)

        if random() < chance_to_spawn_monsters:
            for i in range(number_of_monsters):
                x = randint(room.x1 + 1, room.x2 - 1)
                y = randint(room.y1 + 1, room.y2 - 1)

                if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                    if not self.is_blocked(x, y):
                        monster_choice = random_choice_from_dict(monster_chances)
                        monster = get_monster(monster_choice, x, y)
                        entities.append(monster)

        if random() < chance_to_spawn_items:
            for i in range(number_of_items):
                x = randint(room.x1 + 1, room.x2 - 1)
                y = randint(room.y1 + 1, room.y2 - 1)

                if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                    if not self.is_blocked(x, y):                        
                        if self.dungeon_level == self.dungeon_star_level and not self.spawned_dungeon_star:
                            self.spawned_dungeon_star = True
                            dungeon_star = get_item("dungeon_star", x, y)
                            entities.append(dungeon_star)
                        else:
                            item_choice = random_choice_from_dict(item_chances)
                            item = get_item(item_choice, x, y)
                            entities.append(item)

        for i in range(number_of_traps):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if not self.is_blocked(x, y):
                    trap_chance = random()
                    if trap_chance < .05:
                        trap_component = Trap(poison_trap)
                        trap = Entity("trap", x, y, " ", libtcod.dark_lime,
                                      'Trap', blocks=False, render_order=RenderOrder.TRAP,
                                      trap=trap_component)
                    elif trap_chance < .1:
                        trap_component = Trap(teleport_trap)
                        trap = Entity("trap", x, y, " ", libtcod.dark_fuchsia,
                                      'Trap', blocks=False, render_order=RenderOrder.TRAP,
                                      trap=trap_component)
                    elif trap_chance < .15:
                        trap_component = Trap(hole_trap)
                        trap = Entity("trap", x, y, " ", libtcod.darker_green,
                                      'Trap', blocks=False, render_order=RenderOrder.TRAP,
                                      trap=trap_component)
                    else:
                        trap_component = Trap()
                        trap = Entity("trap", x, y, " ", libtcod.red,
                                      'Trap', blocks=False, render_order=RenderOrder.TRAP,
                                      trap=trap_component)
                    entities.append(trap)

        for i in range(gold_passes):
            if amount_of_gold == 0:
                break
            
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if not self.is_blocked(x, y):
                    take_gold = randint(0, amount_of_gold)
                    amount_of_gold -= take_gold
                    if take_gold < 20:
                        gold = Entity("gold", x, y, '$', libtcod.dark_sepia, 'Copper',
                                      render_order=RenderOrder.GOLD,
                                      valuable=Valuable(take_gold))
                    elif take_gold < 75:
                        gold = Entity("gold", x, y, '$', libtcod.silver, 'Silver',
                                      render_order=RenderOrder.GOLD,
                                      valuable=Valuable(take_gold))
                    else:
                        gold = Entity("gold", x, y, '$', libtcod.gold, 'Gold',
                                      render_order=RenderOrder.GOLD,
                                      valuable=Valuable(take_gold))
                    if gold.valuable.value:
                        entities.append(gold)

    def make_test_map(self, map_width, map_height, player, entities, map_type):
        self.test_map = True
        w = map_width - 2
        h = map_height - 2
        x = 1
        y = 1
        
        new_room = Rect(x, y, w, h)
        for ax in range(x, x + w):
            for ay in range(y, y + h):
                self.tiles[ax][ay].blocked = False
                self.tiles[ax][ay].block_sight = False
        
        (new_x, new_y) = new_room.center()
                
        player.x = new_x
        player.y = new_y

        if map_type == "test_map":
            data = load_test_map_tiles()
        if map_type == "tutorial_map":
            data = load_tutorial_map_tiles()
            
        for data_y in range(len(data)):
            for data_x in range(len(data[x])):
                if data[data_y][data_x] != '':
                    piece = data[data_y][data_x]
                    if piece == "wall":
                        self.tiles[data_x][data_y].blocked = True
                        self.tiles[data_x][data_y].block_sight = True
                    elif piece == "window":
                        self.tiles[data_x][data_y].blocked = True
                        self.tiles[data_x][data_y].block_sight = False
                        self.tiles[data_x][data_y].window = True
                    if piece == "player":
                        player.x = data_x
                        player.y = data_y
                    elif piece[0:6] == "sign: ":
                        sign_component = Sign(piece[6:])
                        sign = Entity("sign", data_x, data_y, "|", libtcod.blue,
                                             'Sign', blocks=False, render_order=RenderOrder.SIGN,
                                      sign=sign_component)
                        entities.append(sign)
                    elif piece == "door":
                        door_component = Door(False, DoorPosition.VERTICAL)
                        door = Entity("door", data_x, data_y, "+", libtcod.lightest_grey,
                                             'Door', blocks=True, render_order=RenderOrder.DOOR,
                                      door=door_component)
                        door.door.close_door(self.tiles[data_x][data_y])
                        entities.append(door)
                    elif piece == "glass_door":
                        self.tiles[data_x][data_y].window = True
                        door_component = Door(False, DoorPosition.VERTICAL, True)
                        door = Entity("door", data_x, data_y, "+", libtcod.dark_blue,
                                             'Door', blocks=True, render_order=RenderOrder.DOOR,
                                      door=door_component)
                        door.door.close_door(self.tiles[data_x][data_y])
                        entities.append(door)
                    elif piece == "trap":
                        trap_component = Trap()
                        trap = Entity("trap", data_x, data_y, " ", libtcod.red,
                                      'Trap', blocks=False, render_order=RenderOrder.TRAP,
                                      trap=trap_component)
                        entities.append(trap)
                    elif piece == "poison_trap":
                        trap_component = Trap(poison_trap)
                        trap = Entity("trap", data_x, data_y, " ", libtcod.dark_lime,
                                      'Poison Trap', blocks=False, render_order=RenderOrder.TRAP,
                                      trap=trap_component)
                        entities.append(trap)
                    elif piece == "teleport_trap":
                        trap_component = Trap(teleport_trap)
                        trap = Entity("trap", data_x, data_y, " ", libtcod.dark_fuchsia,
                                      'Telportation Trap', blocks=False, render_order=RenderOrder.TRAP,
                                      trap=trap_component)
                        entities.append(trap)
                    elif piece == "hole_trap":
                        trap_component = Trap(hole_trap)
                        trap = Entity("trap", data_x, data_y, " ", libtcod.darker_green,
                                      'Hole Trap', blocks=False, render_order=RenderOrder.TRAP,
                                      trap=trap_component)
                        entities.append(trap)
                    elif piece in item_defs:
                        item = get_item(piece, data_x, data_y)
                        entities.append(item)
                    elif piece in monster_defs:
                        monster = get_monster(piece, data_x, data_y)
                        entities.append(monster)
        
    def next_floor(self, player, message_log, constants, downwards, took_stairs=True):
        if downwards:
            self.dungeon_level += 1
        else:
            self.dungeon_level -= 1
        
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, entities, downwards)

        if took_stairs:
            player.fighter.heal(player.fighter.max_hp // 5)
            message_log.add_message(Message('You take a moment to rest, and recover your strength.',
                                            libtcod.light_violet))
            
        return entities
    
    def vline(self, x, y1, y2):
        if y1 > y2:
            y1,y2 = y2,y1
            
        for y in range(y1,y2+1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            
    def vline_up(self, x, y):
        while y >= 0 and self.tiles[x][y].blocked == True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            y -= 1
 
    def vline_down(self, x, y):
        while y < self.height and self.tiles[x][y].blocked == True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            y += 1
 
    def hline(self, x1, y, x2):
        if x1 > x2:
            x1,x2 = x2,x1
            
        for x in range(x1,x2+1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
 
    def hline_left(self, x, y):
        while x >= 0 and self.tiles[x][y].blocked == True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            x -= 1
 
    def hline_right(self, x, y):
        while x < self.width and self.tiles[x][y].blocked == True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            x += 1

    def make_map(self, max_rooms, room_min_size, room_max_size,
                 map_width, map_height, player, entities, downwards):
        self.test_map = False
        rooms = []
        full_rooms = False

        bsp = libtcod.bsp.BSP(x=0, y=0, width=map_width - 1, height=map_height - 1)
        bsp.split_recursive(
            depth=5,
            min_width=room_min_size + 1,
            min_height=room_min_size + 1,
            max_horizontal_ratio=1.5,
            max_vertical_ratio=1.5,
        )
        
        center_of_last_room_x = None
        center_of_last_room_y = None

        rooms_list = []

        # In pre order, leaf nodes are visited before the nodes that connect them.
        for node in bsp.inverted_level_order():
            if node.children:
                left, right = node.children
                node.x = min(left.x, right.x)
                node.y = min(left.y, right.y)
                node.w = max(left.x + left.w, right.x + right.w) - node.x
                node.h = max(left.y + left.h, right.y + right.h) - node.y
                
                if node.horizontal:
                    if left.x + left.w - 1 < right.x or right.x + right.w - 1 < left.x:
                        x1 = randint(left.x, left.x + left.w - 1)
                        x2 = randint(right.x, right.x + right.w - 1)
                        y = randint(left.y + left.h, right.y)

                        self.vline_up(x1, y - 1)
                        self.hline(x1, y, x2)
                        self.vline_down(x2, y + 1)
                        
                    else:
                        minx = max(left.x, right.x)
                        maxx = min(left.x + left.w - 1, right.x + right.w - 1)
                        x = randint(minx, maxx)
                        
                        # catch out-of-bounds attempts
                        while x > map_width - 1:
                            x -= 1
                            
                        self.vline_down(x, right.y)
                        self.vline_up(x, right.y - 1)
 
                else:
                    if left.y + left.h - 1 < right.y or right.y + right.h - 1 < left.y:
                        y1 = randint(left.y, left.y + left.h - 1)
                        y2 = randint(right.y, right.y + right.h - 1)
                        x = randint(left.x + left.w, right.x)
                        
                        self.hline_left(x - 1, y1)
                        self.vline(x, y1, y2)
                        self.hline_right(x + 1, y2)
                    else:
                        miny = max(left.y, right.y)
                        maxy = min(left.y + left.h - 1, right.y + right.h - 1)
                        y = randint(miny, maxy)
                        
                        # catch out-of-bounds attempts
                        while y > map_height - 1:
                            y -= 1

                        self.hline_left(right.x - 1, y)
                        self.hline_right(right.x, y)
                    
            else:
                min_x = node.x + 1
                min_y = node.y + 1
                max_x = node.x + node.width - 1
                max_y = node.y + node.height - 1

                if max_x == map_width - 1:
                    max_x -= 1
                if max_y == map_height - 1:
                    max_y -= 1
                
                if not full_rooms:
                    min_x = randint(min_x, max_x - room_min_size + 1)
                    min_y = randint(min_y, max_y - room_min_size + 1)
                    max_x = randint(min_x + room_min_size - 2, max_x)
                    max_y = randint(min_y + room_min_size - 2, max_y)

                node.x = min_x
                node.y = min_y
                node.w = max_x - min_x + 1
                node.h = max_y - min_y + 1

                for x in range(min_x, max_x + 1):
                    for y in range(min_y, max_y + 1):
                        self.tiles[x][y].blocked = False
                        self.tiles[x][y].block_sight = False
                    
                new_room = Rect(node.x, node.y, node.w, node.h)
                rooms_list.append(new_room)
                
                (new_x, new_y) = new_room.center()
                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

        # wall off map from exiting bounds
        for x in range(0, self.width):
            self.tiles[x][0].blocked = True
            self.tiles[x][0].block_sight = True
            self.tiles[x][self.height - 1].blocked = True
            self.tiles[x][self.height - 1].block_sight = True
        for y in range(0, self.height):
            self.tiles[0][y].blocked = True
            self.tiles[0][y].block_sight = True
            self.tiles[self.width - 1][y].blocked = True
            self.tiles[self.width - 1][y].block_sight = True
                
        player_room = choice(rooms_list)
        (player.x, player.y) = player_room.center()

        for r in rooms_list:
            self.place_entities(r, entities)
            rooms.append(r)
                
        entities_blocking_stairs = get_entities_at_location(entities, center_of_last_room_x, center_of_last_room_y)
        for e in entities_blocking_stairs:
            if e.id == "player":
                random_x = e.x + randint(0, 2) - 1
                random_y = e.y + randint(0, 2) - 1
                if random_x != e.x and random_y != e.y:
                    e.move_towards(random_x, random_y, game_map, entities)

                    while e.x == center_of_last_room_x and e.y == center_of_last_room_y:
                        random_x = e.x + randint(0, 2) - 1
                        random_y = e.y + randint(0, 2) - 1
                        if random_x != e.x and random_y != e.y:
                            e.move_towards(random_x, random_y, game_map, entities)
            else:
                entities.remove(e)

        if downwards:
            return_stairs_component = Stairs(self.dungeon_level - 1, False)
            return_stairs = Entity("up_stairs", player.x, player.y, 30,
                                   libtcod.white, 'Stairs (up)', render_order=RenderOrder.STAIRS,
                                   stairs=return_stairs_component)
        else:
            return_stairs_component = Stairs(self.dungeon_level + 1, True)
            return_stairs = Entity("down_stairs", player.x, player.y, 31,
                                   libtcod.white, 'Stairs (downwards)', render_order=RenderOrder.STAIRS,
                                   stairs=return_stairs_component)
        entities.append(return_stairs)
                
        stairs_component = Stairs(self.dungeon_level + 1, True)
        stairs = Entity("down_stairs", center_of_last_room_x, center_of_last_room_y, 31,
                        libtcod.white, 'Stairs (downwards)', render_order=RenderOrder.STAIRS,
                        stairs=stairs_component)

        entities.append(stairs)
