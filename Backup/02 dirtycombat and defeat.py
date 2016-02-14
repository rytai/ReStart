import sys, pygame
from collections import deque  # Queues
import random
import os

__author__ = 'Kodex'

pygame.init()

size = width, height = 1280, 840
speed = [2, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

# STARTGAME--------------------------

screen.fill(black)

textLine1 = "Welcome to the survival games."
textLine2 = "Press Space to begin."

defaultFont = pygame.font.get_default_font()
basicFont = pygame.font.Font(defaultFont, 15)
colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0)
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


# MAINCODE---------------------------

floorImg = pygame.image.load("dg_extra132_boulderFloor.gif")
floorTile_s = pygame.transform.scale(floorImg, (64, 64))
ballrect = floorTile_s.get_rect()

# Create Floor
floor_s = pygame.Surface((1280, 840))
for x in range(0, 9):
    for y in range(0, 9):
        floor_s.blit(floorTile_s, (x * 64 + 16, y * 64 + 16))


# Player and NPCs


class Hero:
    surface = 0
    rect = 0
    name = ""
    positionOnMap = (0, 0)

    sheet = 0

    def __init__(self, img_filename):
        self.name = "Hero"
        self.surface = pygame.image.load(img_filename)
        self.surface = pygame.transform.scale(self.surface, (64, 64))
        self.surface.set_colorkey(colorWhite)
        self.rect = self.surface.get_rect()

        self.sheet = self.Sheet()

    def move(self, x, y):
        self.rect.move_ip(x * 64, y * 64)
        self.positionOnMap = self.positionOnMap[0] + x, self.positionOnMap[1] + y

    def attack(self, target):
        assert isinstance(target, Hero)
        success = make_skill_roll(self.sheet.fitness, self.sheet.brawling)

        attack_report = "Attack w/ {0}D: ".format(self.sheet.fitness)

        # Overkill
        if success >= 4:
            target.sheet.fatigue += 1
            attack_report += "Overkill! 1 FAT dmg."
        elif success >= 0:
            print roll_dice(1)
            if roll_dice(1)[0] > target.sheet.ac:
                target.sheet.fatigue += 1
                attack_report += "1 FAT dmg."
            else:
                attack_report += "{0} blocked.".format(target.name)
        elif success < 0:
            attack_report += "missed."

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

            self.brawling = 3


class MessageLog:
    fontSize = 20
    lineHeight = 4
    linesToRender = 12

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
            if occupied is not -1:
                if not occupied:
                    try:
                        self.charLayer[destination] = self.charLayer.pop(origin)
                        return True
                    except KeyError:
                        print "Error: No such key: " + str(destination) + " or: " + str(origin)
                if occupied:
                    return occupied

            else:
                print "No go: " + str(destination) + " code: " + str(self.tile_occupied(destination))
        else:
            raise StandardError("No layer named: " + layerName)


def roll_dice(amount_of_dices):
    dicePool = []
    for dice in range(0, amount_of_dices):
        dicePool.append(random.randint(1, 10))

    return dicePool

def make_skill_roll(ability, skill):
    dicePool = roll_dice(ability)
    assert (dicePool[0], int)
    step = 0
    for dice in dicePool:
        if dice <= skill:
            step += dice

    print "Skill roll: a"+str(ability)+" s"+str(skill)+"steps "+str(step)
    if step <= skill - 4:  # Calamity
        return -2
    elif step < skill:  # Fail
        return -1
    elif step >= skill:  #Success/Overkill
        return step

mapData = MapData((9, 9))

hero = Hero("dg_classm32_swordHero.gif")
if not mapData.tile_occupied((0, 0)):
    mapData.charLayer[(0, 0)] = hero
    hero.move(0, 0)

temporaryNpc = Hero("dg_monster132_thug.gif")
temporaryNpc.name = "Thug"
if not mapData.tile_occupied((5, 5)):
    mapData.charLayer[(5, 5)] = temporaryNpc
    temporaryNpc.move(5, 5)

messageLog = MessageLog(defaultFont)
messageLog.position = (screen.get_size()[0] - messageLog.render.get_size()[0], 0)

# MAINLOOP--------------------------
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                messageLog.newline("space pressed.")

            hero_move = 0;
            if event.key == pygame.K_UP:
                hero_move = (0, -1)
            if event.key == pygame.K_DOWN:
                hero_move = (0, 1)
            if event.key == pygame.K_LEFT:
                hero_move = (-1, 0)
            if event.key == pygame.K_RIGHT:
                hero_move = (1, 0)

            if hero_move is not 0:
                move_success = mapData.attempt_move("char", hero.positionOnMap, hero_move)
                if move_success is True:  # Let's move
                    hero.move(*hero_move)
                elif isinstance(move_success, Hero):  # Let's attack
                    target = move_success
                    attack_report = hero.attack(target)
                    messageLog.newline(attack_report)

                    if target.sheet.fatigue == 4:
                        messageLog.newline("{target} is knocked out.".format(target=target.name))
                        target.surface.fill(colorWhite)
                        mapData.charLayer.pop(target.positionOnMap)

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(floor_s, (0, 0))
    screen.blit(floorTile_s, ballrect)
    screen.blit(hero.surface, hero.rect.move(16, 16))
    screen.blit(temporaryNpc.surface, temporaryNpc.rect.move(16, 16))
    screen.blit(messageLog.render, messageLog.position)
    pygame.display.flip()
