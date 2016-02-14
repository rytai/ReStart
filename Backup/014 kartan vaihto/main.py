import sys
import pygame
from collections import deque  # Queues
import random
from PathFinder import PathFinder
from dirty_drawing import DirtyDrawing
from map_stuff import MapData, MapLoader
from creatures import Creature, Hero, NPC
from item_stuff import *
import dice as Dice
import resources

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

    textlines = [
        'Welcome to the survival games.',
        'Press Space to begin.',
        '',
        'Keys:------------------------------',
        '|Move - Numpad / Arrows',
        '|Open Inventory - I',
        '|Add an enemy - +',
        '-----------------------------------'
    ]

    #render the textlines in_place
    textlines = [basicFont.render(x, False, colorWhite, colorBlack) for x in textlines]

    lineSpace = basicFont.size(textLine1)[1] + 12

    for i in range(0,textlines.__len__()):
        screen.blit(textlines[i], (10, (10 + lineSpace) * i + 10))

    pygame.display.flip()

    stuckInBeginning = True
    while stuckInBeginning:

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    stuckInBeginning = False


#StartMenu(defaultFont, screen_)

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


class Camera:
    current_viewport = pygame.Rect((0, 0, 0, 0))
    viewport_boundaries = pygame.Rect(0, 0, 0, 0)

    def __init__(self, starting_position=(0, 0), viewport_size=(0, 0)):
        """


        :rtype : Camera
        :type viewport_size: tuple
        """
        self.current_viewport.size = viewport_size[0], viewport_size[1]
        self.current_viewport.center = starting_position

    def set_tile_position(self, position):
        """

        :type position: tuple
        """
        self.current_viewport.center = position

        self.current_viewport.clamp_ip(self.viewport_boundaries)

    def set_viewport_size(self, size):
        self.current_viewport.width = size[0]
        self.current_viewport.height = size[1]

    def set_viewport_boundaries(self, top_left=(0, 0), size=(9, 9)):
        self.viewport_boundaries.topleft = top_left
        self.viewport_boundaries.size = size
        self.current_viewport.clamp_ip(self.viewport_boundaries)

    @property
    def get_viewport_rect(self):
        """

        :rtype : pygame.Rect
        """
        return self.current_viewport


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


def handle_attack(attacker, target, _message_log, map_data, entities_in_combat, reaction_order, sword_surface=None):
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

        new_sword = Weapon(generate_item_name(), surface=sword_surface)
        map_data.set_item_on_map(new_sword, target.positionOnMap)
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
    if path.__len__() == 0 or path == 'path not found':
        return

    line_color = random_colour()
    previous_tile = path[:].pop(0)

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
            new_name += random.choice(sword_prefixes) + " "

        new_name += random.choice(sword_middle_names)

        if random.randint(0, 100) <= 10:
            new_name += " " + random.choice(sword_affixes)
    else:
        print "Generate item name error: no type named: {}".format(type)
        new_name = "Null"

    return new_name


def pick_up_item(creature, map_data):
    """

    :type creature: Creature
    """
    item = map_data.pop_item_from_position(creature.positionOnMap)
    if item is not None:
        creature.inventory.add_item(item)


def load_map(map_name = None, map_loader=None, resource_loader=None, hero=None):
    assert isinstance(map_loader, MapLoader)
    assert isinstance(resource_loader, resources.Resource_Loader)
    assert PathFinder is not None
    assert isinstance(hero, Hero)
    #Kartan lataaminen
    if map_name == 'default':
        map_data, hero_position = map_loader.load_default_map(resource_loader, Inventory)
    else:
        map_data, hero_position = map_loader.load_map_named(map_name, resource_loader, Inventory)

    #Kartta pathfinder luokalle
    path_finder = PathFinder(map_data.passable_tiles)

    #Kartta piirtoluokalle
    map_surface_size = map_data.mapBoundaries[0]*64, map_data.mapBoundaries[1]*64
    floor_s = pygame.Surface(map_surface_size)
    world_s = pygame.Surface(map_surface_size)
    dirty_drawing = DirtyDrawing(floor_s, map_data.get_texture_layer)

    if not map_data.tile_occupied(hero_position):
        map_data.set_character_on_map(hero, hero_position)
        hero.set_position(hero_position)
    else:
        print "Hero tile occupied: position:{}, mapdata:{}".format(hero_position, map_data.get_characters_on_map)

    return map_data, path_finder, dirty_drawing, floor_s, world_s


def create_combat(map_entities):
    reaction_order = []
    creature_in_turn = None
    entities_in_combat = []

    for entity in map_entities:
        entities_in_combat.append(entity)

    new_event = pygame.event.Event(pygame.USEREVENT, subtype="combat", combat_situation="start")
    pygame.event.post(new_event)

    return entities_in_combat, reaction_order, creature_in_turn


def push_new_user_event(user_event_type = None, data = None):
    new_event = pygame.event.Event(pygame.USEREVENT, subtype=user_event_type, data = data)
    pygame.event.post(new_event)


def main(screen):
    # -----------Debug------------
    enable_pathfinder_screen = False  # Draws the found pathfinder path
    report_pathfinder_time = False

    print_keypresses = False

    dev_hero_undying = True
    # ----------------------------

    clock = pygame.time.Clock()
    pathfinder_screen_s = pygame.Surface((10 * 64, 20 * 64))
    pathfinder_screen_s.set_colorkey(colorBlack)
    pathfinding_screen_reset = False

    intent = Intent()

    resource_loader = resources.Resource_Loader()

    sword_surface = resource_loader.load_sprite('sword')

    main_menu = MainMenu()

    map_loader = MapLoader(MapData, NPC, Intent)

    hero = Hero(surface=resource_loader.load_sprite('hero'), intent_instance=Intent(), inventory_instance=Inventory())

    map_data, path_finder, dirty_drawing, floor_s, world_s = load_map('default', map_loader, resource_loader, hero)


    new_weapon = Weapon(generate_item_name('sword'))
    print hero.inventory
    hero.inventory.add_item(new_weapon)

    camera = Camera(starting_position=hero.positionOnMap, viewport_size=(10, 10))
    camera.set_viewport_boundaries((0, 0), map_data.mapBoundaries)

    message_log = MessageLog(defaultFont)
    message_log.position = (screen.get_size()[0] - message_log.render.get_size()[0], 0)

    # Temporary. Combat is on at the start
    in_combat = False

    entities_in_combat, reaction_order, creature_in_turn = create_combat(map_data.get_characters_on_map)

    screen.fill(colorBlack)

    new_sword = Weapon(generate_item_name(), surface=sword_surface)
    map_data.set_item_on_map(new_sword, (3, 4))

    # MAINLOOP--------------------------
    while 1:
        clock.tick(40)
        hero.intent.type = 0

        if dev_hero_undying:
            hero.sheet.fatigue = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.USEREVENT:
                if event.subtype is 'map_change':
                    try:
                        if event.data[0] == '@':
                            map_data, path_finder, dirty_drawing, floor_s, world_s = load_map('map_arena.map',
                                                                                              map_loader, resource_loader, hero)
                            combat_variables = create_combat(map_data.get_characters_on_map)
                            entities_in_combat, reaction_order, creature_in_turn = combat_variables
                            camera.set_viewport_boundaries((0, 0), map_data.mapBoundaries)
                    except IndexError:
                        print "Invalid event data: {}".format(event.data)

                elif event.subtype is "combat":

                    if event.combat_situation == 'start':
                        in_combat = True
                        reaction_order = Dice.roll_reactions(entities_in_combat)
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
                        reaction_order = Dice.roll_reactions(entities_in_combat)
                        creature_in_turn = None
                        message_log.newline('EOP- RR')
                        pathfinding_screen_reset = True
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                             subtype="combat", combat_situation='first_turn'))

                    if event.combat_situation == "end":
                        in_combat = False

                elif event.subtype is 'menu':
                    main_menu.open_menu(screen)

            if event.type == pygame.KEYUP:
                if print_keypresses == True:
                    print event.key
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
                    npc = add_monster_to_random_position(map_data, NPC(resource_loader.load_sprite('thug'),
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
                # , : Pick item
                elif event.key == pygame.K_COMMA:
                    pick_up_item(hero, map_data)
                # > : Change map
                elif event.key == 60 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    push_new_user_event('map_change', data='@')

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
                                      message_log, map_data, entities_in_combat, reaction_order,
                                      sword_surface=sword_surface)

                    elif hero.intent.type == intent.WAIT:
                        pass
                    else:
                        raise "No Hero intention_:{}".format(hero.intent.type)

            elif isinstance(creature_in_turn, NPC):
                npc = creature_in_turn
                path = path_finder.find_path_between_points(npc.positionOnMap, hero.positionOnMap,
                                                            report_time=report_pathfinder_time)
                if enable_pathfinder_screen == True:
                    if pathfinding_screen_reset == True:
                        pathfinder_screen_s.fill(colorBlack)
                        pathfinding_screen_reset = False
                    draw_pathfinder_path(pathfinder_screen_s, path)
                if path == 'path not found' or path == None:
                    pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                         subtype="combat", combat_situation="turn_change"))
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

        camera.set_tile_position(hero.positionOnMap)

        if enable_pathfinder_screen:
            dirty_drawing.issue_world_surface_redraw()

        dirty_drawing.draw(screen, world_s, camera, floor_s, map_data)

        if message_log.get_is_dirty is True:
            dirty_drawing.draw_message_log(screen, message_log)

        if enable_pathfinder_screen:
            pass
            # dirty_drawing.draw_pathfinder_screen(screen, pathfinder_screen_s)

        pygame.display.flip()


if __name__ == '__main__':
    main(screen_)
