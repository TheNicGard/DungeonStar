
class Identity:
    def __init__(self, name, color, identify_on_use):
        self.name = name
        self.color = color
        self.identified = False
        self.identify_on_use = identify_on_use

    def identify(self, do_identify=True):
        self.identified = do_identify

def identify_item_in_list(item, identities, do_identify=True):
    item.identity.identify(do_identify=do_identify)
    identities[item.id] = True
