from dice import make_skill_roll
from dice import roll_dice

__author__ = 'Kodex'
import random


class Creature:
    name = ""
    surface = 0
    rect = 0
    positionOnMap = (0, 0)

    inventory = None

    in_combat = True

    def __init__(self, surface=None, inventory_instance=None):
        self.name = ""
        self.surface = surface
        self.rect = self.surface.get_rect()

        self.sheet = self.Sheet()

        self.inventory = inventory_instance

    def move(self, x, y):
        """

        :rtype : None
        """
        self.rect.move_ip(x * 64, y * 64)
        self.positionOnMap = self.positionOnMap[0] + x, self.positionOnMap[1] + y

    def set_position(self, x, y=0):
        try:
            x, y = x
        except TypeError:
            pass

        try:
            self.rect.topleft = (x * 64, y * 64)
            self.positionOnMap = (x, y)
        except TypeError:
            print "Invalid set position creature:{}, position:{}".format(self, (x, y))

    def attack(self, target):
        """
        0: (int) attack difficulty
        1: (int) steps achieved
        2: (list) dices rolled
        3: (tuple) damage dealed FAT, INJ
        4: missed, blocked, dmg, overkill
        :param target:
        :return:
        """
        assert isinstance(target, Creature)

        attack_report = []

        attack_difficulty = 2
        attack_report.append(attack_difficulty)

        step_value, dices_rolled = make_skill_roll(self.sheet.fitness, self.sheet.brawling)
        attack_report.append(step_value)
        attack_report.append(dices_rolled)

        result = step_value - attack_difficulty
        # Overkill
        if result >= 4:
            target.sheet.fatigue += 1
            attack_report.append((1, 0))
            attack_report.append("overkill")
        elif result >= 0:
            dice = roll_dice(1)
            if dice > target.sheet.ac:
                target.sheet.fatigue += 1
                attack_report.append((1, 0))
                attack_report.append("dmg")
            else:
                attack_report.append((0, 0))
                attack_report.append("blocked")
        else:
            attack_report.append((0, 0))
            attack_report.append("missed")

        return attack_report

    class Sheet:
        fatigue = 0

        fitness = 0
        awareness = 0

        brawling = 0

        ac = 4

        def __init__(self):
            """
            :rtype : Sheet
            """
            self.fitness = 3
            self.awareness = 3

            self.brawling = 4


class Hero(Creature):
    inventory = None
    intent = None

    def __init__(self, surface=None, inventory_instance=None):
        """

        :rtype : Hero
        """
        Creature.__init__(self, surface, inventory_instance)

        self.name = "Hero"
        self.intent = self.Intent()

    class Intent:
        MOVE = 1
        ATTACK = 2
        WAIT = 3
        type = 0
        target = 0
        direction = (0, 0)

        def __init__(self):
            """

            :rtype : self
            """
            self.MOVE = 1
            self.ATTACK = 2
            self.WAIT = 3


class NPC(Creature):
    state_of_mind = None

    def __init__(self, surface=None, inventory_instance=None):
        Creature.__init__(self, surface, inventory_instance)

    def update(self):
        pass


class StateOfMind():
    """Peaceful: Doesn't attack
    Homing missile: Finds you from anywhere and attacks"""
    PEACEFUL = 'peaceful'
    ATTACK_ON_SIGHT = 'attackonsight'
    HOMING_MISSILE = 'homingmissile'
