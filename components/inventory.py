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
            weight += i.weight
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
            if self.current_weight >= self.capacity:
                results.append({
                    'item_added': None,
                    'message': Message('You cannot carry any more!', libtcod.yellow)
                })
            else:
                results.append({
                    'item_added': item,
                    'message': Message('You pick up the {0}!'.format(item.name), libtcod.blue)
                })
                self.items.append(item)
                self.items.sort(key=lambda x: x.name)

        return results

    def use(self, item_entity, **kwargs):
        results = []

        item_component = item_entity.item

        if item_component.use_function is None:
            equippable_component = item_entity.equippable

            if equippable_component:
                results.append({'equip': item_entity})
            else:
                results.append({'message': Message('The {0} cannot be used!'.format(
                item_entity.name), libtcod.yellow)})
        else:
            if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get('consumed'):
                        self.remove_item(item_entity)

                results.extend(item_use_results)
            
        return results

    def remove_item(self, item):
        self.items.remove(item)

    def drop_item(self, item):
        results = []

        if self.owner.equipment.main_hand == item or self.owner.equipment.off_hand == item:
            self.owner.equipment.toggle_equip(item)
        
        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)
        results.append({'item_dropped': item,
                        'message': Message('You dropped the {0}.'.format(item.name),
                                           libtcod.yellow)})

        return results
