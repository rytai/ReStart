import sys
import pygame
from collections import deque  # Queues
import random
from PathFinder import PathFinder
from dirty_drawing import DirtyDrawing
from map_data import MapData

__author__ = 'Kodex'

pygame.init()

size = width, height = 1280, 840
colorBlue = (0, 0, 255)
colorRed = (255, 0, 0)
colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0)

screen_ = pygame.display.set_mode(size)

# STARTGAME--------------------------

screen_.fill(colorBlack)

defaultFont = pygame.font.get_default_font()


def StartMenu(defaultFont, screen):
    textLine1 = "Welcome to the survival games."
    textLine2 = "Press Space to begin."

    basicFont = pygame.font.Font(defaultFont, 15)
    line1_s = basicFont.render(textLine1, False, colorWhite, colorBlack)
    line2_s = basicFont.render(textLine2, False, colorWhite, colorBlack)

    lineSpace = basicFont.size(textLine1)[1] + 12

    screen.blit(line1_s, (10, 10))
    screen.blit(line2_s, (10, 10 + lineSpace))

    pygame.display.flip()

    stuckInBeginning = True
    while stuckInBeginning:

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    stuckInBeginning = False


# StartMenu(defaultFont, screen_)

# Classes----------------------------


class InputHandler:
    key_pressed = None

    def __init__(self):
        pass


class Creature:
    name = ""
    surface = 0
    rect = 0
    positionOnMap = (0, 0)

    intent = None
    inventory = None

    def __init__(self, img_filename, _intent, inventory):
        self.name = ""
        self.surface = pygame.image.load(img_filename)
        self.surface = pygame.transform.scale(self.surface, (64, 64))
        self.surface.set_colorkey(colorWhite)
        self.rect = self.surface.get_rect()

        self.sheet = self.Sheet()

        self.intent = _intent
        self.inventory = inventory

    def move(self, x, y):
        """

        :rtype : None
        """
        self.rect.move_ip(x * 64, y * 64)
        self.positionOnMap = self.positionOnMap[0] + x, self.positionOnMap[1] + y

    def set_position(self, x, y=0):
        try:
            x, y = x
        except:
            pass
        self.rect.topleft = (x * 64, y * 64)
        self.positionOnMap = (x, y)

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
    def __init__(self, img_filename, intent, inventory):
        """

        :rtype : Hero
        """
        Creature.__init__(self, img_filename, intent, inventory)

        self.name = "Hero"


class NPC(Creature):
    def __init__(self, img_filename, intent, inventory):
        Creature.__init__(self, img_filename, intent, inventory)

    def make_random_move_intent(self):
        self.intent.type = self.intent.MOVE
        self.intent.direction = random.randint(-1, 1), random.randint(-1, 1)
        return self.intent


class Inventory:
    left_hand = None
    items = []

    def __init__(self):
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

    def __init__(self):
        self.name = ''
        self.surface = None


class Weapon(Item):
    def __init__(self, name):
        """

        :rtype : Weapon
        """
        Item.__init__(self)

        self.name = name


class MessageLog:
    fontSize = 20
    lineHeight = 4
    linesToRender = 20

    text_lines = []
    text_renders = 0  # Queue
    render = 0  # Has the complete messageLog rendered.
    position = (0, 0)
    font = False

    is_dirty = False

    def __init__(self, font):
        """

        :rtype : MessageLog
        """
        self.is_dirty = False
        self.font = pygame.font.Font(font, self.fontSize)
        assert isinstance(self.font, pygame.font.Font)
        self.text_renders = deque()

        # Calculate a size and create the 'render' surface.
        test_string = "50 characters|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|->"
        linespace_x, linespace_y = self.font.size(test_string)
        self.lineHeight += linespace_y

        surface_height = self.linesToRender * self.lineHeight
        self.render = pygame.Surface((linespace_x, surface_height))

        # First text.
        self.newline(test_string)
        new_text = "Welcome."
        self.newline(new_text)

    def newline(self, string):
        new_text = string
        new_render = self.font.render(new_text, False, colorWhite, colorBlack)
        self.text_lines.append(new_text)
        self.text_renders.append(new_render)

        # If the surface is full, pop earliest of the renders out.
        try:
            self.text_renders[self.linesToRender]
        except IndexError:
            pass
        else:
            self.text_renders.popleft()

        self.render_lines()

    def render_lines(self):
        y_position = 0
        self.render.fill(colorBlack)
        for text_render in self.text_renders:
            self.render.blit(text_render, (0, y_position))
            y_position += self.lineHeight

        self.is_dirty = True

    def set_is_dirty(self, boolean):
        """

        :rtype : None
        """
        self.is_dirty = boolean

    @property
    def get_is_dirty(self):
        return self.is_dirty


class MenuHandler:
    _menu_list = []
    screen = None

    paused_background_screen = pygame.Surface((0, 0))
    menu_surface = pygame.Surface((0, 0))

    def __init__(self):
        self._menu_list.append(self)

    def open_menu(self, screen):
        """

        :type screen: pygame.Surface
        """

        self.paused_background_screen = screen.copy()
        x, y = screen.get_size()
        new_size = x / 2, y / 2
        self.menu_surface = pygame.Surface(new_size)

        while 1:
            screen.fill(colorWhite)
            screen.blit(self.paused_background_screen, (0, 0))
            screen.blit(self.menu_surface, (x / 4, y / 4))
            pygame.display.flip()

        pass

    @property
    def menu_list(self):
        return self._menu_list


class MainMenu(MenuHandler):
    def __init__(self):
        MenuHandler.__init__(self)
        pass
        # TODO: STATSIT NAKYVIIN ALAS. SAMANKALTAINEN LUOKKA ITEMI-IKKUNALLE


class MapLoader:
    _MapData = None
    _NPC = None
    _Intent = None
    map_data_list = []

    def __init__(self, _MapData, _NPC, _Intent):
        """


        :rtype : MapLoader
        :type _NPC: NPC
        """
        self.default_map_name = "map_default.map"
        self._MapData = _MapData
        self._NPC = _NPC
        self._Intent = _Intent

    def load_default_map(self):

        map_size, map_name, string_data = self.load_map_data(self.default_map_name)

        map_layer_tile, map_layer_entities = self.resolve_map_string_data(map_size, string_data)

        new_map_data = self._MapData(map_size)

        self.populate_map_tiles(new_map_data, map_layer_tile)

        self.populate_map_entities(new_map_data, map_layer_entities)

        self.map_data_list.append(new_map_data)

        return new_map_data

    @staticmethod
    def populate_map_tiles(_map_data, _map_layer_tile):
        floor_img = pygame.image.load('dg_features32_floor.gif')
        floorTile_s = pygame.transform.scale(floor_img, (64, 64))
        wall_img = pygame.image.load('dg_extra132_boulderFloor.gif')
        wallTile_s = pygame.transform.scale(wall_img, (64, 64))

        map_size = _map_data.mapBoundaries

        for x in range(map_size[0]):
            for y in range(map_size[1]):
                if _map_layer_tile[(x, y)] == 1:
                    _map_data.texture_layer[(x, y)] = floorTile_s
                    _map_data.set_passable_tile(x, y, True)
                elif _map_layer_tile[(x, y)] == 2:
                    _map_data.texture_layer[(x, y)] = wallTile_s
                    _map_data.set_passable_tile(x, y, False)
                else:
                    raise RuntimeError

    def populate_map_entities(self, _map_data, _map_layer_entities):

        for _entity in _map_layer_entities:
            if _entity[0] == 1:
                new_entity = NPC("dg_monster132_thug.gif", self._Intent(), Inventory())
                new_entity.name = "Thug"
                assert isinstance(new_entity, NPC)
                new_entity.move(*_entity[1])
                _map_data.character_layer[_entity[1]] = new_entity

    def resolve_map_string_data(self, _map_size, _string_data):
        map_layer_tile = {}
        map_layer_entities = []

        # string data - Rest of the map file: List of csv strings
        for line in range(_map_size[1]):
            data_string = _string_data[line]
            string_position = 0
            length_of_line = len(data_string)
            for tile_in_line in range(_map_size[0]):
                # Tile Id
                data_bit, string_position = self.read_bits(string_position, data_string, 2)
                map_layer_tile[(tile_in_line, line)] = int(data_bit)

                data_bit, string_position = self.read_bits(string_position, data_string, 1)
                # Entity
                if data_bit == ':':
                    string_position += 1
                    # Entity Id
                    data_bit, string_position = self.read_bits(string_position, data_string, 1)
                    new_entity = int(data_bit)
                    new_entity_position = (tile_in_line, line)

                    map_layer_entities.append((new_entity, new_entity_position))
                    data_bit, string_position = self.read_bits(string_position, data_string, 1)

                if data_bit == ',':
                    pass
                else:
                    print data_string
                    print map_layer_tile
                    raise RuntimeError()

        return map_layer_tile, map_layer_entities

    @staticmethod
    def read_bits(_string_position, _from, _amount):
        _data_bit = _from[_string_position:_string_position + _amount]
        _string_position += _amount
        return _data_bit, _string_position

    @staticmethod
    def load_map_data(_map_name):
        f = open(_map_name, 'r')

        map_size = f.readline()

        map_size = int(map_size[:2]), int(map_size[-3:-1])

        map_name = f.readline()

        string_data = f.readlines()

        f.close()

        return [map_size, map_name, string_data]

    def save_map(self):
        pass




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



def roll_dice(amount_of_dices):
    dice_pool = []
    for dice in range(0, amount_of_dices):
        dice_pool.append(random.randint(1, 10))

    if amount_of_dices == 1:
        return dice_pool[0]
    else:
        return dice_pool


def make_skill_roll(ability, skill):
    dice_pool = roll_dice(ability)
    assert dice_pool[0], int
    step = 0
    for dice in dice_pool:
        if dice <= skill:
            step += dice

    return step, dice_pool


def roll_reactions(creatures_in_combat):  # There may be same fitness and roll. tobefixd
    """
    Takes creatures in combat. Puts them in list of tuples and rolls dices. Then takes only the creatures and puts them
    on a single list.
    :type creatures_in_combat: list(Creature)
    """

    reaction_order_ = []
    assert creatures_in_combat, [Creature]
    for creature in creatures_in_combat:
        dice = roll_dice(1)
        reaction_order_.append((dice, creature.sheet.fitness, creature))

    reaction_order_.sort()

    reaction_order_ = zip(*reaction_order_)[2]

    return list(reaction_order_)


def add_monster_to_random_position(map_data, new_monster):
    """



    :rtype : NPC
    :type new_monster: Creature
    :type map_data: MapData
    """
    counter = 50
    while counter is not 0:
        counter -= 1
        random_tile = random.randint(0, map_data.mapBoundaries[0]), random.randint(0, map_data.mapBoundaries[1])
        if map_data.tile_is_free(random_tile):
            map_data.set_character_on_map(new_monster, random_tile)
            new_monster.move(*random_tile)
            counter = 0

    return new_monster


def hero_turn(hero, map_data, message_log):
    if hero.intent.type is hero.intent.MOVE:  # There is an intent to move

        # See what there is in the spot.
        move_report = map_data.attempt_move("char", hero.positionOnMap, direction=hero.intent.direction, checkonly=True)

        # Intent to move was actually intent to attack
        if isinstance(move_report, Creature):
            hero.intent.type = hero.intent.ATTACK
            hero.intent.target = move_report
            return True

        # There was a wall
        if move_report == -1:
            hero.intent.type = hero.intent.WAIT
            message_log.newline('Ouch! You bumped to a wall.')
            return True

        # There was an empty tile.
        if move_report is True:
            return True

        return False

    elif hero.intent.type is hero.intent.WAIT:
        return True
    else:
        return False


def handle_attack(attacker, target, _message_log, map_data, entities_in_combat, reaction_order):
    """


    :type target: Hero or NPC
    :type map_data: MapData
    """
    report_from_attack = attacker.attack(target)

    _message_log.newline(attacker.name + str(report_from_attack))

    if target.sheet.fatigue == 4:
        if isinstance(target, Hero):
            _message_log.newline("You are knocked out.")
            del entities_in_combat[:]
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, subtype="combat", combat_situation="end"))
        else:
            _message_log.newline("{target} is knocked out.".format(target=target.name))
            entities_in_combat.remove(target)

        target.surface.fill(colorWhite)
        
        map_data.remove_character_from_position(target.positionOnMap)
        try:
            reaction_order.remove(target)
        except ValueError:
            pass


def draw_line_between_tiles(surface, from_tile, to_tile, line_width, line_color):
    x, y = from_tile
    _from = x * 64 + 32, y * 64 + 32
    x, y = to_tile
    _to = x * 64 + 32, y * 64 + 32
    assert isinstance(surface, pygame.Surface)
    pygame.draw.line(surface, line_color, _from, _to, line_width)


def draw_pathfinder_path(surface, path):
    """

    :rtype : None
    """
    assert isinstance(path, list)
    if path.__len__() == 0:
        return

    line_color = random_colour()
    previous_tile = path.pop(0)

    for current_tile in path:
        draw_line_between_tiles(surface, previous_tile, current_tile, 4, line_color)
        previous_tile = current_tile


def random_colour():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def generate_item_name(type='sword'):
    """

    :rtype : str
    """
    sword_prefixes = ['wooden', 'broken', 'shiny', 'fine']
    sword_middle_names = ['practise sword', 'sword', 'blade']
    sword_affixes = ['of might', 'of killing', 'of vampirism']

    new_name = ""

    if type == 'sword':
        prefix_percentage = random.randint(1, 100)
        # 20% Chance to get prefix
        if random.randint(0, 100) <= 20:
            new_name += random.choice(sword_prefixes)

        new_name += random.choice(sword_middle_names)

        if random.randint(0, 100) <= 10:
            new_name += random.choice(sword_affixes)
    else:
        print "Generate item name error: no type named: {}".format(type)
        new_name = "Null"

    return new_name


def main(screen):
    clock = pygame.time.Clock()

    floor_s = pygame.Surface((640, 640))
    pathfinder_screen_s = floor_s.copy()
    pathfinder_screen_s.set_colorkey(colorBlack)
    pathfinding_screen_reset = False

    main_menu = MainMenu()

    map_loader = MapLoader(MapData, NPC, Intent)
    map_data = map_loader.load_default_map()

    path_finder = PathFinder(map_data.passable_tiles)

    dirty_drawing = DirtyDrawing()
    dirty_drawing.prepare_floor(floor_s, map_data.get_texture_layer)
    dirty_drawing.issue_world_window_redraw()

    intent = Intent()

    hero = Hero("dg_classm32_swordHero.gif", Intent(), Inventory())
    if not map_data.tile_occupied((1, 1)):
        map_data.set_character_on_map(hero, (1, 1))
        hero.move(1, 1)
    hero.inventory.add_item(Weapon(generate_item_name('sword')))

    message_log = MessageLog(defaultFont)
    message_log.position = (screen.get_size()[0] - message_log.render.get_size()[0], 0)

    # Temporary. Combat is on at the start
    in_combat = False

    entities_in_combat = []
    for entity in map_data.get_characters_on_map:
        entities_in_combat.append(entity)
    reaction_order = []
    creature_in_turn = None
    new_event = pygame.event.Event(pygame.USEREVENT, subtype="combat", combat_situation="start")
    pygame.event.post(new_event)

    screen.fill(colorBlack)

    enable_pathfinder_screen = False

    # MAINLOOP--------------------------
    while 1:
        clock.tick(40)
        hero.intent.type = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    hero.intent.type = intent.WAIT
                elif event.key == pygame.K_UP or event.key == pygame.K_KP8:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (0, -1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (0, 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (1, 0)
                elif event.key == pygame.K_KP7:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (-1, -1)
                elif event.key == pygame.K_KP9:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (1, -1)
                elif event.key == pygame.K_KP3:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (1, 1)
                elif event.key == pygame.K_KP1:
                    hero.intent.type = intent.MOVE
                    hero.intent.direction = (-1, 1)
                elif event.key == pygame.K_KP_PLUS:
                    npc = add_monster_to_random_position(map_data, NPC("dg_monster132_thug.gif",
                                                                       Intent(), Inventory()))
                    entities_in_combat.append(npc)
                elif event.key == pygame.K_KP_MINUS:
                    pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                         subtype="menu"))
                elif event.key == pygame.K_i:
                    message_log.newline("-----Inventory:-----")
                    for item in hero.inventory.get_items:
                        assert isinstance(item, Item)
                        message_log.newline(item.name)

            if event.type == pygame.USEREVENT:
                if event.subtype is "combat":

                    if event.combat_situation == 'start':
                        in_combat = True
                        reaction_order = roll_reactions(entities_in_combat)
                        message_log.newline('RR')
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                             subtype="combat", combat_situation='first_turn'))

                    if event.combat_situation == 'first_turn':
                        creature_in_turn = reaction_order[0]
                        if creature_in_turn == hero:
                            message_log.newline("You start")
                        else:
                            message_log.newline('{} starts'.format(reaction_order[0].name))

                    if event.combat_situation == 'turn_change':
                        try:
                            reaction_order.remove(creature_in_turn)
                        except ValueError:
                            print '{} not in reaction order.'.format(creature_in_turn)

                        try:
                            creature_in_turn = reaction_order[0]
                            if creature_in_turn == hero:
                                message_log.newline("Your turn.")
                            else:
                                message_log.newline("{}'s turn.".format(reaction_order[0].name))
                        except IndexError:
                            creature_in_turn = None
                            pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                                 subtype="combat", combat_situation='end_of_phase'))

                    if event.combat_situation == "end_of_phase" and in_combat:
                        reaction_order = roll_reactions(entities_in_combat)
                        creature_in_turn = None
                        message_log.newline('EOP- RR')
                        pathfinding_screen_reset = True
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                             subtype="combat", combat_situation='first_turn'))

                    if event.combat_situation == "end":
                        in_combat = False

                elif event.subtype is 'menu':
                    main_menu.open_menu(screen)

        if in_combat is True:

            if isinstance(creature_in_turn, Hero):
                hero_makes_decision = hero_turn(hero, map_data, message_log)
                if hero_makes_decision:
                    pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                         subtype="combat", combat_situation="turn_change"))

                    if hero.intent.type is intent.MOVE:
                        map_data.attempt_move("char", hero.positionOnMap, direction=hero.intent.direction)
                        hero.move(*hero.intent.direction)

                    elif hero.intent.type is intent.ATTACK:
                        handle_attack(hero, hero.intent.target,
                                      message_log, map_data, entities_in_combat, reaction_order)

                    elif hero.intent.type == intent.WAIT:
                        pass
                    else:
                        raise "No Hero intention_:{}".format(hero.intent.type)

            elif isinstance(creature_in_turn, NPC):
                npc = creature_in_turn
                path = path_finder.find_path_between_points(npc.positionOnMap, hero.positionOnMap)
                if enable_pathfinder_screen == True:
                    if pathfinding_screen_reset == True:
                        pathfinder_screen_s.fill(colorBlack)
                    draw_pathfinder_path(pathfinder_screen_s, path)
                if path == "No route found":
                    pass
                else:
                    move_success = map_data.attempt_move("char", npc.positionOnMap, destination=path[1])
                    if move_success is True:
                        # npc.move(*npc.intent.direction)
                        npc.set_position(path[1])
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                             subtype="combat", combat_situation="turn_change"))
                    elif isinstance(move_success, NPC):
                        npc.intent = Intent.WAIT
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                             subtype="combat", combat_situation="turn_change"))
                    elif isinstance(move_success, Hero):
                        handle_attack(npc, hero, message_log, map_data, entities_in_combat, reaction_order)
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                             subtype="combat", combat_situation="turn_change"))
                    else:
                        print "ERRORROROREREERRROR"

        if enable_pathfinder_screen:
            dirty_drawing.issue_world_window_redraw()

        dirty_drawing.draw(screen, floor_s, map_data)

        if message_log.get_is_dirty is True:
            dirty_drawing.draw_message_log(screen, message_log)

        if enable_pathfinder_screen:
            dirty_drawing.draw_pathfinder_screen(screen, pathfinder_screen_s)

        pygame.display.flip()


if __name__ == '__main__':
    main(screen_)
