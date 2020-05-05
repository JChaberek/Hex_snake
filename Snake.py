import os
import time
import numpy as np
from pynput import keyboard
from termcolor import colored

width, height = 78, 17
keys = []


# controls q - upper right, a - right, z - bottom right, e - upper left, d - left, c - bottom left

class snake_map:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.ltype, self.ftype = "*", " "
        self.map = [[self.ltype for _ in range(x)] for _ in range(y)]

    def init_map(self):
        for j, js in zip(range(2, self.x, 4), range(3, self.x, 4)):
            self.map[1][j] = self.ftype
            self.map[1][js] = self.ftype
            self.map[self.y - 2][js] = self.ftype
            self.map[self.y - 2][j] = self.ftype
        for i in range(2, self.y - 2, 4):
            for j in range(1, self.x - 1):
                self.map[i][j] = self.ftype
        for i in range(3, self.y - 2, 2):
            for j in range(2, self.x - 2):
                self.map[i][j] = self.ftype
        for i in range(4, self.y - 2, 4):
            for j in range(3, self.x - 3):
                self.map[i][j] = self.ftype

    def draw_map(self, animal, fruits):
        for i in range(self.y):
            for j in range(self.x):
                if self.map[i][j] == self.ltype:
                    color = "blue"
                if self.map[i][j] == animal[0].ftype:
                    color = "green"
                if self.map[i][j] == fruits.ftype:
                    color = "red"
                print(colored(self.map[i][j], color), end="")
            print("")

    def update_field(self, x, y):
        self.map[y][x] = self.ftype
        self.map[y][x + 1] = self.ftype
        self.map[y + 1][x - 1] = self.ftype
        self.map[y + 1][x] = self.ftype
        self.map[y + 1][x + 1] = self.ftype
        self.map[y + 1][x + 2] = self.ftype
        self.map[y + 2][x] = self.ftype
        self.map[y + 2][x + 1] = self.ftype


class snake(snake_map):
    def __init__(self, hex_fields, terrain, ftype):
        self.map = terrain
        self.x, self.y = hex_fields[1], hex_fields[0]
        self.ftype = ftype
        self.update_field(self.x, self.y)


class fruit(snake):
    def __init__(self, hex_fields, terrain, ftype):
        super().__init__(hex_fields, terrain, ftype)


def check_space(map, x, mode, animal):
    if mode == 1:
        x_cords, y_cords = x[1::2], x[0::2]
    else:
        i, j = animal[1], animal[0]
        cords = [i, j, i, j + 1, i + 1, j - 1, i + 1, j, i + 1, j + 1, i + 1, j + 2, i + 2, j, i + 2, j + 1]
        x_cords, y_cords = cords[1::2], cords[0::2]
    for y, x in zip(y_cords, x_cords):
        try:
            if map[y][x] == "@":
                return True, 1
            if map[y][x] == "*" or map[y][x] == "#":
                return False, 0
        except:
            return False, 0
    return True, 0


def get_hex(hex, game):
    for i in range(1, height - 1):
        if game.map[i][1] == game.ftype:
            for j in range(1, game.x - 1, 4):
                hex.append([i - 1, j + 1, i - 1, j + 2, i, j, i, j + 1, i, j + 2, i, j + 3, i + 1, j + 1, i + 1, j + 2])
        if game.map[i][2] == game.ltype:
            for j in range(3, game.x - 3, 4):
                hex.append([i - 1, j + 1, i - 1, j + 2, i, j, i, j + 1, i, j + 2, i, j + 3, i + 1, j + 1, i + 1, j + 2])


def move(game, animal, direction, hex):
    if direction == "a":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x - 4, animal[0].y
    elif direction == "d":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x + 4, animal[0].y
    elif direction == "q":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x - 2, animal[0].y - 2
    elif direction == "z":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x - 2, animal[0].y + 2
    elif direction == "e":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x + 2, animal[0].y - 2
    elif direction == "c":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x + 2, animal[0].y + 2
    is_ok, is_fruit = check_space(game.map, hex, 0, [new_x, new_y])

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
            animal.insert(0, snake([new_y, new_x], game.map, "#"))
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


def main_game():
    game = snake_map(width, height)
    hex, animal = [], []
    spawn_animal, spawn_fruit, game_loop = False, False, True
    game.init_map()
    get_hex(hex, game)

    while not spawn_animal:
        x = np.random.randint(0, len(hex))
        spawn_animal, _ = check_space(game.map, hex[x], 1, 0)
    animal.insert(0, snake(hex[x], game.map, "#"))
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while game_loop:
        if not spawn_fruit:
            while not spawn_fruit:
                x = np.random.randint(0, len(hex))
                spawn_fruit, _ = check_space(game.map, hex[x], 1, 0)
        fruit_for_snake = fruit(hex[x], game.map, "@")
        game.draw_map(animal, fruit_for_snake)
        time.sleep(0.8)
        if len(keys) > 0:
            direction = keys[-1]
            game_loop, spawn_fruit = move(game, animal, direction, hex)
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    print(colored("YOU LOST!", "red"))


main_game()
