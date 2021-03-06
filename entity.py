import tcod as libtcod
import math
from components.item import Item
from render_functions import RenderOrder

class Entity:
    def __init__(self, id, x, y, char, color, name, weight=0, blocks=False,
                 render_order = RenderOrder.CORPSE, fighter=None, ai=None,
                 item=None, inventory=None, stairs=None, level=None,
                 equipment=None, equippable=None, valuable=None, door=None,
                 animation=None, hunger=None, food=None, trap=None,
                 classification=[], sign=None, identity=None):
        self.id = id
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.weight = weight
        self.blocks = blocks
        self.render_order = render_order
        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.level = level
        self.equipment = equipment
        self.equippable = equippable
        self.valuable = valuable
        self.door = door
        self.animation = animation
        self.hunger = hunger
        self.food = food
        self.trap = trap
        self.classification = classification
        self.sign = sign
        self.identity = identity
        
        if self.fighter:
            self.fighter.owner = self
        if self.ai:
            self.ai.owner = self
        if self.item:
            self.item.owner = self
        if self.inventory:
            self.inventory.owner = self
        if self.stairs:
            self.stairs.owner = self
        if self.door:
            self.door.owner = self
        if self.level:
            self.level.owner = self
        if self.equipment:
            self.equipment.owner = self
        if self.equippable:
            self.equippable.owner = self
            if not self.item:
                item = Item(1)
                self.item = item
                self.item.owner = self
        if self.valuable:
            self.valuable.owner = self
        if self.animation:
            self.animation.owner = self
        if self.hunger:
            self.hunger.owner = self
        if self.sign:
            self.sign.owner = self
        if self.trap:
            self.trap.owner = self

    def __str__(self):
        return "Entity \'{0}\' is represented by {1} at location ({2}, {3}).".format(self.name, self.char, self.x, self.y)

    @property
    def get_name(self):
        if self.identity and not self.identity.identified:
            return self.identity.name
        return self.name

    @property
    def get_char(self):
        if self.item and self.item.light_source:
            return self.item.light_source.get_char
        return self.char

    @property
    def get_color(self):
        if self.identity and not self.identity.identified:
            return self.identity.color
        return self.color

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt((dx ** 2) + (dy ** 2))

        if distance == 0:
            return

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move_astar(self, target, entities, game_map):
        # Create a FOV map that has the dimensions of the map
        fov = libtcod.map_new(game_map.width, game_map.height)
        
        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                libtcod.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight,
                                           not game_map.tiles[x1][y1].blocked)

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                libtcod.map_set_properties(fov, entity.x, entity.y, True, False)

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = libtcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for
        # example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around
        # the map if there's an alternative path really far away
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths
            # (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y, game_map, entities)

            # Delete the path to free memory
        libtcod.path_delete(my_path)

    def flee_astar(self, predator, entities, game_map, safe_range):
        target_locations = []
        
        fov = libtcod.map_new(game_map.width, game_map.height)
        
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                libtcod.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight,
                                           not game_map.tiles[x1][y1].blocked)

        for entity in entities:
            if entity.blocks and entity != self and entity != predator:
                libtcod.map_set_properties(fov, entity.x, entity.y, True, False)

        my_path = libtcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for
        # example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around
        # the map if there's an alternative path really far away
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths
            # (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y, game_map, entities)

            # Delete the path to free memory
        libtcod.path_delete(my_path)

















        

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt((dx ** 2) + (dy ** 2))

def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            if entity.fighter:
                if entity.fighter.is_effect("invisible"):
                    return None
                else:
                    return entity
            else:
                return entity
    return None

def get_entities_at_location(entities, destination_x, destination_y):
    found_entities = []
    
    for entity in entities:
        if entity and entity.x == destination_x and entity.y == destination_y:
            found_entities.append(entity)
        
    return found_entities
