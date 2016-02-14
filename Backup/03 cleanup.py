import sys, pygame
from collections import deque  # Queues
import random
import os

__author__ = 'Kodex'

pygame.init()

size = width, height = 1280, 840
colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0)

screen = pygame.display.set_mode(size)

# STARTGAME--------------------------

screen.fill(colorBlack)

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

StartMenu(defaultFont, screen)


# MAINCODE---------------------------

floorImg = pygame.image.load("dg_extra132_boulderFloor.gif")
floorTile_s = pygame.transform.scale(floorImg, (64, 64))

# Create Floor
floor_s = pygame.Surface((1280, 840))
for x in range(0, 9):
    for y in range(0, 9):
        floor_s.blit(floorTile_s, (x * 64 + 16, y * 64 + 16))


# Classes----------------------------


class Creature:
    name = ""
    surface = 0
    rect = 0
    positionOnMap = (0, 0)

    def __init__(self, img_filename):
        self.name = ""
        self.surface = pygame.image.load(img_filename)
        self.surface = pygame.transform.scale(self.surface, (64, 64))
        self.surface.set_colorkey(colorWhite)
        self.rect = self.surface.get_rect()

        self.sheet = self.Sheet()

    def move(self, x, y):
        self.rect.move_ip(x * 64, y * 64)
        self.positionOnMap = self.positionOnMap[0] + x, self.positionOnMap[1] + y

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


    def __init__(self, img_filename):
        Creature.__init__(self, img_filename)

        self.name = "Hero"

    def attack(self, target):
        assert isinstance(target, Creature)
        step_value = make_skill_roll(self.sheet.fitness, self.sheet.brawling)

        attack_report = "Attack w/ {0}D: ".format(self.sheet.fitness)

        # Overkill
        if step_value >= 6:
            target.sheet.fatigue += 1
            attack_report += "Overkill! 1 FAT dmg."
        elif step_value >= 2:
            dice = roll_dice(1)
            if dice[0] > target.sheet.ac:
                target.sheet.fatigue += 1
                attack_report += "1 FAT dmg."
            else:
                attack_report += "{0} blocked.".format(target.name)
        else:
            attack_report += "missed."

        return attack_report


class NPC(Creature):
    def __init__(self, img_filename):
        Creature.__init__(self, img_filename)


class MessageLog:
    fontSize = 20
    lineHeight = 4
    linesToRender = 20

    text_lines = []
    text_renders = 0  # Queue
    render = 0  # Has the complete messageLog rendered.
    position = (0, 0)
    font = False

    def __init__(self, font):
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

        self.renderLines()

    def renderLines(self):
        y_position = 0
        self.render.fill(colorBlack)
        for text_render in self.text_renders:
            self.render.blit(text_render, (0, y_position))
            y_position += self.lineHeight


class MapData:
    mapBoundaries = (0, 0)
    charLayer = {}

    def __init__(self, map_boundaries_t):
        self.mapBoundaries = map_boundaries_t

    def tile_occupied(self, tile_t):
        """Return occupant, false if not occupied, -1 if out of boundaries"""
        if self.in_boundaries(tile_t):
            if tile_t in self.charLayer:
                return self.charLayer[tile_t]
            else:
                return False
        return -1

    def in_boundaries(self, tile_t):
        if -1 < tile_t[0] < self.mapBoundaries[0]:
            if -1 < tile_t[1] < self.mapBoundaries[1]:
                return True
        return False

    def attempt_move(self, layerName, origin, direction):
        """Attempts to move the entity to the direction provided on the layer"""
        destination = origin[0] + direction[0], origin[1] + direction[1]
        if layerName == "char":
            occupied = self.tile_occupied(destination)
            #In Boundaries
            if occupied is not -1:
                #There is something on the tile --return it
                if occupied:
                    return occupied
                #The tile is free. move the character.
                elif not occupied:
                    try:
                        self.charLayer[destination] = self.charLayer.pop(origin)
                        return True
                    #Human error
                    except KeyError:
                        print "Error: No such key: " + str(destination) + " or: " + str(origin)
            #Out of boundaries
            else:
                print "No go: " + str(destination) + " code: " + str(self.tile_occupied(destination))
                return -1
        #Human error.
        else:
            raise StandardError("No layer named: " + layerName)


class Intent:
    move = 1
    def __init__(self):
        self.move = 1
intent = Intent()

def roll_dice(amount_of_dices):
    dicePool = []
    text = ""
    for dice in range(0, amount_of_dices):
        dicePool.append(random.randint(1, 10))
        text += "[{}] ".format(dicePool[-1])

    print text
    return dicePool

def make_skill_roll(ability, skill):
    dicePool = roll_dice(ability)
    assert (dicePool[0], int)
    step = 0
    for dice in dicePool:
        if dice <= skill:
            step += dice

    return step

mapData = MapData((9, 9))

hero = Hero("dg_classm32_swordHero.gif")
if not mapData.tile_occupied((0, 0)):
    mapData.charLayer[(0, 0)] = hero
    hero.move(0, 0)

temporaryNpc = NPC("dg_monster132_thug.gif")
temporaryNpc.name = "Thug"
if not mapData.tile_occupied((5, 5)):
    mapData.charLayer[(5, 5)] = temporaryNpc
    temporaryNpc.move(5, 5)

messageLog = MessageLog(defaultFont)
messageLog.position = (screen.get_size()[0] - messageLog.render.get_size()[0], 0)

hero_move = 0;
hero_intent = 0

# MAINLOOP--------------------------
while 1:
    hero_move = 0;
    hero_intent = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                messageLog.newline("space pressed.")

            if event.key == pygame.K_UP:
                hero_move = (0, -1)
            if event.key == pygame.K_DOWN:
                hero_move = (0, 1)
            if event.key == pygame.K_LEFT:
                hero_move = (-1, 0)
            if event.key == pygame.K_RIGHT:
                hero_move = (1, 0)
            if hero_move is not 0:
                hero_intent = intent.move

    if hero_intent is intent.move:  # There is an intent to move
        move_report = mapData.attempt_move("char", hero.positionOnMap, hero_move)
        # Legal move.
        if move_report is not -1:
            # Let's move the player
            if move_report is True:
                hero.move(*hero_move)
            # Encountered an npc.
            else:
                target = move_report
                if not isinstance(target, Creature):
                    raise TypeError(target)
                attack_report = hero.attack(target)
                messageLog.newline(attack_report)
                if target.sheet.fatigue == 4:
                    messageLog.newline("{target} is knocked out.".format(target=target.name))
                    target.surface.fill(colorWhite)
                    mapData.charLayer.pop(target.positionOnMap)
        else:
            messageLog.newline("Ouch! You bumped to a wall.")


    screen.fill(colorBlack)
    screen.blit(floor_s, (0, 0))
    screen.blit(hero.surface, hero.rect.move(16, 16))
    screen.blit(temporaryNpc.surface, temporaryNpc.rect.move(16, 16))
    screen.blit(messageLog.render, messageLog.position)
    pygame.display.flip()
