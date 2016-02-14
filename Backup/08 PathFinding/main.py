import sys
import pygame
from collections import deque  # Queues
import random
from PathFinder import  PathFinder

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
        self.rect.move_ip(x * 64, y * 64)
        self.positionOnMap = self.positionOnMap[0] + x, self.positionOnMap[1] + y

    def set_position(self, x, y):
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

        :rtype : self
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


class Item:
    name = ''

    def __init__(self):
        self.name = ''


class Weapon(Item):
    def __init__(self, name):
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
    dirty_drawing = False

    def __init__(self, font, _dirty_drawing):
        """

        :rtype : MessageLog
        """
        self.font = pygame.font.Font(font, self.fontSize)
        self.dirty_drawing = _dirty_drawing
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

        self.dirty_drawing.message_log_is_dirty = True


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
    _dirty_drawing = None
    map_data_list = []

    def __init__(self, _MapData, _dirty_drawing, _NPC, _Intent):
        """


        :rtype : MapLoader
        :type _NPC: NPC
        """
        self.default_map_name = "map_default.map"
        self._MapData = _MapData
        self._dirty_drawing = _dirty_drawing
        self._NPC = _NPC
        self._Intent = _Intent

    def load_default_map(self):

        map_size, map_name, string_data = self.load_map_data(self.default_map_name)

        map_layer_tile, map_layer_entities = self.resolve_map_string_data(map_size, string_data)

        new_map_data = self._MapData(map_size, self._dirty_drawing)

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
                _map_data.charLayer[_entity[1]] = new_entity

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


class MapData:
    mapBoundaries = (0, 0)
    charLayer = {}
    tile_passable = {} # (x,y): True if passable
    texture_layer = {}
    dirty_drawing = False

    _open_tiles_modified = False

    def __init__(self, map_boundaries_t, _dirty_drawing):
        """

        :rtype : MapData
        """
        self.mapBoundaries = map_boundaries_t
        self.dirty_drawing = _dirty_drawing


    def tile_occupied(self, tile_t):
        """Return occupant, false if not occupied, -1 if out of boundaries"""
        if tile_t in self.charLayer:
            return self.charLayer[tile_t]
        else:
            return False

    def in_boundaries(self, tile_t):
        if -1 < tile_t[0] < self.mapBoundaries[0]:
            if -1 < tile_t[1] < self.mapBoundaries[1]:
                return True
        return False

    def attempt_move(self, layer_name, origin, direction=(0, 0), destination=0, checkonly=False):
        """Attempts to move the entity to the direction provided on the layer"""
        assert origin, (int, int)
        assert direction, (int, int)
        if destination == 0:
            destination = origin[0] + direction[0], origin[1] + direction[1]
        if layer_name == "char":
            # Check if the destination is within boundaries
            if not self.in_boundaries(destination):
                return -1

            # Check if the destination is a wall.
            try:
                if self.tile_passable[destination] is False:
                    return -1
            except KeyError:
                pass

            # Check if there is someone on the spot.
            occupied = self.tile_occupied(destination)
            if occupied:
                return occupied
            elif not occupied:
                try:
                    if not checkonly:
                        self.charLayer[destination] = self.charLayer.pop(origin)
                        self.dirty_drawing.add_dirty_tile(origin)
                        self.dirty_drawing.add_dirty_tile(destination)
                    return True
                # Human error
                except KeyError:
                    print "Error: No such key: " + str(destination) + " or: " + str(origin)
        # Human error.
        else:
            raise StandardError("No layer named: " + layer_name)

    def tile_is_free(self, tile_t):
        if self.in_boundaries(tile_t):
            if not self.tile_occupied(tile_t):
                try:
                    if self.tile_passable[tile_t] is True:
                        return True
                    else:
                        return False
                except KeyError:
                    return True

    @property
    def passable_tiles(self):
        """


        :rtype : [tuple(int,int)]
        """
        return [position for position, boolean in self.tile_passable.iteritems() if boolean == True ]

    def set_passable_tile(self, tile_x, tile_y, passability):
        assert isinstance(passability, bool)
        self.tile_passable[(tile_x, tile_y)] = passability

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


class DirtyDrawing:
    message_log_is_dirty = False
    world_window_is_dirty = False
    world_window_redraw = False

    dirty_tiles = []

    def __init__(self):
        self.message_log_is_dirty = False
        self.world_window_is_dirty = True
        self.world_window_redraw = True
        self.dirty_tiles = []

        self.path_finder_debug_screen_draw = True

    def add_dirty_tile(self, value):
        self.dirty_tiles.append(value)
        self.world_window_is_dirty = True

    def draw(self, map_data, floor_s, update_game_window, _screen, message_log, pathfinder_screen_s):
        # Redraw the whole WorldWindow
        if self.world_window_redraw and update_game_window is True:
            for x in range(map_data.mapBoundaries[0]):
                for y in range(map_data.mapBoundaries[1]):
                    floor_s.blit(map_data.texture_layer[(x, y)], (x * 64, y * 64))
            for entity in map_data.charLayer.values():
                floor_s.blit(entity.surface, entity.rect)
            self.world_window_redraw = False
            self.world_window_is_dirty = False
            del self.dirty_tiles[:]
            update_game_window = False

            _screen.blit(floor_s, (16, 16))
        # Draw dirty parts of WorldWindow
        elif self.world_window_is_dirty and update_game_window is True:
            for tile in self.dirty_tiles:
                _screen.blit(map_data.texture_layer[(tile[0], tile[1])], (tile[0] * 64 + 16, tile[1] * 64 + 16))
            for entity in map_data.charLayer.values():
                _screen.blit(entity.surface, entity.rect.move((16, 16)))
            self.world_window_is_dirty = False
            del self.dirty_tiles[:]
            update_game_window = False
        # Draw the visual representation of pathfinder
        if self.path_finder_debug_screen_draw:
            _screen.blit(pathfinder_screen_s, (16, 16))

        if self.message_log_is_dirty:
            _screen.blit(message_log.render, message_log.position)
            self.message_log_is_dirty = False

        return floor_s, update_game_window, _screen


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


def add_monster_to_random_position(_map_data, new_monster, _dirty_drawing):
    counter = 50
    while counter is not 0:
        counter -= 1
        random_tile = random.randint(0, _map_data.mapBoundaries[0]), random.randint(0, _map_data.mapBoundaries[1])
        if _map_data.tile_is_free(random_tile):
            _map_data.charLayer[random_tile] = new_monster
            new_monster.move(*random_tile)
            _dirty_drawing.add_dirty_tile(random_tile)
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


def handle_attack(attacker, target, _message_log, _map_data, _dirty_drawing, entities_in_combat, reaction_order):
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
        _dirty_drawing.add_dirty_tile(target.positionOnMap)
        _dirty_drawing.world_window_is_dirty = True
        _map_data.charLayer.pop(target.positionOnMap)
        try:
            reaction_order.remove(target)
        except ValueError:
            pass


def main(screen):
    clock = pygame.time.Clock()
    main_menu = MainMenu()

    dirty_drawing = DirtyDrawing()
    dirty_drawing.world_window_is_dirty = True
    dirty_drawing.world_window_redraw = True

    map_loader = MapLoader(MapData, dirty_drawing, NPC, Intent)
    map_data = map_loader.load_default_map()

    passable_tiles = map_data.passable_tiles
    path_finder = PathFinder(passable_tiles)
    floor_s = pygame.Surface((1280, 840))
    pathfinder_screen_s = floor_s.copy()
    pathfinder_screen_s.set_colorkey(colorBlack)

    intent = Intent()

    hero = Hero("dg_classm32_swordHero.gif", Intent(), Inventory())
    if not map_data.tile_occupied((1, 1)):
        map_data.charLayer[(1, 1)] = hero
        hero.move(1, 1)
    hero.inventory.add_item(Weapon("Knuckles +1Fat"))

    message_log = MessageLog(defaultFont, dirty_drawing)
    message_log.position = (screen.get_size()[0] - message_log.render.get_size()[0], 0)

    # Temporary. Combat is on at the start
    in_combat = False

    entities_in_combat = []
    for entity in map_data.charLayer.values():
        entities_in_combat.append(entity)
    reaction_order = []
    new_event = pygame.event.Event(pygame.USEREVENT, subtype="combat", combat_situation="start")
    pygame.event.post(new_event)

    screen.fill(colorBlack)

    update_game_window = True

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
                                                                       Intent()), dirty_drawing)
                    entities_in_combat.append(npc)
                    update_game_window = True
                elif event.key == pygame.K_KP_MINUS:
                    pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                         subtype="menu"))
            if event.type == pygame.USEREVENT:
                if event.subtype is "combat":

                    if event.combat_situation == 'start':
                        in_combat = True
                        reaction_order = roll_reactions(entities_in_combat)
                        creature_in_turn = reaction_order[0]
                        message_log.newline('RR')

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
                        update_game_window = True

                    if event.combat_situation == "end_of_phase":
                        if in_combat:
                            reaction_order = roll_reactions(entities_in_combat)
                            creature_in_turn = None
                            message_log.newline('EOP- RR')
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
                                      message_log, map_data, dirty_drawing, entities_in_combat, reaction_order)

                    elif hero.intent.type == intent.WAIT:
                        pass
                    else:
                        raise "No Hero intention_:{}".format(hero.intent.type)

            elif isinstance(creature_in_turn, NPC):
                npc = creature_in_turn
                path = path_finder.find_path_between_points(npc.positionOnMap, hero.positionOnMap, pathfinder_screen_s)
                if path == "No route found":
                    pass
                if len(path) == 1:
                    handle_attack(npc, hero, message_log, map_data, dirty_drawing, entities_in_combat, reaction_order)
                    pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                         subtype="combat", combat_situation="turn_change"))
                else:
                    move_success = map_data.attempt_move("char", npc.positionOnMap, destination=path[1])
                    if move_success is True:
                        # npc.move(*npc.intent.direction)
                        npc.set_position(*path[1])
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                             subtype="combat", combat_situation="turn_change"))
                    elif isinstance(move_success, NPC):
                        npc.intent = Intent.WAIT
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                             subtype="combat", combat_situation="turn_change"))
                    else:
                        print "ERRORROROREREERRROR"

        enable_pathfinder_screen = True
        if enable_pathfinder_screen == True:
            dirty_drawing.world_window_redraw = True

        floor_s, update_game_window, screen = dirty_drawing.draw(map_data, floor_s, update_game_window,
                                                                 screen, message_log, pathfinder_screen_s)

        pygame.display.flip()


if __name__ == '__main__':
    main(screen_)
