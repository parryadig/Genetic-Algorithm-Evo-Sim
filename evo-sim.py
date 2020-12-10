"""
evo-sim.py

Evolution simulator, draws upon concepts in genetic algorithms & pathfinding

10 autonomous agents (with random dna) spawn.
Initially they can't tell food from poison


To do:
    - Change did_eat() to eat anything agent crosses (done)
    - Make speed a trait
    - Make vision radius for poison (done)
    - Add fleeing behaviour (done)
    - Add weighting on seeking & fleeing (done)
    - 

"""

import sys
import math
import random
import statistics
import pygame as pg
from pygame import gfxdraw
from bot import Bot
from food import Food
from poison import Poison

vec = pg.math.Vector2

FPS = 30
HEIGHT = 720
WIDTH = 1200
SIZE = WIDTH, HEIGHT
BOT_SIZE = 8
MAX_SPEED = 3
MAX_FORCE = 0.1
APPROACH_RADIUS = 100

black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)

selected_dict = {0: (200, 200, 200), 1: (0, 255, 255)}

bots_list, food_list, poison_list = [], [], []

best_so_far = None

screen = pg.display.set_mode(SIZE) # surface to draw to
pg.display.set_caption("Evolution Simulator")

def get_best(bots):
    best = None
    best_fitness = 0
    for bot in bots:
        bot_dna = bot.to_dna()
        fitness = (bot_dna[0] / 100) + (bot_dna[1] / 0.5) + (bot_dna[2] - bot_dna[3]) + bot_dna[6]
        if fitness > best_fitness:
            best_fitness = fitness
            best = bot
    return best

def print_bot(bot):
    if bot.seek_status == 1:
        behav = "Seeking"
    elif bot.seek_status == -1:
        behav = "Fleeing"
    else:
        behav = "Wandering"

    priority = "Food" if bot.food_pref > 0.5 else "Poison"
    behav_food = "{} ({})".format(str(bot.food_desire), "Seeking" if bot.food_desire > 0.5 else "Fleeing")
    behav_poison = "{} ({})".format(str(bot.poison_desire), "Seeking" if bot.poison_desire > 0.5 else "Fleeing")
    print("""
ID: {}
Max HP: {:.2f}
Current HP: {:.2f}
Priority: {}
Behavior (food): {}
Behavior (poison): {}
Vision radius (Food): {:.2f}
Vision radius (Poison): {:.2f}
Max speed: {:.2f}
Current behaviour: {}
Generation: {}
-----------------------
    """.format(
        id(bot), bot.max_hp, bot.hp, priority, behav_food, behav_poison,
        bot.food_vision, bot.poison_vision, bot.max_vel, behav, bot.gen))

for i in range(20):
    bots_list.append(Bot())

for i in range(20):
    food_list.append(Food())
    poison_list.append(Poison())

clock = pg.time.Clock()
while 1:
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT: sys.exit()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p:
                print("Best in current generation:")
                get_best(bots_list).is_selected = 1
                print_bot(get_best(bots_list))
            elif event.key == pg.K_o:
                print("Best ever:")
                print_bot(best_so_far)
            elif event.key == pg.K_u:
                print("Mean of current generation:")
                # print("HP: {}\nMagG: {}\nMagR: {}\nVision: {}".format(statistics.mean(bots_list.))
            elif event.key == pg.K_EQUALS and FPS < 60:
                FPS += 10
                print("Set FPS to {}".format(FPS))
            elif event.key == pg.K_MINUS and FPS > 10:
                FPS -= 10
                print("Set FPS to {}".format(FPS))

    screen.fill(black)

    # Saving the best ever
    new_best = get_best(bots_list)

    if new_best != None:
        if best_so_far == None:
            best_so_far = new_best
        elif get_best([best_so_far, new_best]) == new_best:
            best_so_far = new_best

    if len(bots_list) < 1 or random.random() < 0.0001:
        bots_list.append(Bot())

    if len(food_list) < 2 or random.random() < 0.01:
        food_list.append(Food())

    if len(poison_list) < 15:
        if len(poison_list) < 2 or random.random() < 0.01:
            poison_list.append(Poison())

    for food in food_list:
        food.draw()

    for poison in poison_list:
        poison.draw()

    for bot in bots_list:
        if bot.pos.distance_to(pg.mouse.get_pos()) <= 20 and pg.mouse.get_pressed()[0] == 1:
            print_bot(bot)
            bot.is_selected = 1

        if not bot.is_dead():
            bot.update(food_list, poison_list)

            did_eat = bot.did_eat(food_list, poison_list)
            if did_eat is not None:
                just_ate = "poison" if isinstance(did_eat, Poison) else "food"
                print("Bot {} just ate some {}!".format(id(bot), just_ate))
                try:
                    food_list.remove(did_eat)
                except:
                    poison_list.remove(did_eat)

            did_breed = bot.breed_chance()

            if did_breed != None:
                print("Bot {} has produced offspring.".format(id(bot)))
                bots_list.append(did_breed)
        else:
            print("Bot {} has died.".format(id(bot)))
            food_list.append(Food(bot.pos))
            bots_list.remove(bot)

    pg.display.flip()
