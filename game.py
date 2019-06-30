#!/usr/bin/env python
# encoding: utf-8

from snake import Snake
import random
import pygame, sys
from pygame.locals import *


pygame.init()

USIZE = 20 # 单位长度
ROWS = 25
COLUMNS = 25
size = USIZE * COLUMNS + 300, USIZE * ROWS

# set up the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (20, 160, 15)
#
GAMESTATE = 'playing'
score = 0
isFruitShowing = False
isLocked = False # 加锁，防止一个时间周期内改变两次方向，碰到蛇身第二节。
isFullScreen = False
fruitPos = None
snake = Snake()
#
INITSPEED = 5
speed = INITSPEED # FPS
fpsClock = pygame.time.Clock()
#
fontObj = pygame.font.Font('freesansbold.ttf', 20)
scoreFont = pygame.font.Font('freesansbold.ttf', 32)

def newScreen(size, full=False):
    global isFullScreen
    screen = None
    if full:
        isFullScreen = True
        screen = pygame.display.set_mode(size, FULLSCREEN)
    else:
        isFullScreen = False
        screen = pygame.display.set_mode(size)
    return screen

#  screen = pygame.display.set_mode(size, FULLSCREEN)
screen = newScreen(size)
pygame.display.set_caption('mysnake 1.0')


# 背景音乐
pygame.mixer.init()
pygame.mixer.music.load('res/background.mp3')
#  pygame.mixer.music.load('res/bg.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)
soundEat = pygame.mixer.Sound('res/eat.ogg')
soundFail = pygame.mixer.Sound('res/gameover.ogg')
soundJiayou = pygame.mixer.Sound('res/jiayou.ogg')

# 辅助函数
def initGame():
    """重新开始游戏时，对游戏初始化"""
    global score, GAMESTATE, isFruitShowing, fruitPos,\
            speed, snake
    score = 0
    GAMESTATE = 'playing'
    isFruitShowing = False
    fruitPos = None
    speed = INITSPEED
    snake = Snake()
    pygame.mixer.music.rewind()
    pygame.mixer.music.unpause()
def drawFinal():
    pygame.draw.rect(screen, RED, \
            (200, 120, 400, 300))
    pygame.draw.rect(screen, BLACK, \
            (210, 130, 380, 280))
    overText = scoreFont.render('GAME OVER!',\
            True, WHITE)
    scoreText = scoreFont.render('Your Score: ' + str(score),\
            True, WHITE)
    promptText = fontObj.render('Press "ENTER" to RESTART',
            True, WHITE)
    screen.blit(overText, (300, 200))
    screen.blit(scoreText, (300, 240))
    screen.blit(promptText, (280, 290))

def drawFruit():
    """生成并绘制食物"""
    global isFruitShowing, fruitPos
    if not isFruitShowing:
        tempPos = None
        while not tempPos or tempPos in snake.bodyList:
            fX = random.randint(0, ROWS-1)
            fY = random.randint(0, ROWS-1)
            tempPos = (fX, fY)
        fruitPos = tempPos
    pygame.draw.rect(screen, RED, \
            (fruitPos[0]*USIZE, fruitPos[1]*USIZE, USIZE, USIZE))
    isFruitShowing = True

def drawSnake():
    for pos in snake.bodyList:
        pygame.draw.rect(screen, WHITE, \
                (pos[0]*USIZE, pos[1]*USIZE, USIZE, USIZE))

def redraw():
    screen.fill(GREEN)
    # 分割线
    pygame.draw.line(screen, RED, (502, 0), (502, 500), 3)
    promptText = fontObj.render('Press "SPACE" to', True, WHITE)
    promptText2 = fontObj.render('START/PAUSE', True, WHITE)
    scoreText = scoreFont.render('Score: ' + str(score), True, WHITE)
    screen.blit(promptText, (550, 100))
    screen.blit(promptText2, (560, 120))
    screen.blit(scoreText, (570, 220))
    drawSnake()
    drawFruit()

def checkCollision():
    # 吃到食物
    if tuple(snake.headPos) == fruitPos:
        soundEat.play()
        return 1
    # 碰到自己身体
    if tuple(snake.headPos) in snake.bodyList[1:]:
        return -1
    return 0

redraw()

while True:
    if isLocked:
        isLocked = False
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()
            if event.key == K_f:
                screen = newScreen(size, full=not isFullScreen)

            if GAMESTATE == 'over' and event.key == K_RETURN:
                print 'Return press'
                initGame()
            if event.key == K_SPACE:
                if GAMESTATE == 'playing':
                    GAMESTATE = 'pausing'
                    pygame.mixer.music.pause()
                elif GAMESTATE == 'pausing':
                    GAMESTATE = 'playing'
                    pygame.mixer.music.unpause()
            if GAMESTATE == 'playing' and not isLocked:
                newDirection = ''
                if event.key in (K_DOWN, K_s):
                    newDirection = 'down'
                elif event.key in (K_UP, K_w):
                    newDirection = 'up'
                elif event.key in (K_LEFT, K_a):
                    newDirection = 'left'
                elif event.key in (K_RIGHT, K_d):
                    newDirection = 'right'
                if snake.isValidDirection(newDirection):
                    snake.changeDirection(newDirection)
                    isLocked = True
        if event.type == QUIT:
            #  pygame.quit()
            sys.exit()
    if GAMESTATE == 'playing':
        result = checkCollision()
        if result == 0:
            snake.moveForward()
        elif result == 1:
            snake.moveForward(True)
            score += 1
            isFruitShowing = False
            if speed < 15:
                speed *= 1.1
            if score in (30, 50, 65, 75) or\
                (score > 75 and (score - 80) % 5 == 0):
                soundJiayou.play()
        elif result == -1:
            GAMESTATE = 'over'
            soundFail.play()
            drawFinal()
        redraw()
    elif GAMESTATE == 'over':
        pygame.mixer.music.pause()
        drawFinal()
    pygame.display.update()
    fpsClock.tick(speed)
