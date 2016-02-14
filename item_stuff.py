
class Inventory:
    left_hand = None
    items = []

    def __init__(self, a=None):
        self.left_hand = None
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    @property
    def get_items(self):
        """

        :rtype : [Item]
        """
        return self.items


class Item:
    name = ''
    surface = None

    def __init__(self, surface=None):
        self.name = ''
        self.surface = surface


class Weapon(Item):
    def __init__(self, name, surface=None):
        """

        :rtype : Weapon
        """
        Item.__init__(self, surface=surface)

        self.name = name