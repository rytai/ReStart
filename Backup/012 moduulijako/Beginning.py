import sys,pygame
__author__ = 'Kodex'

pygame.init()

size = width, height = 1260,840
speed = [2, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

# STARTGAME--------------------------

screen.fill(black)

textLine1 = "Welcome to the survival games."
textLine2 = "Press Space to begin."

basicFont = pygame.font.get_default_font()
basicFont = pygame.font.Font(basicFont, 15)
colorWhite = (0, 0, 0)
colorBlack = (255, 255, 255)
line1_s = basicFont.render(textLine1, False, colorWhite, colorBlack)
line2_s = basicFont.render(textLine2, False, colorWhite, colorBlack)

lineSpace = basicFont.size(textLine1)[1]+12

screen.blit(line1_s, (10, 10))
screen.blit(line2_s, (10, 10+lineSpace))

pygame.display.flip()

stuckInBeginning = True
while stuckInBeginning == True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                stuckInBeginning = False
            

# MAINCODE---------------------------

ball = pygame.image.load("ball.bmp")
ballrect = ball.get_rect()



while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                print("DERP")

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()