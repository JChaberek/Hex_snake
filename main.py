import numpy as np
import sys
import Snake
import time
import PySide2.QtGui
import socket
import pickle
import random
import json
import images
import xml.etree.ElementTree as ET
from Snake import snake_map, snake, fruit
from PySide2.QtGui import QPixmap, QBrush, QColor
from PySide2.QtCore import QRect, QPointF
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, \
    QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from threading import Thread
from copy import deepcopy

# keys settings
p1_controls = ["q", "a", "z", "e", "d", "c"]
p2_controls = ["t", "g", "b", "u", "j", "m"]
width, height = 78, 20
p1_keys, new_list, p2_keys = [], [], []

def exit_app():
    sys.exit(0)

class window(QWidget):
    def __init__(self):
        # main window settings
        super().__init__()
        self.setWindowTitle("Snake")
        self.setGeometry(150, 50, 820, 320)
        self.setFixedSize(820, 320)
        self.scene = QGraphicsScene()
        self.game_loop = False
        self.scoreboard = None
        self.hot_seat = 0
        self.config = 0
        self.against_ai = 0
        self.game = snake_map(width, height)
        self.multi_info = []
        self.hex = []
        self.grahpicsitem = []
        self.end_connection = False
        self.guicomponents()

    # key listener for a gameplay that is not provided by tcp
    def keyPressEvent(self, event: PySide2.QtGui.QKeyEvent):
        if self.game_loop:
            if self.against_ai is 0:
                if event.text() in p1_controls:
                    p1_keys.append(event.text())
                if event.text() in p2_controls:
                    p2_keys.append(event.text())
            else:
                if event.text() in p1_controls:
                    p1_keys.append(event.text())

    # main window graphic layout
    def guicomponents(self):
        button_exit = QPushButton("Exit", self)
        button_start = QPushButton("1 player", self)
        button_hot_seat = QPushButton("2 players", self)
        button_multi = QPushButton("Multiplayer", self)
        button_replay = QPushButton("Replay", self)
        button_ai = QPushButton("Against bot", self)
        self.connection_info = QLabel(self)
        self.controls_info = QLabel(self)
        self.scoreboard = QLabel(self)
        self.config_info = QLabel(self)
        self.config_info.setText("")
        self.scoreboard.setText("")
        self.config_info.setFont(PySide2.QtGui.QFont("Courier", 9))
        self.scoreboard.setFont(PySide2.QtGui.QFont("Courier", 10))
        self.scoreboard.setGeometry(QRect(10, 225, 500, 30))
        self.config_info.setGeometry(QRect(10, 225, 790, 30))
        button_start.setGeometry(QRect(10, 250, 100, 30))
        button_exit.setGeometry(QRect(510, 250, 100, 30))
        button_hot_seat.setGeometry(QRect(110, 250, 100, 30))
        button_multi.setGeometry(QRect(210, 250, 100, 30))
        button_replay.setGeometry(QRect(410, 250, 100, 30))
        button_ai.setGeometry(QRect(310, 250, 100, 30))
        self.connection_info.setGeometry(10, 280, 200, 30)
        self.controls_info.setGeometry(220, 280, 200, 30)
        button_hot_seat.clicked.connect(self.prepare_hot_seat)
        button_exit.clicked.connect(exit_app)
        button_start.clicked.connect(self.prepare_single)
        button_multi.clicked.connect(self.prepare_multi)
        button_replay.clicked.connect(self.prepare_replay)
        button_ai.clicked.connect(self.prepare_ai)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(10, 10, 10 * (width + 2), 10 * (height + 2))
        self.scene.setBackgroundBrush(QBrush(QColor(0, 120, 0, 255)))
        self.grass = QPixmap(":/map/grass.png").scaled(20,20)
        self.snake = QPixmap(":/map/orange.png").scaled(20,20)
        self.black = QPixmap(":/map/black.png").scaled(20,20)
        self.apple = QPixmap(":/map/apple.png").scaled(20,20)
        self.white = QPixmap(":/map/white.png").scaled(20,20)
        self.clear_map()

    # load configuration from h5 file and map history from xml file
    def prepare_replay(self):
        try:
            self.scoreboard.setText("")
            with open("config.json", "r") as f:
                self.config = json.load(f)
            output = []
            for k in self.config:
                output.append([k, self.config[k]])
            output = [item for sublist in output for item in sublist]
            self.config_info.setText("".join(output))
            tree = ET.parse("replay.xml")
            root = tree.getroot()
            game_history = []
            rounds = []
            for turn in root:
                for cells in turn:
                    for row in cells:
                        if cells.attrib["indexes"] == "19" and row.attrib["indexes"] == "77":
                            game_history.append(row.text)
                            copy_history = deepcopy(game_history)
                            rounds.append(copy_history)
                            game_history.clear()
                        else:
                            game_history.append(row.text)
            for round in rounds:
                round = np.reshape(round, (20, 78))
                self.game.map = round
                Snake.get_hex(self.hex, self.game)
                self.initialize_map()
                self.update_map()
                myApp.processEvents()
                time.sleep(0.5)
        except:
            self.config_info.setText("Failed to load a replay!")

    # key listener for multiplayer
    def send_key(self, number, socket):
        self.game_loop = True
        while True:
            time.sleep(0.3)
            if number == "0" and len(p1_keys) > 0:
                try:
                    socket.send(bytes(p1_keys[-1], "utf-8"))
                except:
                    break
            elif number == "1" and len(p2_keys) > 0:
                try:
                    socket.send(bytes(p2_keys[-1], "utf-8"))
                except:
                    break
            if self.end_connection:
                break

    # receive map configuration from the server
    def prepare_multi(self):
        self.end_connection = False
        root = ET.Element("game")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 1235))
        self.connection_info.setText("Connected to server!")

        msg = s.recv(1024).decode("utf-8")
        init_msg = msg.split()
        score_1, score_2 = 0, 0

        if init_msg[0] == "Start":
            if init_msg[1] == "0":
                self.controls_info.setText("Controls Q, A, Z, E, D, C")
            elif init_msg[1] == "1":
                self.controls_info.setText("Controls T, G, B, U, J, M")
            Thread(target=self.send_key, args=(init_msg[-1], s)).start()
            end = False
            frames = 0

            while end is False:
                myApp.processEvents()
                msg = s.recv(4096)
                msg = pickle.loads(msg)

                if msg[0] == 'end':
                    end = True
                    self.config = {"mode-" : "Multiplayer", " Client 1 -" : str(msg[1]), " Client 2 -" : str(msg[-1]),
                                   " P1 points-": str(score_1), " P2 points-": str(score_2)}
                    with open("config.json", "w") as f:
                        json.dump(self.config, f)
                    continue

                self.game.map = msg[0]
                doc = ET.SubElement(root, "turn", name=str(frames))
                for i in range(height):
                    row = ET.SubElement(doc, "cell", indexes=str(i))
                    for j in range(width):
                        ET.SubElement(row, "row", indexes=str(j)).text = self.game.map[i][j]

                if len(msg) == 3:
                    score_1, score_2 = msg[1], msg[2]

                if msg[0] != "end":
                    if init_msg[1] == "0":
                        self.scoreboard.setText("Your score - " + str(msg[1]) + " | " + "Enemy - " + str(msg[2]))
                    if init_msg[1] == "1":
                        self.scoreboard.setText("Your score - " + str(msg[2]) + " | " + "Enemy - " + str(msg[1]))

                if frames == 0:
                    Snake.get_hex(self.hex, self.game)
                    self.initialize_map()

                self.update_map()
                myApp.processEvents()
                frames = frames + 1
                time.sleep(0.25)

            if init_msg[1] == "0":
                if score_1 > score_2:
                    self.scoreboard.setText("You won!")
                elif score_2 > score_1:
                    self.scoreboard.setText("Enemy won!")
                else:
                    self.scoreboard.setText("Draw!")

            if init_msg[1] == "1":
                if score_1 < score_2:
                    self.scoreboard.setText("You won!")
                elif score_2 < score_1:
                    self.scoreboard.setText("Enemy won!")
                else:
                    self.scoreboard.setText("Draw!")

        self.connection_info.setText("Disconnected!")
        tree = ET.ElementTree(root)
        tree.write("replay.xml")
        self.end_connection = True

    def prepare_hot_seat(self):
        self.hot_seat = 1
        self.against_ai = 0
        self.clear_map()
        self.start_game()

    def prepare_single(self):
        self.hot_seat = 0
        self.against_ai = 0
        self.clear_map()
        self.start_game()

    def prepare_ai(self):
        self.against_ai = 1
        self.hot_seat = 0
        self.clear_map()
        self.start_game()

    def clear_map(self):
        self.game.init_map()
        Snake.get_hex(self.hex, self.game)
        self.initialize_map()

    def initialize_map(self):
        self.grahpicsitem = []
        self.scene.clear()
        for i in self.hex:
            if self.game.map[i[0]][i[1]] == " ":
                cell = QGraphicsPixmapItem(self.grass)
                cell.setPos(QPointF(i[1]*10, i[0]*10))
                self.grahpicsitem.append(cell)
                self.scene.addItem(cell)
            elif self.game.map[i[0]][i[1]] == "#":
                cell = QGraphicsPixmapItem(self.black)
                cell.setPos(QPointF(i[1]*10, i[0]*10))
                self.grahpicsitem.append(cell)
                self.scene.addItem(cell)
            elif self.game.map[i[0]][i[1]] == "+":
                cell = QGraphicsPixmapItem(self.white)
                cell.setPos(QPointF(i[1]*10, i[0]*10))
                self.grahpicsitem.append(cell)
                self.scene.addItem(cell)
            if self.game.map[i[0]][i[1]] == "@":
                cell = QGraphicsPixmapItem(self.apple)
                cell.setPos(QPointF(i[1]*10, i[0]*10))
                self.grahpicsitem.append(cell)
                self.scene.addItem(cell)

    def update_map(self):
        for i in range(len(self.hex)):
            if self.game.map[self.hex[i][0]][self.hex[i][1]] == " ":
                self.grahpicsitem[i].setPixmap(self.grass)
            elif self.game.map[self.hex[i][0]][self.hex[i][1]] == "#":
                self.grahpicsitem[i].setPixmap(self.black)
            elif self.game.map[self.hex[i][0]][self.hex[i][1]] == "@":
                self.grahpicsitem[i].setPixmap(self.apple)
            elif self.game.map[self.hex[i][0]][self.hex[i][1]] == "+":
                self.grahpicsitem[i].setPixmap(self.white)

    def start_game(self):
        self.config_info.setText("")
        self.game_loop, spawn_fruit = False, False

        if self.game_loop is not True:
            p1_keys.clear(), p2_keys.clear()

        root = ET.Element("game")
        spawn_animal1, spawn_animal2, self.game_loop = False, False, True
        p1_can_play, p2_can_play = True, True
        animal1, animal2 = [], []
        points1, points2 = 0, 0

        # find free space on the map and spawn snake (or snakes)
        if (self.hot_seat and self.against_ai is 0) or (self.hot_seat is 0 and self.against_ai):
            self.scoreboard.setText("1.P1 points - " + str(points1) + " | 2.P2 points - " + str(points2))
            while (spawn_animal1 is False) and (spawn_animal2 is False):
                if not spawn_animal1:
                    x = np.random.randint(0, len(self.hex))
                    spawn_animal1, _ = Snake.check_space(self.game.map, self.hex[x], 1, [0, 0, "#", "+"], 0)
                if not spawn_animal2:
                    y = np.random.randint(0, len(self.hex))
                    spawn_animal2, _ = Snake.check_space(self.game.map, self.hex[y], 1, [0, 0, "#", "+"], 0)
            animal1.insert(0, snake(self.hex[x], self.game.map, "#"))
            animal2.insert(0, snake(self.hex[y], self.game.map, "+"))
        elif self.hot_seat is 0 and self.against_ai is 0:
            self.scoreboard.setText("Points - " + str(points1))
            while not spawn_animal1:
                x = np.random.randint(0, len(self.hex))
                spawn_animal1, _ = Snake.check_space(self.game.map, self.hex[x], 1, [0, 0, "#"], 0)
            animal1.insert(0, snake(self.hex[x], self.game.map, "#"))

        #main game loop
        index = 0
        while self.game_loop:

            # save actual map to xml file
            doc = ET.SubElement(root, "turn", name=str(index))
            for i in range(height):
                row = ET.SubElement(doc, "cell", indexes=str(i))
                for j in range(width):
                    ET.SubElement(row, "row", indexes=str(j)).text = self.game.map[i][j]

            # spawn fruit on the map
            if not spawn_fruit:
                while not spawn_fruit:
                    x = np.random.randint(0, len(self.hex))
                    spawn_fruit, _ = Snake.check_space(self.game.map, self.hex[x], 1, [0, 0, "@"], 0)

            fruit_on_map = fruit(self.hex[x], self.game.map, "@")

            spawn_fruit, points1, points2, p1_can_play, p2_can_play, self.game_loop = \
                Snake.move_anim(p1_can_play, p2_can_play, spawn_fruit, animal1, animal2, points1, points2, fruit_on_map,
                                p1_keys, p2_keys, self.hot_seat, self.against_ai, self.game, self.hex, self.scoreboard,
                                self.game_loop)

            self.update_map()
            index = index + 1
            myApp.processEvents()
            time.sleep(0.5)

        # prepare configuration and map history
        if self.hot_seat is 0 and self.against_ai is 0:
            self.config = {"mode-" : "Singleplayer", " points-" : str(points1)}
        elif self.hot_seat and self.against_ai is 0:
            self.config = {"mode-" : "Hotseat", " P1 points-" : str(points1), " P2 points-" : str(points2)}
        elif self.hot_seat is 0 and self.against_ai:
            self.config = {"mode-": "Against Bot", " P1 points-": str(points1), " P2 points-": str(points2)}
        with open("config.json", "w") as f:
            json.dump(self.config, f)

        tree = ET.ElementTree(root)
        tree.write("replay.xml")

        if (self.hot_seat and self.against_ai is 0) or (self.hot_seat is 0 and self.against_ai):
            if points1 == points2:
                self.scoreboard.setText("It's draw! 1.P1 score - " + str(points1) + " | 2.P2 score - " + str(points2))
            elif points1 > points2:
                self.scoreboard.setText("P1 won! 1.P1 score - " + str(points1) + " | 2.P2 score - " + str(points2))
            else:
                self.scoreboard.setText("P2 won! 1.P1 score - " + str(points1) + " | 2.P2 score - " + str(points2))
        else:
            self.scoreboard.setText("You lost! Your score - " + str(points1))

myApp = QApplication(sys.argv)
window = window()
window.show()
myApp.exec_()
sys.exit(0)
