import pygame
import random

pygame.init()

SCREEN_HEIGHT = 720
SCREEN_WIDTH = 720

RUNNING = True

mainClock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

x = 100
y = 100

yv = 1
ya = 0.15

font = pygame.font.Font('freesansbold.ttf', 32)
text = font.render('Test', True, 'white')
textRect = text.get_rect()
textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

alive = True

obsx = []
obsy = []
heights = []
spawn = False
obsx.append(720)
obsy.append(random.randint(100, 400))
heights.append(200)
cnt = 1
points = 0

while RUNNING and alive:

    dt = mainClock.tick(60) * 0.001 * 60

    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            RUNNING = False
        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_UP or events.key == pygame.K_SPACE:
                yv = -5
                if ya == 0:
                    ya = 0.15

    # "AI"
    n = 0
    if obsx[0] < 100 - 20:
        n = 1
    if y + 60 + yv + ya > obsy[n] + heights[n]:
        yv = -5

    yv = yv + ya * dt

    y += yv * dt + (ya * 0.5) * (dt * dt)

    screen.fill((0, 0, 0))

    # pygame.draw.circle(screen, (123, 123, 123), (x, y), 30, 10)
    pygame.draw.rect(screen, (255, 255, 255), (100, y, 60, 60), 5, 1)
    # pygame.draw.circle(screen, (255, 255, 255), (x + 30, y - 30), 30, 5)
    # the bird

    textRect.center = (SCREEN_WIDTH // 2, 80)
    text = font.render(str(points), True, 'white')

    screen.blit(text, textRect)

    for i in range(cnt):
        n = cnt - i - 1
        xx = obsx[n]
        yy = obsy[n]
        hh = heights[n]

        if xx > - 20:
            if 98 <= xx <= 100:
                points += 1

            if 420 <= xx <= 422:
                spawn = True

            pygame.draw.rect(screen, (255, 255, 255), (xx, 0, 20, yy), 3, 1)  # top rect
            pygame.draw.rect(screen, (255, 255, 255), (xx, yy + hh, 20, 720 - yy - hh), 3, 1)  # bottom rect
            obsx[n] -= 3

            if (100 - 20 <= xx <= 100 + 60) and (-60 < y <= yy or y + 60 >= yy + hh):  # collision detection
                alive = False
        else:
            obsx.remove(xx)
            obsy.remove(yy)
            heights.remove(hh)
            cnt -= 1

    if spawn:
        obsx.append(720)
        obsy.append(random.randint(130, 400))
        heights.append(random.randint(115, int(160 * (0.95 ** points + 1))))
        cnt += 1
        spawn = False

    if y + 60 > SCREEN_HEIGHT:
        yv = 0
        ya = 0
        y = SCREEN_HEIGHT - 60

    yv *= 0.99

    pygame.display.update()
