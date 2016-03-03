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


class Item(object):
    name = ''
    surface = None
    rareness = 0
    position_on_map = None

    def __init__(self, surface=None):
        self.name = ''
        self.surface = surface


class Equippable(Item):
    EQUIP_SLOT_ONE_HAND = 0
    EQUIP_SLOT_TWO_HANDED = 1

    equip_slot = EQUIP_SLOT_ONE_HAND
    equippable = True

    def __init__(self):
        Item.__init__(self)
        self.equip_slot = 0


class Weapon(Equippable):
    mod_attack = 2
    mod_speed = 1

    type = None

    T_1H_SWORD = 0
    T_2H_SWORD = 1

    def __init__(self, name='', surface=None):
        """

        :rtype : Weapon
        """
        Equippable.__init__(self)

        self.name = name
        self.surface = surface

        self.type = self.T_1H_SWORD
