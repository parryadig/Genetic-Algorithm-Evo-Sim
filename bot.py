import sys
import math
import random
import statistics
import pygame as pg
from pygame import gfxdraw
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

selected_dict = {0: (200, 200, 200), 1: (0, 255, 255)}

screen = pg.display.set_mode(SIZE) # surface to draw to

black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)

class Bot:
    def __init__(self, pos = None, dna = None):
        self.seek_status = 0
        self.is_selected = 0
        # Establish position
        if pos != None:
            self.pos = pos
            self.pos.y += 50
        else:
            self.pos = vec(random.randint(0, WIDTH), random.randint(0, HEIGHT))

        # Following attributes are controlled by the DNA
        if dna != None:
            # [max_hp, food_pref, food_desire, poison_desire, food_vision, poison_vision]
            self.max_hp = dna[0]
            self.hp = dna[0]
            self.food_pref = dna[1]
            self.food_desire = dna[2]
            self.poison_desire = dna[3]
            self.food_vision = dna[4]
            self.poison_vision = dna[5]
            self.max_vel = dna[6]
            self.gen = dna[7]
        else:
            self.max_hp = 100
            self.hp = 100
            self.food_pref = random.uniform(0, 1)
            self.food_desire = 0.5
            self.poison_desire = 0.5
            self.food_vision = random.randint(10, 50)
            self.poison_vision = random.randint(10, 50)
            self.max_vel = random.uniform(1, MAX_SPEED)
            self.gen = 0

        self.vel = vec(random.uniform(0, self.max_vel)).rotate(random.uniform(0, 360))
        self.acc = vec(0, 0)


    # Helper function to find closest food/ poison
    def get_target(self, foods, poisons):
        chance = random.random()
        # Check what is visible each time function is called
        if chance > self.food_pref:
            found_item = self.find_closest(foods, 'f')
            if found_item == None:
                found_item = self.find_closest(poisons, 'p')

        elif chance < self.food_pref:
            found_item = self.find_closest(poisons, 'p')
            if found_item == None:
                found_item = self.find_closest(foods, 'f')

        return found_item

    def find_closest(self, target_array, target_type):
        closest = None
        dist = float('inf')

        # Find closest
        if target_type == 'f':
            for i in range(0, len(target_array)):
                dist_to_item = self.pos.distance_to(target_array[i].pos) 
                if dist_to_item < self.food_vision and dist_to_item < dist:
                    dist = dist_to_item
                    closest = target_array[i]
        elif target_type == 'p':
            for i in range(0, len(target_array)):
                dist_to_item = self.pos.distance_to(target_array[i].pos) 
                if dist_to_item < self.poison_vision and dist_to_item < dist:
                    dist = dist_to_item
                    closest = target_array[i]

        return closest

    def seek(self, target_pos):
        self.desired = (target_pos - self.pos)
        # dist = self.desired.length()
        self.desired.normalize_ip()
        # if dist < APPROACH_RADIUS:
        #     self.desired *= dist / APPROACH_RADIUS * self.max_vel
        # else:
        self.desired *= self.max_vel
        steer = (self.desired - self.vel)

        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)

        return steer

    def flee(self, target_pos):
        steer = vec(0, 0)
        dist = self.pos - target_pos
        if dist.length() < self.poison_vision:
            self.desired = (self.pos - target_pos).normalize() * self.max_vel
        else:
            self.desired = self.vel.normalize() * self.max_vel

        steer = (self.desired - self.vel)

        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)

        return steer

    def wander(self):
        # Circle in front of agent at a distance of 150
        future = self.pos + self.vel.normalize() * 150

        if future.x > WIDTH or future.x < 0:
            future.x *= -1

        if future.y > HEIGHT or future.y < 0:
            future.y *= -1

        target = future + vec(100, 0).rotate(random.uniform(0, 360))

        return self.seek(target)

    def to_dna(self):
        return [self.max_hp, self.food_pref, self.food_desire, self.poison_desire, self.food_vision, self.poison_vision, self.max_vel, self.gen]

        

    def breed_chance(self):
        will_breed = random.random()

        if will_breed < 0.0002:
            dna = self.mutate_chance(self.to_dna())
            return Bot(pos = vec(WIDTH/2, HEIGHT/2 ), dna = dna)

        return None

    def mutate_chance(self, dna):
        will_mutate = random.random()

        if will_mutate < 1:
            print("Mutation occured.")
            print("Old: ", dna)
            new_dna = dna.copy()
            for i in range(len(dna) - 1):
                deviation = dna[i] * 0.1
                new_dna[i] += random.uniform(-deviation, deviation)
                if isinstance(dna[i], int):
                    new_dna[i] = math.floor(new_dna[i])
            new_dna[-1] += 1

            print("New: ", new_dna)

        return new_dna

    def is_dead(self):
        if self.hp <= 0:
            return True

        return False

    def did_eat(self, food_list, poison_list):

        for food in food_list:
            if self.pos.distance_to(food.pos) < 5:
                self.hp += food.val
                self.target = None
                return food

        for poison in poison_list:
            if self.pos.distance_to(poison.pos) < 5:
                self.hp += poison.val
                self.target = None
                return poison

        return None

    def update(self, foods, poisons):
        if math.ceil(self.is_selected) == 1:
            self.is_selected -= 0.02
        else:
            self.is_selected = 0

        global selected_dict

        # Aging
        self.hp -= 0.05
        # Acquire target
        self.target = self.get_target(foods, poisons)

        # If there is nothing in agents FoV
        if self.target == None:
            self.seek_status = 0
            self.acc += self.wander()

        # Case food
        elif isinstance(self.target, Food):
            chance = random.random()
            if chance < self.food_desire:
                self.seek_status = 1
                self.acc += self.seek(self.target.pos)
            else:
                chance = random.random()
                if chance > 0.5:
                    self.seek_status = 0
                    self.acc += self.wander()
                else:
                    self.seek_status = -1
                    self.acc += self.flee(self.target.pos)

        # Case poison
        elif isinstance(self.target, Poison):
            chance = random.random()
            if chance < self.poison_desire:
                self.seek_status = 1
                self.acc += self.seek(self.target.pos)
            else:
                chance = random.random()
                if chance > 0.5:
                    self.seek_status = 0
                    self.acc += self.wander()
                else:
                    self.seek_status = -1
                    self.acc += self.flee(self.target.pos)

        self.vel += self.acc

        if self.vel.length() > self.max_vel:
            self.vel.scale_to_length(self.max_vel)

        # if self.pos.x > WIDTH or self.pos.x < 0:
        #     self.vel.x *= -1

        # if self.pos.y > HEIGHT or self.pos.y < 0:
        #     self.vel.y *= -1

        self.pos += self.vel

        gfxdraw.aacircle(
            screen, int(self.pos.x), int(self.pos.y),
            BOT_SIZE + self.food_vision, (0, 255, 0))

        gfxdraw.aacircle(
            screen, int(self.pos.x), int(self.pos.y),
            BOT_SIZE + self.poison_vision, (255, 0, 0))

        gfxdraw.filled_circle(
            screen, int(self.pos.x), int(self.pos.y), 
            BOT_SIZE, selected_dict[math.ceil(self.is_selected)])

        if self.food_pref > 0.5:
            gfxdraw.filled_circle(
                screen, int(self.pos.x), int(self.pos.y), 
                math.floor(BOT_SIZE/4), green)
        else:
            gfxdraw.filled_circle(
                screen, int(self.pos.x), int(self.pos.y), 
                math.floor(BOT_SIZE/4), red)