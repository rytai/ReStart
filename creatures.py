from dice import make_skill_roll
from dice import roll_dice

__author__ = 'Kodex'
import random


class Creature(object):
    name = ""
    surface = 0
    rect = 0
    position_on_map = (0, 0)

    inventory = None

    in_combat = False

    # Here is saved last pathfinding path.
    old_path = []

    def __init__(self, surface=None, inventory_instance=None):
        self.name = ""
        self.surface = surface
        self.rect = self.surface.get_rect()

        self.sheet = self.Sheet()

        self.inventory = inventory_instance

        self.old_path = []

    def move(self, x, y):
        """

        :rtype : None
        """
        self.rect.move_ip(x * 64, y * 64)
        self.position_on_map = self.position_on_map[0] + x, self.position_on_map[1] + y

    def set_position(self, x, y=0):
        try:
            x, y = x
        except TypeError:
            pass

        try:
            self.rect.topleft = (x * 64, y * 64)
            self.position_on_map = (x, y)
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

    @property
    def old_path(self):
        return self._old_path

    @old_path.setter
    def old_path(self, path):
        self._old_path = path

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
        NOT_RESOLVED = 999
        MOVE = 1
        ATTACK = 2
        WAIT = 3
        PICK_ITEM = 4
        WALK_TO = 5
        CHAT = 6
        type = 0
        target = 0
        direction = None

        def __init__(self):
            """

            :rtype : self
            """
            pass

        @property
        def position(self):
            return self._position

        @position.setter
        def position(self, pos):
            self._position = pos


class NPC(Creature):
    state_of_mind = None
    action_queue = []
    speech_id = 1

    def __init__(self, surface=None, inventory_instance=None):
        Creature.__init__(self, surface, inventory_instance)
        self.action_queue = []
        self.state_of_mind = StateOfMind()
        self.speech_id = 1

    def get_action(self):
        # No actions in the queue. Get some.
        if self.action_queue.__len__() == 0:
            self.set_action()
            return self.action_queue.pop()
        else:
            return self.action_queue.pop()

    def set_action(self, action_list=None):
        state = self.state_of_mind.get
        if state is self.state_of_mind.WANDERING:
            if random.randint(0, 1) == 0:
                for i in range(0, random.randint(0, 2)):
                    self.action_queue.append('wait')
                self.action_queue.append('step to random')
                self.action_queue.reverse()
            else:
                self.action_queue.append('step to random')


class StateOfMind(object):
    """Peaceful: Doesn't attack
    Homing missile: Finds you from anywhere and attacks"""
    get = None
    WANDERING = 'wandering'
    ATTACK_ON_SIGHT = 'attackonsight'
    HOMING_MISSILE = 'homingmissile'

    def __init__(self):
        self.get = self.WANDERING

    @property
    def get(self):
        return self._get

    @get.setter
    def get(self, state):
        self._get = state
