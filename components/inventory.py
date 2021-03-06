import tcod as libtcod
from components.identity import identify_item_in_list
from game_messages import Message
from random import randint

class Inventory:
    def __init__(self, capacity, gold_carried=0):
        self.capacity = capacity
        self.items = []
        if gold_carried >= 0:
            self.gold_carried = gold_carried

    @property
    def current_weight(self):
        weight = 0
        for i in self.items:
            weight += (i.weight * i.item.count)
        return weight
            
    def add_item(self, item):
        results = []

        if item.valuable:
            results.append({
                'gold_added': item,
                'message': Message('You pick up {0} gold!'.format(item.valuable.value), libtcod.gold)
            })
            self.gold_carried += item.valuable.value
        else:
            if self.current_weight + item.weight > self.capacity:
                results.append({
                    'item_added': None,
                    'message': Message('You cannot carry any more!', libtcod.yellow)
                })
            else:
                results.append({
                    'item_added': item,
                    'message': Message('You pick up the {0}!'.format(item.get_name), libtcod.blue)
                })

                matching_entry = None
                for i in self.items:
                    if i.id == item.id:
                        matching_entry = i
                if matching_entry and not (matching_entry.equippable or (matching_entry.item and (matching_entry.item.chargeable or matching_entry.item.light_source))):
                    matching_entry.item.count += item.item.count
                else:
                    self.items.append(item)
                    
        return results

    def use(self, item_entity, **kwargs):
        results = []

        identities = kwargs.get("identities")

        item_component = item_entity.item

        if item_component.use_function is None:
            equippable_component = item_entity.equippable
            food_component = item_entity.food
            light_component = item_entity.item.light_source

            if equippable_component:
                results.append({'equip': item_entity})
            elif food_component:
                results.extend(self.owner.hunger.eat(item_entity))
            elif light_component:
                if light_component.lit:
                    light_component.lit = not light_component.lit
                    results.append({'message': Message('You unlight the {0}.'.format(item_entity.get_name)), 'light_removed': light_component})
                else:
                    if light_component.duration <= 0:
                        results.append({'message': Message('The {0} could not be lit!'.format(item_entity.get_name), libtcod.yellow)})
                    else:
                        results.append({'message': Message('You light the {0}.'.format(item_entity.get_name)), 'light_added': light_component})
                        light_component.lit = not light_component.lit
            else:
                results.append({'message': Message('The {0} cannot be used!'.format(
                item_entity.get_name), libtcod.yellow)})

            for item_use_result in results:
                if item_use_result.get('food_eaten'):
                    self.remove_item(item_entity, 1)
        else:
            if item_component.chargeable and item_component.chargeable.charge == 0:
                results.append({'message': Message('The {0} is out of charges!'.format(item_entity.get_name))})
            else:
                if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                    results.append({'targeting': item_entity})
                else:
                    # I'm told by pyflakes this is incorrect syntax, but it only works with the ** ?
                    kwargs = {**item_component.function_kwargs, **kwargs}
                    kwargs["item"] = item_entity
                    item_use_results = item_component.use_function(self.owner, **kwargs)

                    for item_use_result in item_use_results:
                        if item_use_result.get('consumed'):
                            if item_component.chargeable:
                                item_component.chargeable.charge -= 1
                            else:
                                self.remove_item(item_entity, 1)

                    results.extend(item_use_results)

                if item_entity.identity and item_entity.identity.identify_on_use and not item_entity.identity.identified:
                    self.identify_item(item_entity, identities)
            
        return results

    def remove_item(self, item, count=1):
        matching_entry = None
        for i in self.items:
            if i.id == item.id:
                matching_entry = i
                break
        if matching_entry:
            if count >= matching_entry.item.count:
                self.items.remove(matching_entry)
            else:
                matching_entry.item.count -= count
        else:
            self.items.remove(item)

    def drop_item(self, item):
        results = []

        if hasattr(self.owner.equipment, "is_equipped") and self.owner.equipment.is_equipped(item):
            self.owner.equipment.toggle_equip(item)
            
        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item, count=item.item.count)
        results.append({'item_dropped': item})
        if not self.owner.ai:
            results.append({'message': Message('You dropped the {0}.'.format(item.get_name),
                                               libtcod.yellow)})

        return results

    def identify_item(self, item, identities):
        results = []

        if item.identity and not item.identity.identified:
            identify_item_in_list(item, identities)
            results.append({'item_identified': item})
            if not self.owner.ai:
                results.append({'message': Message('You identified the {0}.'.format(item.get_name),
                                                   libtcod.lightest_grey)})
        else:
            results.append({"message": Message('The {0} is already identified!'.format(item.get_name),
                                               libtcod.yellow)})
        return results

    def charge_item(self, item):
        results = []

        if item.item.chargeable:
            item.item.chargeable.recharge(randint(4, 8))
            results.append({'item_charged': item, "consumed": True})
            if not self.owner.ai:
                results.append({'message': Message('You charged the {0}.'.format(item.get_name),
                                                   libtcod.peach)})
        else:
            results.append({"message": Message('The {0} cannot be sealed!'.format(item.get_name),
                                                   libtcod.yellow),
                            "consumed": False})
            
        return results

    def enchant_item(self, item):
        results = []

        if item.equippable:
            item.equippable.enchantment += 1
            results.append({'message': Message('The {0} flashes.'.format(item.get_name),
                                               libtcod.turquoise), "consumed": True})
        elif item.item.light_source:
            item.item.light_source.enchantment += 1
            results.append({'message': Message('The {0} flashes.'.format(item.get_name),
                                               libtcod.turquoise), "consumed": True})
        else:
            results.append({'message': Message('You fail to enchant the {0}.'.format(item.get_name),
                                               libtcod.yellow), "consumed": True})
            
        return results

    def get_light(self):
        brightest_light = 0
        
        for i.item in self.items:
            if i.light_source and i.light_source.get_light > brightest_light:
                brightest_light = i.light_source.get_light

        return brightest_light
