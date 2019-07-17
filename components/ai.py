import tcod as libtcod
from random import randint, random
from game_messages import Message

class BasicMonster:
    def __str__(self):
        return "Basic monster AI. Hunts closest target when in FOV."
    
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
        else:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1
            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)
                    
        return results

class AggressiveMonster:
    def __init__(self, patience=20):
        self.max_patience = patience
        self.current_patience = 0
        self.seeking = False
        
    def __str__(self):
        return "Aggressive monster AI. Hunts closest target until patience runs out."
    
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            self.seeking = True
            self.current_patience = self.max_patience
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
        elif self.current_patience > 0 and self.seeking:
            self.current_patience -= 1
            if self.current_patience <= 0:
                self.seeking = False
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter.hp > 0:
                if self.current_patience < self.max_patience:
                    self.current_patience += 1
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
        else:
            if self.current_patience < self.max_patience:
                    self.current_patience += 1
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1
            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)
                    
        return results

class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def __str__(self):
        return "Confused monster AI. Walks in a random direction until no longer confused."

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name),
                                               libtcod.red)})
        return results

class DummyMonster:
    def __str__(self):
        return "Dummy monster AI. Does nothing."
    
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        return results

class StoppedMonster:
    def __init__(self, previous_ai, number_of_turns=10, chance_to_resume=None, resume_text="stopped"):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns
        self.resume_text = resume_text
        self.chance_to_resume = chance_to_resume

    def __str__(self):
        return "Stopped monster AI. Resumes previous after x turns, or with a chance to resume action."

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.chance_to_resume:
            if random() < self.chance_to_resume:
                self.owner.ai = self.previous_ai
                results.append({'message': Message(
                    'The {0} is no longer {1}!'.format(self.owner.name, self.resume_text),
                    libtcod.red)})
        elif self.number_of_turns > 0:
            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({'message': Message(
                'The {0} is no longer {1}!'.format(self.owner.name, self.resume_text),
                libtcod.red)})
        return results
