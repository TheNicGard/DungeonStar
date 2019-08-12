import tcod as libtcod
from game_messages import Message

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
                if matching_entry and not (matching_entry.equippable or (matching_entry.item and matching_entry.item.chargeable)):
                    matching_entry.item.count += item.item.count
                else:
                    self.items.append(item)
                    
        return results

    def use(self, item_entity, **kwargs):
        results = []

        item_component = item_entity.item

        if item_component.use_function is None:
            equippable_component = item_entity.equippable
            food_component = item_entity.food

            if equippable_component:
                results.append({'equip': item_entity})
            elif food_component:
                results.extend(self.owner.hunger.eat(item_entity))
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
                    item_use_results = item_component.use_function(self.owner, **kwargs)

                    for item_use_result in item_use_results:
                        if item_use_result.get('consumed'):
                            if item_component.chargeable:
                                item_component.chargeable.charge -= 1
                            else:
                                self.remove_item(item_entity, 1)

                    results.extend(item_use_results)
            
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
            

            
                
