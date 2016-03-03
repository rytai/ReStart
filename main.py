# coding=utf-8
import os
import sys

try:
    import pygame_sdl2

    pygame_sdl2.import_as_pygame()
except ImportError:
    pass
import pygame
from collections import deque  # Queues
import random
from PathFinder import PathFinder
from dialogs import *
import drawing
from map_stuff import MapData, MapLoader
import creatures as creatures
from item_stuff import *
import dice as dice
import resources
import devtools
import windows
import generators

__author__ = 'Kodex'

pygame.init()

width, height = 1280, 800
size = width, height
colorBlue = (0, 0, 255)
colorRed = (255, 0, 0)
colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0)

screen_ = pygame.display.set_mode(size, pygame.HWSURFACE)

# STARTGAME--------------------------

screen_.fill(colorBlack)
# default_font = 'basis33.ttf'
default_font = pygame.font.get_default_font()


def start_menu(default_font, screen):
    basic_font = default_font
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Resources', 'Fonts', 'basis33.ttf')
    basic_font = pygame.font.Font(file_path, 40)

    text_lines = [
        'Welcome to the survival games.     (Currently you have godmode enabled.)',
        'Press Space to begin.',
        '',
        '|----------------------------------------',
        '| Move with numpad or arrows.',
        '|  ,  - Pick Item',
        '|  I  - Open Inventory',
        '|  +  - Add an enemy',
        '|  >  - Change map',
        '|  F1 - Enable GodMode',
        '|----------------------------------------'
    ]
    line_space = basic_font.size(text_lines[0])[1] + 2

    # render the text_lines in_place
    text_lines = [basic_font.render(x, False, colorWhite, colorBlack) for x in text_lines]

    for i in range(0, text_lines.__len__()):
        screen.blit(text_lines[i], (10, (10 + line_space) * i + 10))

    pygame.display.flip()

    stuck_in_beginning = True
    while stuck_in_beginning:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    stuck_in_beginning = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                stuck_in_beginning = False

            if event.type == pygame_sdl2.MULTIGESTURE:
                derp = raw_input()
                print derp
            elif event.type == pygame_sdl2.TEXTINPUT:
                print event
            elif event.type == pygame_sdl2.TEXTEDITING:
                print event


start_menu(default_font, screen_)


# Classes----------------------------


class InputHandler:
    key_pressed = None

    def __init__(self):
        pass


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

        :param boolean: Bool
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

    def _launch(self, screen):
        """

        :type screen: pygame.Surface
        """
        clock = pygame.time.Clock()

        while 1:
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:
                        return

            pygame.display.flip()

        pass

    @property
    def menu_list(self):
        return self._menu_list

    def init_menu_screen(self, screen):
        self.paused_background_screen = screen.copy()
        x, y = screen.get_size()
        new_size = x / 2, y / 2
        self.menu_surface = pygame.Surface(new_size)

        screen.fill(colorWhite)
        screen.blit(self.paused_background_screen, (0, 0))
        screen.blit(self.menu_surface, (x / 4, y / 4))


class MainMenu(MenuHandler):
    def __init__(self):
        MenuHandler.__init__(self)
        button = pygame.Surface((200, 50))
        pressed_button = pygame.Surface((200, 50))
        pass
        # TODO: STATSIT NAKYVIIN ALAS. SAMANKALTAINEN LUOKKA ITEMI-IKKUNALLE

    def launch(self, screen):
        self.init_menu_screen(screen)
        new_button = self.make_button_surface((240, 120))
        screen.blit(new_button, (400, 300))
        self._launch(screen)

    def make_button_surface(self, size=(50, 50), text=None):
        new_surface = pygame.Surface(size)
        new_surface.fill((255, 255, 255))

        x_size, y_size = size
        x_pos = x_size * 0.1
        y_pos = y_size * 0.1
        new_x_size = x_size * 0.8
        new_y_size = y_size * 0.8

        new_surface.fill((150, 150, 150), rect=pygame.Rect(x_pos, y_pos, new_x_size, new_y_size))

        # Centered text
        font = pygame.font.Font(pygame.font.get_default_font(), 32)
        text_surface = font.render('Retry', False, (255, 0, 0), (150, 150, 150))
        x, y = text_surface.get_size()
        x, y = x_size / 2 - (x / 2), y_size / 2 - (y / 2)

        new_surface.blit(text_surface, (x, y))

        return new_surface


class Camera:
    current_viewport = pygame.Rect((0, 0, 0, 0))
    viewport_boundaries = pygame.Rect(0, 0, 0, 0)
    viewport_screen_position = (16, 16)
    viewport_screen_area = pygame.Rect
    tile_size = (64, 64)

    def __init__(self, starting_position, viewport_size, viewport_screen_position, tile_size):
        """


        :rtype : Camera
        :type viewport_size: tuple
        """
        self.current_viewport.size = viewport_size[0], viewport_size[1]
        self.current_viewport.center = starting_position
        self.viewport_screen_position = viewport_screen_position
        self.tile_size = tile_size

        # Calculate the pixel position and size of viewport.
        topleft_pos = viewport_screen_position
        size_x = viewport_size[0] * tile_size[0]
        size_y = viewport_size[1] * tile_size[1]
        self.viewport_screen_area = pygame.Rect(topleft_pos, (size_x, size_y))

    def set_tile_position(self, position):
        """

        :type position: tuple
        """
        self.current_viewport.center = position

        self.current_viewport.clamp_ip(self.viewport_boundaries)

    def set_viewport_size(self, _size):
        self.current_viewport.width = _size[0]
        self.current_viewport.height = _size[1]

    def set_viewport_boundaries(self, top_left=(0, 0), _size=(9, 9)):
        self.viewport_boundaries.topleft = top_left
        self.viewport_boundaries.size = _size
        self.current_viewport.clamp_ip(self.viewport_boundaries)

    @property
    def get_viewport_rect(self):
        """

        :rtype : pygame.Rect
        """
        return self.current_viewport

    @property
    def get_viewport_topleft_tile(self):
        return self.current_viewport.topleft

    def calculate_tilepos_from_screenpos(self, screen_position):

        # Check if the position is within viewport area.
        if self.viewport_screen_area.collidepoint(screen_position):
            pixel_position_on_viewport_x = screen_position[0] - self.viewport_screen_position[0]
            pixel_position_on_viewport_y = screen_position[1] - self.viewport_screen_position[1]

            tile_viewport_x_position = pixel_position_on_viewport_x / self.tile_size[0]
            tile_viewport_y_position = pixel_position_on_viewport_y / self.tile_size[1]

            tile_x = tile_viewport_x_position + self.get_viewport_topleft_tile[0]
            tile_y = tile_viewport_y_position + self.get_viewport_topleft_tile[1]

            tile_position = tile_x, tile_y
            return tile_position
        else:
            return False


class CreatureActionHandler(object):
    creature_list = []
    creature_in_turn = None

    def __init__(self):
        self.creature_list = []

    def add_creature(self, entity_or_list, position=None):
        try:
            for entity in entity_or_list:
                self.creature_list.append(entity)
        except TypeError, err:
            if position:
                self.creature_list.insert(entity_or_list, position)
            else:
                self.creature_list.append(entity_or_list)
        pass

    def make_hero_first(self):
        for creature in self.creature_list:
            if isinstance(creature, creatures.Hero):
                self.add_creature(self.remove_creature(creature), 0)

    def remove_creature(self, cr):
        assert issubclass(cr, creatures.Creature)
        try:
            self.creature_list.pop(cr)
        except IndexError, err:
            print "CrAcHandler, cannot pop {}, no such entry in list. {}".format(cr, err)
            return None

    # Deal with one creature at a time, starting with player.
    def handle_turn(self, hero, message_log, map_data, sword_surface, path_finder=None, creature=None):
        if not creature:
            creature = self.creature_in_turn
        # Deal with hero's turn.
        if isinstance(creature, creatures.Hero):
            return self.hero_turn(creature, map_data, message_log, sword_surface, path_finder)
        # Deal with npc's turn.
        elif isinstance(creature, creatures.NPC):
            return self.npc_turn(creature, hero, message_log, map_data, sword_surface, path_finder)
        else:
            pass

    def hero_turn(self, hero, map_data, message_log, sword_surface, path_finder):
        # Handle everything the hero class can do
        """

        :param hero:
        :type hero: creatures.Hero
        :param map_data:
        :type map_data: map_stuff.MapData
        :param message_log:
        :type message_log: MessageLog
        :param sword_surface:
        :type sword_surface: generators.ItemGenerator
        :param path_finder:
        :type path_finder: PathFinder.PathFinder
        """
        assert isinstance(hero, creatures.Hero)
        assert isinstance(map_data, MapData)
        # Get intent
        intent_type = hero.intent.i_type
        if intent_type:  # There is an intent, continue

            if intent_type is hero.intent.MOVE:
                # Return the output.
                output = self.hero_turn_move(hero, map_data, message_log, sword_surface, path_finder)

            elif intent_type is hero.intent.ATTACK:
                distance = path_finder.get_distance(hero.position_on_map, hero.intent.target.position_on_map)
                if distance[1] <= 1 and distance[0] <= 1:
                    output = self.handle_attack(hero, hero.intent.target, message_log, map_data, sword_surface)
                    hero.intent.do_not_reset = False
                else:
                    self.hero_turn_move(hero, map_data, message_log, sword_surface, path_finder, find_path=True)
                    output = True

            elif intent_type is hero.intent.WAIT:
                output = True

            elif intent_type is hero.intent.WALK_TO:
                target = hero.intent.target
                try:  # Got tuple mayhaps?
                    position_x, position_y = target
                    if target == hero.position_on_map:  # Standing on target.
                        hero.intent.i_type = hero.intent.PICK_ITEM
                        hero.intent.do_not_reset = False
                        output = self.hero_turn(hero, map_data, message_log, sword_surface, path_finder)

                    else:  # Continue to target.
                        hero.intent.i_type = hero.intent.WALK_TO
                        if self.hero_turn_move(hero, map_data, message_log, sword_surface, path_finder, find_path=True):
                            hero.intent.do_not_reset = False
                        output = True
                except TypeError:  # Nope, propably an NPC. Decide interaction and reroll
                    self.decide_hero_interaction(hero, target)
                    output = self.hero_turn(hero, map_data, message_log, sword_surface, path_finder)


            elif intent_type is hero.intent.PICK_ITEM:
                # Hero standing on item.
                try:
                    target_position = hero.intent.target.position_on_map
                except AttributeError:
                    target_position = hero.intent.target
                if target_position == hero.position_on_map:
                    self.give_item_from_ground(hero, map_data)
                    hero.intent.do_not_reset = False
                else:
                    self.hero_turn_move(hero, map_data, message_log, sword_surface, path_finder, find_path=True)
                output = True

            elif intent_type is hero.intent.CHAT:
                print "Chattitychat"
                output = True

            else:
                print "There is hero intent. but it's type isnt' handled:{}".format(intent_type)
                output = False

            if output is True:
                if isinstance(self, CombatHandler):
                    push_new_user_event('combat', 'turn_change')
                else:
                    push_new_user_event('turn_order', 'turn_change')


        else:  # There's no intent. Fall back.
            pass

    def decide_hero_interaction(self, hero, target):
        """Changes hero's intent according the given target."""
        try:
            if target.in_combat:  # ATTACK
                hero.intent.i_type = hero.intent.ATTACK
            else:  # CHAT
                hero.intent.i_type = hero.intent.CHAT
            hero.intent.target = target
        except AttributeError:  # Wasn't an NPC.. dafuq?
            print "decide hero interaction, invalid target:{}".format(target)

        return None

    def hero_turn_move(self, hero, map_data, message_log, sword_surface, path_finder, find_path=False):
        """
        Try to move hero on the spot. Returns creature if there is one on the tile.
        :param hero: creatures.Hero
        :param map_data: MapData
        :param message_log: MessageLog
        :rtype: bool
        """
        layer = 'char'

        # PATHFINDING
        if find_path:
            try:
                target = hero.intent.target.position_on_map
            except AttributeError:
                target = hero.intent.target
            path = path_finder.find_path_between_points(hero.position_on_map, target)
            hero.old_path = path

            next_step = path[1]

            move_report = map_data.attempt_move(layer, hero.position_on_map, destination=next_step, checkonly=False)
        else:
            from_pos = hero.position_on_map
            direction = hero.intent.direction
            only_check = False  # Doesn't really move there. Just checks if it's free.
            move_report = map_data.attempt_move(layer, from_pos, direction=direction, checkonly=only_check)

        if move_report is True:  # Move successful
            if find_path:
                hero.set_position(*next_step)
            else:
                hero.move(*hero.intent.direction)
            return True

        # Couldn't move. There was an creature on destination tile. ATTACK
        elif isinstance(move_report, creatures.Creature):
            self.decide_hero_interaction(hero, move_report)
            self.hero_turn(hero, map_data, message_log, sword_surface, path_finder)
            return False

        # There was a wall
        elif move_report == -1:
            hero.intent.i_type = hero.intent.WAIT
            message_log.newline('Ouch! You bumped to a wall.')
            return True
        else:
            print 'Hero turn handler: Weird attempt move output{}'.format(move_report)
            return False

    @staticmethod
    def give_item_from_ground(creature, map_data):
        """

        :param map_data: instance
        :type creature: Creature
        """
        item = map_data.pop_item_from_position(creature.position_on_map)
        if item is not None:
            creature.inventory.add_item(item)

    # Rest will be declared on the subclasses.
    def npc_turn(self, *args):
        pass

    def handle_attack(self, *args):
        print "ERROR: handle attack in peaceful:{}".format(args)

    @property
    def creature_in_turn(self):
        return self._creature_in_turn

    @creature_in_turn.setter
    def creature_in_turn(self, cr):
        self._creature_in_turn = cr

    @property
    def creature_list(self):
        return self._creature_list

    @creature_list.setter
    def creature_list(self, crs):
        self._creature_list = crs


class CombatHandler(CreatureActionHandler):
    combat_active = False
    reaction_order = None
    combat_phase_done = False
    message_log = None

    def __init__(self, message_log):
        CreatureActionHandler.__init__(self)
        self.combat_active = False
        self.reaction_order = []
        self.creature_in_turn = None
        self.combat_phase_done = False
        self.message_log = message_log

    def level_init(self, creatures_on_map, hero):
        hero.in_combat = False
        self.creature_list = [creature for creature in creatures_on_map if creature.in_combat]
        if self.creature_list.__len__ > 0:
            hero.in_combat = True
            self.creature_list.append(hero)

    def create_combat(self, map_entities=None, hero=None):
        self.combat_active = True

        self.reaction_order = []  # Reset reaction. Dice will be thrown in Event
        self.creature_in_turn = None

        if map_entities:  # If list of creatures is provided as argument
            self.creature_list = [entity for entity in map_entities if entity.in_combat]

        if self.creature_list.__len__ == 0:  # Nobody to fight
            push_new_user_event('combat', 'end')
            return None
        else:  # Fight starting
            if hero not in self.creature_list:
                hero.in_combat = True
                self.creature_list.append(hero)

        self.message_log.newline('Entering combat.')
        push_new_user_event('combat', 'start_phase')

    def remove_creature(self, cr):
        try:
            self.creature_list.remove(cr)
            self.reaction_order.remove(cr)
        except ValueError, err:
            print "CombatHandler, cannot pop {}, no such entry in list".format(cr)
            return None
        except TypeError, err:
            print err
            print cr

        self.check_combat_state()

    def check_combat_state(self):
        if self.creature_list.__len__() <= 1:
            push_new_user_event('combat', 'end')
            for creature in self.creature_list:
                creature.in_combat = False

    def next_creature_turn(self):
        try:
            creature = self.reaction_order.pop(0)
        except IndexError:
            self.creature_in_turn = None
            return None
        self.creature_in_turn = creature
        return self.creature_in_turn

    def handle_attack(self, attacker, target, _message_log, map_data, sword_surface=None):
        """
        :param sword_surface: Surface
        :param _message_log: MessageLog
        :param attacker: creatures.Hero or creatures.NPC
        :type target: creatures.Hero or creatures.NPC
        :type map_data: MapData
        """
        attack_report = attacker.attack(target)

        _message_log.newline(attacker.name + str(attack_report))

        if target.sheet.fatigue == 4:
            if isinstance(target, creatures.Hero):
                _message_log.newline("You are knocked out.")
                self.remove_creature(target)
                push_new_user_event('combat', 'end')
            else:
                _message_log.newline("{target} is knocked out.".format(target=target.name))
                self.remove_creature(target)
                self.check_combat_state()

            new_sword = sword_surface.generate_sword()
            map_data.set_item_on_map(new_sword, target.position_on_map)
            map_data.remove_character_from_position(target.position_on_map)
            try:
                self.reaction_order.remove(target)
            except ValueError:
                pass

        return True

    def npc_turn(self, npc, hero, message_log, map_data, sword_surface, path_finder):
        # Find where the hero is.
        path = path_finder.find_path_between_points(npc.position_on_map, hero.position_on_map, old_path=npc.old_path)
        npc.old_path = path

        # Path NOT FOUND
        if path == 'path_not_found' or not path:
            push_new_user_event('combat', 'turn_change')
        elif path:  # Path found

            # Try to move closer to player
            layer = 'char'
            from_pos = npc.position_on_map
            dest_pos = path[1]  # First step on returned path.

            move_report = map_data.attempt_move(layer, from_pos, destination=dest_pos)

            if move_report:
                # Tile ahead is free. MOVE forward.
                if move_report is True:
                    npc.set_position(dest_pos)
                    push_new_user_event('combat', 'turn_change')
                    return True
                # Another npc is blocking the route. WAIT
                elif isinstance(move_report, creatures.NPC):
                    push_new_user_event('combat', 'turn_change')
                    return True
                # Hero is next to npc. ATTACK
                elif isinstance(move_report, creatures.Hero):
                    self.handle_attack(npc, hero, message_log, map_data, sword_surface)
                    push_new_user_event('combat', 'turn_change')
                    return True
            else:
                print 'CombatHandler npc invalid move report{}'.format(move_report)
                return False

    @property
    def combat_active(self):
        return self._combat_active

    @combat_active.setter
    def combat_active(self, ac):
        self._combat_active = ac

    @property
    def reaction_order(self):
        return self._reaction_order

    @reaction_order.setter
    def reaction_order(self, re):
        self._reaction_order = re
        self.next_creature_turn()

    @property
    def combat_phase_done(self):
        return self._combat_phase_done

    @combat_phase_done.setter
    def combat_phase_done(self, bo):
        self._combat_phase_done = bo


class PeacefulActionHandler(CreatureActionHandler):
    """Handles movement
    Every action, except combat/attacking"""
    turn_ordered_creatures = []

    def __init__(self):
        CreatureActionHandler.__init__(self)
        self.current_creature_index = 0

    def level_init(self, creatures_on_map):
        self.creature_list = [creature for creature in creatures_on_map if not creature.in_combat]

    def npc_turn(self, npc, hero, message_log, map_data, sword_surface, path_finder):

        """

        :param npc:
        :type npc: creatures.NPC
        :param hero:
        :type hero: creatures.Hero
        :param message_log:
        :type message_log: MessageLog
        :param map_data:
        :type map_data: map_stuff.MapData
        :param sword_surface:
        :type sword_surface: generators.ItemGenerator
        :param path_finder:
        :type path_finder: PathFinder.PathFinder
        :return:
        :rtype:
        """
        npc_action = npc.get_action()
        if npc_action == 'wait':
            return True
        elif npc_action == 'step to random':
            choices = [(1, 0), (-1, 0), (0, -1), (0, 1)]
            random.shuffle(choices)
            for direction_of_choice in choices:
                move_report = map_data.attempt_move('char', npc.position_on_map, direction=direction_of_choice)
                if move_report is True:
                    npc.move(*direction_of_choice)
                    break
                else:
                    choices.remove(direction_of_choice)
                    random.shuffle(choices)

        push_new_user_event('turn_order', 'turn_change')

    def next_creature(self):
        self.current_creature_index += 1

    def reset_creature_index(self):
        self.current_creature_index = 0

    @property
    def creature_in_turn(self):
        if self.creature_list.__len__() != 0:
            # There is creature at current index.
            try:
                cur_creature = self.creature_list[self.current_creature_index]
            # Index out of bounds, return to 0 and end the cycling of creatures->Next turn
            except IndexError:
                cur_creature = False
                self.current_creature_index = 0
                push_new_user_event('turn_order', 'end_phase')
        else:
            cur_creature = False

        return cur_creature


class TouchResolver:
    map_data = None
    camera = None

    def __init__(self, map_data, camera):
        assert isinstance(map_data, MapData)
        assert isinstance(camera, Camera)
        self.map_data = map_data
        self.camera = camera

    def resolve_touch(self, event=None, hero=None):
        assert event
        position = event.pos
        object_ = self.get_object_on_map(position)
        if object_:
            if isinstance(object_, Item):
                hero.intent.i_type = hero.intent.PICK_ITEM
            else:
                hero.intent.i_type = hero.intent.WALK_TO
            hero.intent.do_not_reset = True
            hero.intent.target = object_

    def get_object_on_map(self, position):
        """
        :type position: tuple
        :return: NPC -> Item -> Map_Position -> None
        :rtype: NPC or Item or None
        """
        map_position = self.camera.calculate_tilepos_from_screenpos(position)

        # Within viewport.
        if map_position:
            # Is there an NPC?
            tile_return_value = self.map_data.tile_occupied(map_position)
            if isinstance(tile_return_value, creatures.NPC):
                return tile_return_value
            else:  # Is there an Item?
                objects_on_tile = self.map_data.get_items_on_position(map_position)
                if objects_on_tile:
                    try:
                        return objects_on_tile[0]
                    except TypeError:
                        return objects_on_tile
                else:
                    if self.map_data.get_passable_tile(map_position):
                        return map_position
                    else:
                        return None
        else:  # Out of viewport
            return False


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
            new_monster.name = "derp"
            counter = 0

    return new_monster


def draw_line_between_tiles(surface, from_tile, to_tile, line_width, line_color):
    x, y = from_tile
    _from = x * 64 + 32, y * 64 + 32
    x, y = to_tile
    _to = x * 64 + 32, y * 64 + 32
    assert isinstance(surface, pygame.Surface)
    pygame.draw.line(surface, line_color, _from, _to, line_width)


def random_colour():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def load_map(map_name=None, map_loader=None, resource_loader=None, hero=None):
    assert isinstance(map_loader, MapLoader)
    assert isinstance(resource_loader, resources.Resource_Loader)
    assert PathFinder is not None
    assert isinstance(hero, creatures.Hero)
    # Kartan lataaminen
    if map_name == 'default':
        map_data, hero_position = map_loader.load_default_map(resource_loader, Inventory)
    else:
        map_data, hero_position = map_loader.load_map_named(map_name, resource_loader, Inventory)

    # Kartta pathfinder luokalle
    path_finder = PathFinder(map_data.passable_tiles)

    # Kartta piirtoluokalle
    map_surface_size = map_data.mapBoundaries[0] * 64, map_data.mapBoundaries[1] * 64
    floor_s = pygame.Surface(map_surface_size)
    world_s = pygame.Surface(map_surface_size)
    dirty_drawing = drawing.DirtyDrawing(floor_s, map_data.get_texture_layer)

    if not map_data.tile_occupied(hero_position):
        map_data.set_character_on_map(hero, hero_position)
        hero.set_position(hero_position)
    else:
        print "Hero tile occupied: position:{}, mapdata:{}".format(hero_position, map_data.get_characters_on_map)

    return map_data, path_finder, dirty_drawing, floor_s, world_s


def push_new_user_event(subtype=None, data=None):
    new_event = pygame.event.Event(pygame.USEREVENT, subtype=subtype, data=data)
    pygame.event.post(new_event)


def set_window_frames(dialog_window_inst, resource_loader, drawing, id=None):
    # Tarkistetaan, että framet pitää oikeasti vaihtaa.
    if dialog_window_inst.get_frame_surface is None and dialog_window_inst.frame_id != id:
        frame_id = dialog_window_inst.get_frame_id
        frame = resource_loader.get_frame_pieces(frame_id)
        frame_render = drawing.render_frames(frame, size=dialog_window_inst.rect.size)
        dialog_window_inst.set_frame_surface(frame_render)


class CustomEvents:
    E_MAP_CHANGE = pygame.USEREVENT + 1


def main(screen):
    ev = CustomEvents
    # -----------Debug------------

    print_keypresses = False

    dev_hero_undying = False
    # ------Init classes----------

    clock = pygame.time.Clock()
    resource_loader = resources.Resource_Loader()
    main_menu = MainMenu()
    map_loader = MapLoader(MapData, creatures.NPC)
    dialogs = Dialogs()
    dialog_window_inst = windows.DialogWindow()
    peaceful_action_handler = PeacefulActionHandler()

    camera = Camera((0, 0), (10, 10), (16, 16), (64, 64))
    message_log = MessageLog(default_font)

    combat_handler = CombatHandler(message_log)

    map_editor = devtools.Map_editor(resource_loader)
    item_generator = generators.ItemGenerator(resource_loader)

    # ------Load variables----------

    hero = creatures.Hero(surface=resource_loader.load_sprite('hero'), inventory_instance=Inventory())

    map_data, path_finder, dirty_drawing, floor_s, world_s = load_map('default', map_loader, resource_loader, hero)

    camera.set_tile_position(hero.position_on_map)
    camera.set_viewport_size((10, 10))
    camera.set_viewport_boundaries((0, 0), map_data.mapBoundaries)

    message_log.position = (screen.get_size()[0] - message_log.render.get_size()[0], 0)

    set_window_frames(dialog_window_inst, resource_loader, drawing)

    # Give hero an sword an put pne on the ground
    hero.inventory.add_item(item_generator.generate_sword())
    map_data.set_item_on_map(item_generator.generate_sword(), (1, 6))
    map_data.set_item_on_map(item_generator.generate_sword(), (1, 4))
    map_data.set_item_on_map(item_generator.generate_sword(), (1, 3))

    temp_sound = pygame.mixer.Sound(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Resources', 'Sound', 'map_change.wav'))
    default_font_inited = pygame.font.Font(default_font, 17)

    screen.fill(colorBlack)

    touch_resolver = TouchResolver(map_data, camera)

    push_new_user_event('combat', 'level_init')
    push_new_user_event('combat', 'start')
    # combat_handler.create_combat(map_data.get_characters_on_map, hero)

    # MAINLOOP--------------------------
    while 1:
        clock.tick(40)
        if not hero.intent.do_not_reset:
            hero.intent.i_type = 0

        if dev_hero_undying:
            hero.sheet.fatigue = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYUP:
                if print_keypresses:
                    print event.key
                if event.key == pygame.K_SPACE:
                    hero.intent.i_type = hero.intent.WAIT
                elif event.key == pygame.K_UP or event.key == pygame.K_KP8:
                    hero.intent.i_type = hero.intent.MOVE
                    hero.intent.direction = (0, -1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
                    hero.intent.i_type = hero.intent.MOVE
                    hero.intent.direction = (0, 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
                    hero.intent.i_type = hero.intent.MOVE
                    hero.intent.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
                    hero.intent.i_type = hero.intent.MOVE
                    hero.intent.direction = (1, 0)
                elif event.key == pygame.K_KP7:
                    hero.intent.i_type = hero.intent.MOVE
                    hero.intent.direction = (-1, -1)
                elif event.key == pygame.K_KP9:
                    hero.intent.i_type = hero.intent.MOVE
                    hero.intent.direction = (1, -1)
                elif event.key == pygame.K_KP3:
                    hero.intent.i_type = hero.intent.MOVE
                    hero.intent.direction = (1, 1)
                elif event.key == pygame.K_KP1:
                    hero.intent.i_type = hero.intent.MOVE
                    hero.intent.direction = (-1, 1)

                # + : Add enemy
                elif event.key == pygame.K_KP_PLUS:
                    new_creature = creatures.NPC(resource_loader.load_sprite('thug'))
                    npc = add_monster_to_random_position(map_data, new_creature)
                    combat_handler.add_creature(npc)
                # c : Chat
                elif event.key == pygame.K_c:
                    crs = map_data.get_creatures_around_tile(hero.position_on_map)
                    if crs.__len__() != 0:
                        push_new_user_event('chat', data=crs)
                # i : Inventory
                elif event.key == pygame.K_i:
                    message_log.newline("-----Inventory:-----")
                    for item in hero.inventory.get_items:
                        try:
                            message_log.newline('{}, {}ad'.format(item.name, item.mod_attack))
                        except AttributeError:
                            message_log.newline('{}'.format(item.name))
                # , : Pick item
                elif event.key == pygame.K_COMMA:
                    peaceful_action_handler.give_item_from_ground(hero, map_data)
                # > : Change map
                elif event.key == 60 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    new_event = pygame.event.Event(ev.E_MAP_CHANGE, map_name='@')
                    pygame.event.post(new_event)
                # F1 : GodMode
                elif event.key == pygame.K_F1:
                    dev_hero_undying = not dev_hero_undying
                    message_log.newline('God mode: {}'.format(dev_hero_undying))
                # F2: Menu
                elif event.key == pygame.K_F2:
                    push_new_user_event('menu')
                # F3: MapEditor
                elif event.key == pygame.K_F3:
                    map_editor.launch(map_data, screen)
                    screen.fill(colorBlack)
                    dirty_drawing.issue_world_surface_redraw()
                    message_log.set_is_dirty(True)
                # F4: Open chat-window
                elif event.key == pygame.K_F4:
                    push_new_user_event('open-dialog', data=1)
                # Home: Mouse position to caption.
                elif event.key == pygame.K_HOME:
                    devtools.mouse_position_to_caption()
                # TAB : Terminate program
                elif event.key == pygame.K_TAB:
                    sys.exit()

            # Clicked on the screen. Better check it out.
            elif event.type == pygame_sdl2.MOUSEBUTTONDOWN:
                touch_resolver.resolve_touch(event=event, hero=hero)

            elif event.type == ev.E_MAP_CHANGE:
                if event.map_name == '@':
                    map_load_return = load_map('map_arena.map', map_loader, resource_loader, hero)
                    map_data, path_finder, dirty_drawing, floor_s, world_s = map_load_return
                    push_new_user_event('combat', 'level_init')
                    push_new_user_event('combat', 'start')

                    camera.set_viewport_boundaries((0, 0), map_data.mapBoundaries)

                    temp_sound.play()
            elif event.type == pygame.USEREVENT:
                if event.subtype is 'combat':
                    if event.data == 'level_init':
                        combat_handler.level_init(map_data.get_characters_on_map, hero)
                        peaceful_action_handler.level_init(map_data.get_characters_on_map)

                    elif event.data == 'start':
                        combat_handler.create_combat(hero=hero)

                    elif event.data == 'start_phase':
                        combat_handler.combat_phase_done = False
                        combat_handler.reaction_order = dice.roll_reactions(combat_handler.creature_list)
                        if combat_handler.creature_in_turn == hero:
                            message_log.newline("You start")
                        elif isinstance(combat_handler.creature_in_turn, creatures.NPC):
                            message_log.newline('{} starts'.format(combat_handler.creature_in_turn.name))
                        else:
                            print 'ERROR: first turn invalid creature in turn {}'.format(
                                combat_handler.creature_in_turn)

                    elif event.data == 'turn_change':
                        combat_handler.next_creature_turn()

                        if combat_handler.creature_in_turn is not None:
                            if combat_handler.creature_in_turn == hero:
                                message_log.newline("Your turn.")
                            else:
                                message_log.newline("{}'s turn.".format(combat_handler.creature_in_turn.name))
                        else:
                            push_new_user_event('combat', 'end_of_phase')

                    elif event.data == "end_of_phase":
                        message_log.newline('-------------------------------')
                        combat_handler.combat_phase_done = True
                        push_new_user_event('turn_order', 'start_phase')

                    elif event.data == "end":
                        combat_handler.combat_active = False
                        peaceful_action_handler.creature_list = map_data.get_characters_on_map
                        push_new_user_event('turn_order', 'start_phase')


                    else:
                        print "Invalid combat event data:{}".format(event.data)

                # NON-COMBAT TURNS
                elif event.subtype is 'turn_order':
                    if event.data is 'start_phase':
                        peaceful_action_handler.reset_creature_index()
                    if event.data is 'turn_change':
                        peaceful_action_handler.next_creature()
                    if event.data is 'end_phase':
                        if combat_handler.combat_active == True:
                            push_new_user_event('combat', 'start_phase')
                        else:
                            push_new_user_event('turn_order', 'start_phase')

                elif event.subtype is 'menu':
                    main_menu.launch(screen)

                elif event.subtype is 'chat':
                    creatures_ = event.data
                    push_new_user_event('open_dialog', creatures_[0][1])


                elif event.subtype is 'open-dialog':
                    dialog_id = event.data
                    dialog_window_inst.set_text_lines(dialogs.get_dialog(dialog_id))
                    dialog_window_inst.set_title('Hello world.')
                    drawing.render_window(screen, dialog_window_inst, default_font_inited)

        # Handle combat
        if combat_handler.combat_active and not combat_handler.combat_phase_done:
            combat_handler.handle_turn(hero, message_log, map_data, item_generator, path_finder)
        else:
            # Handle other npc/hero actions.
            if peaceful_action_handler.handle_turn(hero, message_log, map_data, item_generator, path_finder):
                push_new_user_event('turn_order', 'turn_change')

        camera.set_tile_position(hero.position_on_map)

        dirty_drawing.draw(screen, world_s, camera, floor_s, map_data)

        if message_log.get_is_dirty is True:
            dirty_drawing.draw_message_log(screen, message_log)

        pygame.display.flip()


if __name__ == '__main__':
    main(screen_)
