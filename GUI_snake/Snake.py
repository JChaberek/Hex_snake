import os
import time
import numpy as np
from pynput import keyboard
from termcolor import colored

width, height = 78, 20
keys = []


# controls q - upper right, a - right, z - bottom right, e - upper left, d - left, c - bottom left

# initialize map
class snake_map:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.ltype, self.ftype = "*", " "
        self.map = [[self.ltype for _ in range(x)] for _ in range(y)]

    def init_map(self):
        for i in range(0, self.y, 4):
            for j in range(self.x - 2):
                self.map[i][j] = self.ftype
        for i in range(2, self.y, 4):
            for j in range(1, self.x - 1):
                self.map[i][j] = self.ftype

    def update_field(self, x, y):
        self.map[y][x] = self.ftype
        self.map[y][x + 1] = self.ftype


class snake(snake_map):
    def __init__(self, hex_fields, terrain, ftype):
        self.map = terrain
        self.x, self.y = hex_fields[1], hex_fields[0]
        self.ftype = ftype
        self.update_field(self.x, self.y)


class fruit(snake):
    def __init__(self, hex_fields, terrain, ftype):
        super().__init__(hex_fields, terrain, ftype)


# checks if the next hexagonal field is free, locked or you can collect a fruit
def check_space(map, x, mode, animal, key):
    if mode == 1:
        x_cords, y_cords = x[1::2], x[0::2]
    else:
        i, j = animal[1], animal[0]
        cords = [i, j, i, j + 1]
        x_cords, y_cords = cords[1::2], cords[0::2]
    for y, x in zip(y_cords, x_cords):
        try:
            if y < 0 and key in ["q", "e", "t", "u"]:
                return False, 0
            elif y > 18 and key in ["z", "c", "b", "m"]:
                return False, 0
            elif x < 0 and key in ["a", "q", "z", "t", "g", "b"]:
                return False, 0
            elif x >= 77 and key in ["e", "d", "c", "u", "j", "m"]:
                return False, 0
            else:
                if map[y][x] == "@":
                    return True, 1
                if map[y][x] in animal:
                    return False, 0
        except Exception as e:
            return False, 0
    return True, 0


# counts hexagonal fields on the map
def get_hex(hex, game):
    for i in range(0, height, 2):
        if game.map[i][0] == game.ftype:
            for j in range(0, game.x - 2, 2):
                hex.append([i, j, i, j + 1])
            continue
        if game.map[i][1] == game.ftype:
            for j in range(1, game.x - 1, 2):
                hex.append([i, j, i, j + 1])


def move(game, animal, direction, hex):
    if direction == "a" or direction == "g":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x - 2, animal[0].y
    elif direction == "d" or direction == "j":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x + 2, animal[0].y
    elif direction == "q" or direction == "t":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x - 1, animal[0].y - 2
    elif direction == "z" or direction == "b":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x - 1, animal[0].y + 2
    elif direction == "e" or direction == "u":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x + 1, animal[0].y - 2
    elif direction == "c" or direction == "m":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x + 1, animal[0].y + 2
    is_ok, is_fruit = check_space(game.map, hex, 0, [new_x, new_y, "#", "+"], direction)

    # if next field is empty or you can get a fruit
    if is_ok:
        animal_copy = []
        if is_fruit == 0:
            for i in range(len(animal)):
                if i == 0:
                    animal_copy.append([animal[i].x, animal[i].y])
                    animal[i].x, animal[i].y = new_x, new_y
                if i > 0:
                    animal_copy.append([animal[i].x, animal[i].y])
                    animal[i].x, animal[i].y = animal_copy[i - 1][0], animal_copy[i - 1][1]
                animal[i].update_field(animal[i].x, animal[i].y)
            game.update_field(prev_x, prev_y)
            return True, True
        elif is_fruit == 1:
            animal.insert(0, snake([new_y, new_x], game.map, animal[0].ftype))
            return True, False
    else:
        return False, True


def on_press(key):
    try:
        k = key.char
    except:
        k = key.name
    if k == "a":
        keys.append("a")
    if k == "d":
        keys.append("d")
    if k == "q":
        keys.append("q")
    if k == "z":
        keys.append("z")
    if k == "e":
        keys.append("e")
    if k == "c":
        keys.append("c")
