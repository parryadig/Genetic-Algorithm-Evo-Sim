import sys
import math
import random
import statistics
import pygame as pg
from pygame import gfxdraw

vec = pg.math.Vector2

FPS = 30
HEIGHT = 720
WIDTH = 1200
SIZE = WIDTH, HEIGHT
BOT_SIZE = 8
MAX_SPEED = 3
MAX_FORCE = 0.1
APPROACH_RADIUS = 100

screen = pg.display.set_mode(SIZE) # surface to draw to

black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)

class Food:
    def __init__(self, pos = None):
        self.pos = pos if pos != None else vec(int(random.gauss(WIDTH/2, WIDTH*0.25)), int(random.gauss(HEIGHT/2, HEIGHT*0.25)))
        self.val = 20

    def draw(self):
        gfxdraw.filled_circle(screen, int(self.pos.x), int(self.pos.y), 4, green)