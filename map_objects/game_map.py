import copy
import tcod as libtcod
from components.door import Door, DoorPosition
from components.item import Item
from components.sign import Sign
from components.stairs import Stairs
from components.trap import Trap
from components.valuable import Valuable
from entity import Entity
from game_messages import Message
from loader_functions.data_loaders import load_test_map_tiles
from loader_functions.entity_definitions import get_item, get_monster, item_defs, monster_defs
from map_objects.rectangle import Rect
from map_objects.tile import Tile
from random import randint, choice
from random_utils import from_dungeon_level, random_choice_from_dict
from render_functions import RenderOrder

class GameMap:
    
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level
        
    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities(self, room, entities):
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 10], [5, 20]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1]], self.dungeon_level)
        
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)
        amount_of_gold = randint(0, 20 + (10 * self.dungeon_level)) + 2
        gold_passes = choice([
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 1, 1, 2
            # 1/16 for 2 piles, 1/8 for 1 pile, 13/16 for no gold
        ])

        monster_chances = {}
        for key, value in self.monster_defs.items():
            monster_chances[key] = from_dungeon_level(value.spawn_rate, self.dungeon_level)

        item_chances = {}
        for key, value in self.item_defs.items():
            item_chances[key] = from_dungeon_level(value.spawn_rate, self.dungeon_level)
        
        for i in range(number_of_monsters):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            blocked = False

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if not self.is_blocked(x, y):
                    monster_choice = random_choice_from_dict(monster_chances)
                    monster = get_monster(monster_choice, x, y)
                    entities.append(monster)
        
        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if not self.is_blocked(x, y):
                    item_choice = random_choice_from_dict(item_chances)
                    item = get_item(item_choice, x, y)
                    entities.append(item)

        for i in range(gold_passes):
            if amount_of_gold == 0:
                break
            
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if not self.is_blocked(x, y):
                    take_gold = randint(0, amount_of_gold)
                    amount_of_gold -= take_gold
                    gold = Entity("gold", x, y, '$', libtcod.gold, 'Gold',
                                  render_order=RenderOrder.GOLD,
                                  valuable=Valuable(take_gold))
                    if gold.valuable.value:
                        entities.append(gold)
                    
    def make_map(self, max_rooms, room_min_size, room_max_size,
                 map_width, map_height, player, entities):
        self.test_map = False
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            new_room = Rect(x, y, w, h)

            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                self.create_room(new_room)
                
                (new_x, new_y) = new_room.center()
                center_of_last_room_x = new_x
                center_of_last_room_y = new_y
                
                if num_rooms == 0:
                    player.x = new_x
                    player.y = new_y
                else:
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()
                    
                    if randint(0, 1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)
                
                self.place_entities(new_room, entities)
                rooms.append(new_room)
                num_rooms += 1
        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity("down_stairs", center_of_last_room_x, center_of_last_room_y, 31, libtcod.white,
                             'Stairs', render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

    def make_test_map(self, map_width, map_height, player, entities):
        self.test_map = True
        w = map_width - 2
        h = map_height - 2
        x = 1
        y = 1
        
        new_room = Rect(x, y, w, h)
        self.create_room(new_room)
        
        (new_x, new_y) = new_room.center()
        center_of_last_room_x = new_x
        center_of_last_room_y = new_y
                
        player.x = new_x
        player.y = new_y

        data = load_test_map_tiles()
        for data_y in range(len(data)):
            for data_x in range(len(data[x])):
                if data[data_y][data_x] != '':
                    piece = data[data_y][data_x]
                    if piece == "wall":
                        self.tiles[data_x][data_y].blocked = True
                        self.tiles[data_x][data_y].block_sight = True
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
                    elif piece == "trap":
                        trap_component = Trap()
                        trap = Entity("trap", data_x, data_y, " ", libtcod.red,
                                             'Trap', blocks=False, render_order=RenderOrder.TRAP,
                                      trap=trap_component)
                        entities.append(trap)
                    elif piece in item_defs:
                        item = get_item(piece, data_x, data_y)
                        entities.append(item)
                    elif piece in monster_defs:
                        monster = get_monster(piece, data_x, data_y)
                        entities.append(monster)
        
    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, entities)

        player.fighter.heal(player.fighter.max_hp // 4)
        message_log.add_message(Message('You take a moment to rest, and recover your strength.',
                                        libtcod.light_violet))
        return entities
