import random

from item_stuff import Item, Equippable, Weapon


class ItemGenerator(object):
    resource_loader = None
    WORTH_COMMON = 0
    WORTH_ENCHANTED = 1
    WORTH_RARE = 2
    WORTH_UNIQUE = 3  # Reserved for custom made items. Not obtainable from generating.
    WORTH_LEGENDARY = 4

    # List(NAME, QUALITY)
    sword_qualities = [('Broken', -2), ('Worn', -1), ('Normal', 0), ('Shiny', 1), ('Fine', 2)]
    sword_types = ['Longsword', 'Sword', 'Scimitar']
    sword_enchantments = ['of might', 'of slashing', 'of vampirism']

    chance_of_enchanted = 200
    chance_of_rare = 100
    chance_of_legendary = 50

    chance_of_enchantment = 20  # When rareness is not enchanted

    def __init__(self, resource_loader):
        self.resource_loader = resource_loader

    def generate_sword(self, rareness=None):

        if not rareness:
            rareness = self.calculate_rareness()

        quality = self.calculate_quality(rareness)
        _type = self.random_sword_type()
        enchantment = self.calculate_enchantment(rareness)
        name = self.build_name(quality, _type, enchantment)

        # Create sword instance and set values
        new_sword = Weapon(name=name)

        new_sword.mod_attack = self.calculate_stats(quality, new_sword.mod_attack)

        if _type == 'Longsword':
            new_sword.type = Weapon.T_2H_SWORD
            new_sword.equip_slot = new_sword.EQUIP_SLOT_TWO_HANDED
        else:
            new_sword.type = Weapon.T_1H_SWORD
            new_sword.equip_slot = new_sword.EQUIP_SLOT_ONE_HAND

        new_sword.surface = self.resource_loader.load_sprite('sword')
        return new_sword

    def calculate_rareness(self):
        # Rareness is presented in chance of 1 of 1000

        chance = random.randint(0, 1000)

        if chance <= self.chance_of_enchanted:
            if chance <= self.chance_of_rare:
                if chance <= self.chance_of_legendary:
                    return self.WORTH_LEGENDARY
                return self.WORTH_RARE
            return self.WORTH_ENCHANTED
        return self.WORTH_COMMON

    def calculate_quality(self, rareness):
        chance = [0, 0, 0, 0, 0]
        chance[0], chance[4] = 8, 8
        chance[1], chance[3] = 17, 17
        chance[2] = 50

        if rareness is not self.WORTH_COMMON:
            pass  # Later well set different percentages of qualities for different rarenesses.

        randm = random.randint(0, 100)
        if randm <= chance[0]:
            return self.sword_qualities[0]  # Broken
        elif randm <= chance[0] + chance[1]:
            return self.sword_qualities[1]
        elif randm <= chance[0] + chance[1] + chance[2]:
            return self.sword_qualities[2]
        elif randm <= chance[0] + chance[1] + chance[2] + chance[3]:
            return self.sword_qualities[3]
        elif randm <= chance[0] + chance[1] + chance[2] + chance[3] + chance[4]:
            return self.sword_qualities[4]
        else:
            print "generator:calc_quality: invalid chance value:{}, {}".format(chance, randm)
            return self.sword_qualities[2]

    def random_sword_type(self):
        return random.choice(self.sword_types)

    def calculate_enchantment(self, rareness):  # 20percent chance for enchantment.
        if rareness is self.WORTH_COMMON:
            return None
        elif rareness is self.WORTH_ENCHANTED:
            return random.choice(self.sword_enchantments)
        else:
            if random.randint(0, 100) <= self.chance_of_enchantment:
                return random.choice(self.sword_enchantments)
            else:
                return None

    @staticmethod
    def build_name(quality, _type, enchantment):
        name = ''

        # Prefix
        if quality[0] != 'Normal':
            name += '{} '.format(quality[0])

        # Name
        name += _type

        # Appendix
        if enchantment is not None:
            name += ' {}'.format(enchantment)

        return name

    def calculate_stats(self, quality, base_attack_mod):
        value_ = base_attack_mod + quality[1]
        return value_




class DungeonGenerator(object):
    def __init__(self):
        pass
