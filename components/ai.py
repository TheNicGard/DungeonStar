import tcod as libtcod
from entity import get_blocking_entities_at_location, get_entities_at_location
from game_messages import Message
from random import randint, random
from rpg_mechanics import attack_success, get_modifier

def check_for_traps(monster, entities, game_map, fov_map):
    results = []
    
    entities_in_loc = get_entities_at_location(entities, monster.x, monster.y)
    for e in entities_in_loc:
        # 50% chance to set off trap
        if e.trap and attack_success(get_modifier(monster.fighter.dexterity), 10):
            if fov_map[monster.y][monster.x]:
                e.trap.set_reveal(True)
            results.extend(e.trap.trap_function(monster, **{"game_map": game_map,
                                                            "entities": entities,
                                                            "fov_map": fov_map}))

    return results

class BasicMonster:
    def __str__(self):
        return "Basic monster AI. Hunts closest target when in FOV."
    
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        
        monster = self.owner
        
        if fov_map.fov[monster.y][monster.x]:
            if monster.distance_to(target) >= 2:
                if not self.owner.fighter.is_effect("stuck"):
                    if target.fighter.is_effect("invisible"):
                        random_x = self.owner.x + randint(0, 2) - 1
                        random_y = self.owner.y + randint(0, 2) - 1
                        if random_x != self.owner.x and random_y != self.owner.y:
                            self.owner.move_towards(random_x, random_y, game_map, entities)
                    else:
                        monster.move_astar(target, entities, game_map)

                    results.extend(check_for_traps(monster, entities, game_map, fov_map))

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
        else:
            if not self.owner.fighter.is_effect("stuck"):
                random_x = self.owner.x + randint(0, 2) - 1
                random_y = self.owner.y + randint(0, 2) - 1
                if not (random_x == self.owner.x and random_y == self.owner.y):
                    self.owner.move_towards(random_x, random_y, game_map, entities)
                    results.extend(check_for_traps(monster, entities, game_map, fov_map))
                    
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
        
        if libtcod.map_is_in_fov(fov_map, monster.y, monster.x):
            self.seeking = True
            self.current_patience = self.max_patience
            if monster.distance_to(target) >= 2:
                if not self.owner.fighter.is_effect("stuck"):
                    if target.fighter.is_effect("invisible"):
                        random_x = monster.x + randint(0, 2) - 1
                        random_y = monster.y + randint(0, 2) - 1
                        if random_x != self.owner.x and random_y != self.owner.y:
                            monster.move_towards(random_x, random_y, game_map, entities)
                    else:
                        monster.move_astar(target, entities, game_map)
                    results.extend(check_for_traps(monster, entities, game_map, fov_map))
            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
        elif self.current_patience > 0 and self.seeking:
            self.current_patience -= 1
            if self.current_patience <= 0:
                self.seeking = False
            if monster.distance_to(target) >= 2:
                if not self.owner.fighter.is_effect("stuck"):
                    monster.move_astar(target, entities, game_map)
                    results.extend(check_for_traps(monster, entities, game_map, fov_map))
            elif target.fighter.hp > 0:
                if self.current_patience < self.max_patience:
                    self.current_patience += 1
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
        else:
            if self.current_patience < self.max_patience:
                    self.current_patience += 1
            if not monster.fighter.is_effect("stuck"):
                random_x = monster.x + randint(0, 2) - 1
                random_y = monster.y + randint(0, 2) - 1
                if random_x != self.owner.x and random_y != self.owner.y:
                    monster.move_towards(random_x, random_y, game_map, entities)
                    results.extend(check_for_traps(monster, entities, game_map, fov_map))
                    
        return results

class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def __str__(self):
        return "Confused monster AI. Walks in a random direction until no longer confused."

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner

        if self.number_of_turns > 0:
            if not monster.fighter.is_effect("stuck"):
                random_x = monster.x + randint(0, 2) - 1
                random_y = monster.y + randint(0, 2) - 1

                if random_x != self.owner.x and random_y != self.owner.y:
                    self.owner.move_towards(random_x, random_y, game_map, entities)
                    results.extend(check_for_traps(monster, entities, game_map, fov_map))

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
        return []

class HardStoppedMonster:
    def __init__(self, previous_ai, number_of_turns=10, resume_text="stopped"):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns
        self.resume_text = resume_text

    def __str__(self):
        return "Hard stopped monster AI. Resumes previous AI after x turns."

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner

        if self.number_of_turns > 0:
            self.number_of_turns -= 1
        else:
            monster.ai = self.previous_ai
            results.append({'message': Message(
                'The {0} is no longer {1}!'.format(monster.name, self.resume_text),
                libtcod.red)})
        return results

class SoftStoppedMonster:
    def __init__(self, previous_ai, number_of_turns=10, chance_to_resume=0.2, resume_text="stopped"):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns
        self.resume_text = resume_text
        self.chance_to_resume = chance_to_resume
        self.first_turn = True

    def __str__(self):
        return "Soft sttopped monster AI. Resumes previous AI after x turns, or with a chance to resume action."

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        
        if self.first_turn:
            self.first_turn = False
        elif self.number_of_turns != 0:
            self.number_of_turns -= 1
            if random() < self.chance_to_resume:
                monster.ai = self.previous_ai
                results.append({'message': Message(
                    'The {0} is no longer {1}!'.format(monster.name, self.resume_text),
                    libtcod.red)})
        else:
            monster.ai = self.previous_ai
            results.append({'message': Message(
                'The {0} is no longer {1}!'.format(monster.name, self.resume_text),
                libtcod.red)})

        return results

class StaticMonster:
    def __str__(self):
        return "Statuc monster AI. Attacks nearby targets, but does not move."
    
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        
        if fov_map.fov[monster.y][monster.x]:
            if target.fighter.is_effect("invisible"):
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
                
        return results

class MotherDoughAI(StaticMonster):
    def __init__(self):
        self.turns_to_spawn = 40

    def __str__(self):
        return "AI for the Mother Dough. Attacks nearby targets, and spreads sourdough starters every few turns."
    
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        
        done = False
        if self.turns_to_spawn <= 0:
            for y in [monster.y - 1, monster.y, monster.y + 1]:
                for x in [monster.x - 1, monster.x, monster.x + 1]:
                    if not (x == monster.x and y == monster.y) and not game_map.is_blocked(x, y):
                            blocking_entities = get_blocking_entities_at_location(entities, x, y)
                            if blocking_entities is None:
                                results.append({"spawn_enemy": {"name": "sourdough_starter",
                                                                "x": x, "y": y,
                                                                "mother": monster}})
                                monster.fighter.heal(10)
                                self.turns_to_spawn = 40
                                done = True
                                break
                if done:
                    break
        else:
            self.turns_to_spawn -= 1
                        
        if fov_map.fov[monster.y][monster.x]:
            if target.fighter.is_effect("invisible"):
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
                
        return results

class SourdoughAI(StaticMonster):
    def __init__(self, min_spread_time, max_spread_time):
        self.min_spread_time = min_spread_time
        self.max_spread_time = max_spread_time
        self.turns_to_spawn = randint(min_spread_time, max_spread_time)
        self.mother = None

    def reroll(self):
        self.turns_to_spawn = randint(self.min_spread_time, self.max_spread_time)
        
    def __str__(self):
        return "AI for the Sourdough Starter. Attacks nearby targets, and spreads sourdough starters more rarely than the mother dough."
    
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner
        
        done = False
        if self.turns_to_spawn <= 0:
            if self.mother and not self.mother.ai:
                results.append({"dead": monster})
            else:
                for y in [monster.y - 1, monster.y, monster.y + 1]:
                    for x in [monster.x - 1, monster.x, monster.x + 1]:
                        if not (x == monster.x and y == monster.y) and not game_map.is_blocked(x, y):
                            blocking_entities = get_blocking_entities_at_location(entities, x, y)
                            if blocking_entities is None:
                                results.append({"spawn_enemy": {"name": "sourdough_starter",
                                                                "x": x, "y": y, "mother": monster}})
                                monster.fighter.heal(10)
                                self.turns_to_spawn = 40
                                done = True
                                break
                    if done:
                        break
        else:
            self.turns_to_spawn -= 1
                        
        if fov_map.fov[monster.y][monster.x]:
            if target.fighter.is_effect("invisible"):
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
                
        return results

class NeutralMonster:
    def __init__(self, aggressive_ai):
        self.aggressive_ai = aggressive_ai
        
    def __str__(self):
        return "Neutral monster AI. Will remain neutral to the player unless attacked."
    
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        
        monster = self.owner

        if not self.owner.fighter.is_effect("stuck"):
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1
            monster.move_towards(random_x, random_y, game_map, entities)
            results.extend(check_for_traps(monster, entities, game_map, fov_map))
                    
        return results

    def become_aggressive(self):
        results = []
        

        self.owner.ai = self.aggressive_ai
        self.aggressive_ai.owner = self.owner
        
        results.append({'message': Message('The {0} become agressive!'.format(self.owner.name),
                                           libtcod.red)})
        return results
