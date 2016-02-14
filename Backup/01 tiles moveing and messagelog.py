import sys,pygame
from collections import deque #Queues
__author__ = 'Kodex'

pygame.init()

size = width, height = 1280,840
speed = [2, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

# STARTGAME--------------------------

screen.fill(black)

textLine1 = "Welcome to the survival games."
textLine2 = "Press Space to begin."

basicFont = pygame.font.get_default_font()
basicFont = pygame.font.Font(basicFont, 15)
colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0)
line1_s = basicFont.render(textLine1, False, colorWhite, colorBlack)
line2_s = basicFont.render(textLine2, False, colorWhite, colorBlack)

lineSpace = basicFont.size(textLine1)[1]+12

screen.blit(line1_s, (10, 10))
screen.blit(line2_s, (10, 10+lineSpace))

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
for x in range( 0, 9):
    for y in range( 0, 9):
        floor_s.blit(floorTile_s, (x*64+16, y*64+16))

# Player and NPCs


class Hero:
    surface = 0
    rect = 0

    def __init__(self, img_filename):
        self.surface = pygame.image.load(img_filename)
        self.surface = pygame.transform.scale(self.surface, (64, 64))
        self.surface.set_colorkey(colorWhite)
        self.rect = self.surface.get_rect()

    def move(self, x, y):
        self.rect.move_ip(x * 64, y * 64)


class MessageLog:
    text_lines = []
    text_renders = 0 #Queue
    linesToRender = 12    
    lineHeight = 4
    render = 0 #Has the complete messageLog rendered.

    def __init__(self):
        self.text_renders = deque()

        #Calculate a size and create the 'render' surface.
        assert isinstance(basicFont, pygame.font.Font)
        test_string = "JUST A TEST-------------"
        linespace_x, linespace_y = basicFont.size(test_string)
        self.lineHeight += linespace_y

        surface_height = self.linesToRender*self.lineHeight
        self.render = pygame.Surface((linespace_x, surface_height))

        #First text.
        new_text = "Welcome."
        self.newline(new_text)

    def newline(self, string):
        new_text = string
        new_render = basicFont.render(new_text, False, colorWhite, colorBlack)
        self.text_lines.append(new_text)
        self.text_renders.append(new_render)

        #If the surface is full, pop earliest of the renders out.
        try:
            self.text_renders[self.linesToRender - 1]
        except IndexError:
            pass
        else:
            self.text_renders.popleft()

        self.renderLines()

    def renderLines(self):
        y_position = 0
        for text_render in self.text_renders:
            self.render.blit(text_render, (0, y_position))
            y_position += self.lineHeight

hero = Hero("dg_classm32_swordHero.gif")
messageLog = MessageLog()

# MAINLOOP--------------------------
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                print("DERP")
            if event.key == pygame.K_UP:
                hero.move(0, -1)
            if event.key == pygame.K_DOWN:
                hero.move(0, 1)
            if event.key == pygame.K_LEFT:
                hero.move(-1, 0)
            if event.key == pygame.K_RIGHT:
                hero.move(1, 0)

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(floor_s, (0,0))
    screen.blit(floorTile_s , ballrect)
    screen.blit(hero.surface, hero.rect.move(16, 16))
    screen.blit(messageLog.render, (50,50))
    pygame.display.flip()