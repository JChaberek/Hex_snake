import os
import time
import random
import numpy as np
from pynput import keyboard
from termcolor import colored

width, height = 78, 20
keys = []

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


# check if the next hexagonal field is free, locked or you can collect a fruit
def check_space(map, x_g, mode, animal, key):
    if mode == 1:
        x_cords, y_cords = x_g[1::2], x_g[0::2]
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
                elif map[y][x] in animal:
                    return False, 0
        except Exception as e:
            print(e)
            return False, 0
    return True, 0


# count hexagonal fields on the map
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
    move_made = False
    if direction == "a" or direction == "g":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x - 2, animal[0].y
        move_made = True
    elif direction == "d" or direction == "j":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x + 2, animal[0].y
        move_made = True
    elif direction == "q" or direction == "t":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x - 1, animal[0].y - 2
        move_made = True
    elif direction == "z" or direction == "b":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x - 1, animal[0].y + 2
        move_made = True
    elif direction == "e" or direction == "u":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x + 1, animal[0].y - 2
        move_made = True
    elif direction == "c" or direction == "m":
        prev_x, prev_y = animal[-1].x, animal[-1].y
        new_x, new_y = animal[0].x + 1, animal[0].y + 2
        move_made = True
    if move_made:
        is_ok, is_fruit = check_space(game.map, hex, 0, [new_x, new_y, "#", "+"], direction)
    else:
        return True, True
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

# main function responsible for mechanics
def move_anim(p1_can_play, p2_can_play, spawn_fruit, animal1, animal2, points1, points2, fruit_on_map,
                  p1_keys, p2_keys, hot_seat, against_ai, game, hexes, scoreboard, game_loop):
    if hot_seat and against_ai is 0:
        # if both players pressed a key
        if len(p1_keys) > 0 and len(p2_keys) > 0:
            # if player1 or player2 can play, make a next move
            if p1_can_play:
                p1_can_play, spawn_fruit1 = move(game, animal1, p1_keys[-1], hexes)
            if p2_can_play:
                p2_can_play, spawn_fruit2 = move(game, animal2, p2_keys[-1], hexes)
            if p2_can_play is False and p1_can_play is False:
                game_loop = False
            if p1_can_play:
                if spawn_fruit1 is not True:
                    points1 += 10
                    spawn_fruit = False
            if p2_can_play:
                if spawn_fruit2 is not True:
                    points2 += 10
                    spawn_fruit = False
            scoreboard.setText("1.P1 points - " + str(points1) + " | 2.P2 points - " + str(points2))

    elif hot_seat is 0 and against_ai:
        if len(p1_keys) > 0:
            key = calculate_next_move(game, animal2, fruit_on_map, hexes)
            p2_keys.append(key)
            if p1_can_play:
                p1_can_play, spawn_fruit1 = move(game, animal1, p1_keys[-1], hexes)
            if p2_can_play:
                p2_can_play, spawn_fruit2 = move(game, animal2, p2_keys[-1], hexes)
            if p2_can_play is False and p1_can_play is False:
                game_loop = False
            if p1_can_play:
                if spawn_fruit1 is not True:
                    points1 += 10
                    spawn_fruit = False
            if p2_can_play:
                if spawn_fruit2 is not True:
                    points2 += 10
                    spawn_fruit = False
            scoreboard.setText("1.P1 points - " + str(points1) + " | 2.P2 points - " + str(points2))

    elif hot_seat is 0 and against_ai is 0:
        if len(p1_keys) > 0:
            game_loop, spawn_fruit = move(game, animal1, p1_keys[-1], hexes)
            if spawn_fruit is not True:
                points1 += 10
                scoreboard.setText("Points - " + str(points1))

    return spawn_fruit, points1, points2, p1_can_play, p2_can_play, game_loop

# function responsible for AI in game
def calculate_next_move(game, animal, fruit, hex, p2_controls):
    final_key = ""
    posible_moves = []

    # check if snake can move in a new direction
    for key in p2_controls:
        if key == "g":
            new_x, new_y = animal[0].x - 2, animal[0].y
        elif key == "j":
            new_x, new_y = animal[0].x + 2, animal[0].y
        elif key == "t":
            new_x, new_y = animal[0].x - 1, animal[0].y - 2
        elif key == "b":
            new_x, new_y = animal[0].x - 1, animal[0].y + 2
        elif key == "u":
            new_x, new_y = animal[0].x + 1, animal[0].y - 2
        elif key == "m":
            new_x, new_y = animal[0].x + 1, animal[0].y + 2
        is_ok, _ = check_space(game.map, hex, 0, [new_x, new_y, "#", "+"], key)
        if is_ok:
            posible_moves.append([key, new_x, new_y])

    # if snake doesnt have any possible moves, pick a random direction and die
    if len(posible_moves) == 0:
        return random.choice(p2_controls)
    # if snake has option to move, pick field with the shortest distance to fruit
    else:
        distance = np.infty
        for move in posible_moves:
            temp_dist = np.sqrt(np.power((fruit.x - move[1]), 2) + np.power((fruit.y - move[2]), 2))
            if temp_dist < distance:
                distance = temp_dist
                final_key = move[0]
    return final_key


