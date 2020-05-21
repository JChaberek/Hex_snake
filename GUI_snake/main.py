import numpy as np
import sys
import Snake
import time
import PySide2.QtGui
import images
from Snake import snake_map, snake, fruit
from PySide2.QtGui import QPixmap, QBrush, QColor
from PySide2.QtCore import QRect, QPointF
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, \
    QGraphicsScene, QGraphicsView, QGraphicsPixmapItem

p1_controls = ["q", "a", "z", "e", "d", "c"]
p2_controls = ["t", "g", "b", "u", "j", "m"]
width, height = 78, 20
p1_keys, new_list, p2_keys = [], [], []

def exit_app():
    sys.exit(0)

class window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snake")
        self.setGeometry(150, 50, 820, 300)
        self.setFixedSize(820, 300)
        self.scene = QGraphicsScene()
        self.game_loop = False
        self.scoreboard = None
        self.hot_seat = 0
        self.game = snake_map(width, height)
        self.hex = []
        self.grahpicsitem = []
        self.guicomponents()

    def keyPressEvent(self, event: PySide2.QtGui.QKeyEvent):
        if self.game_loop:
            if event.text() in p1_controls:
                p1_keys.append(event.text())
            if event.text() in p2_controls:
                p2_keys.append(event.text())

    def guicomponents(self):
        button_exit = QPushButton("Exit", self)
        button_start = QPushButton("1 player", self)
        button_hot_seat = QPushButton("2 players", self)
        self.scoreboard = QLabel(self)
        self.scoreboard.setText("Points - 0")
        self.scoreboard.setFont(PySide2.QtGui.QFont("Courier", 10))
        self.scoreboard.setGeometry(QRect(500, 250, 500, 30))
        button_start.setGeometry(QRect(10, 250, 100, 30))
        button_exit.setGeometry(QRect(210, 250, 100, 30))
        button_hot_seat.setGeometry(QRect(110, 250, 100, 30))
        button_hot_seat.clicked.connect(self.prepare_hot_seat)
        button_exit.clicked.connect(exit_app)
        button_start.clicked.connect(self.prepare_single)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(10, 10, 10 * (width + 2), 10 * (height + 2))
        self.scene.setBackgroundBrush(QBrush(QColor(0, 120, 0, 255)))
        self.grass = QPixmap(":/map/grass.png").scaled(20,20)
        self.snake = QPixmap(":/map/orange.png").scaled(20,20)
        self.black = QPixmap(":/map/black.png").scaled(20,20)
        self.apple = QPixmap(":/map/apple.png").scaled(20,20)
        self.white = QPixmap(":/map/white.png").scaled(20,20)
        self.clear_map()

    def prepare_hot_seat(self):
        self.hot_seat = 1
        self.clear_map()
        self.start_game()

    def prepare_single(self):
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

    def move_anim(self, p1_can_play, p2_can_play, spawn_fruit, animal1, animal2, points1, points2):
        if self.hot_seat:
            if len(p1_keys) > 0 and len(p2_keys) > 0:
                if p1_can_play:
                    p1_can_play, spawn_fruit1 = Snake.move(self.game, animal1, p1_keys[-1], self.hex)
                if p2_can_play:
                    p2_can_play, spawn_fruit2 = Snake.move(self.game, animal2, p2_keys[-1], self.hex)
                if (p1_can_play or p2_can_play) is not True:
                    self.game_loop = False
                if spawn_fruit1 is not True:
                    points1 += 10
                    spawn_fruit = False
                elif spawn_fruit2 is not True:
                    points2 += 10
                    spawn_fruit = False
                self.scoreboard.setText("1.P1 points - " + str(points1) + " | 2.P2 points - " + str(points2))
        else:
            if len(p1_keys) > 0:
                self.game_loop, spawn_fruit = Snake.move(self.game, animal1, p1_keys[-1], self.hex)
                if spawn_fruit is not True:
                    points1 += 10
                    self.scoreboard.setText("Points - " + str(points1))
        return spawn_fruit, points1, points2

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
        self.game_loop, spawn_fruit = False, False

        if self.game_loop is not True:
            p1_keys.clear(), p2_keys.clear()

        spawn_animal1, spawn_animal2, self.game_loop = False, False, True
        p1_can_play, p2_can_play = True, True
        animal1, animal2 = [], []
        points1, points2 = 0, 0

        if self.hot_seat:
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
        else:
            self.scoreboard.setText("Points - " + str(points1))
            while not spawn_animal1:
                x = np.random.randint(0, len(self.hex))
                spawn_animal1, _ = Snake.check_space(self.game.map, self.hex[x], 1, [0, 0, "#"], 0)
            animal1.insert(0, snake(self.hex[x], self.game.map, "#"))

        while self.game_loop:
            if not spawn_fruit:
                while not spawn_fruit:
                    x = np.random.randint(0, len(self.hex))
                    spawn_fruit, _ = Snake.check_space(self.game.map, self.hex[x], 1, [0, 0, "@"], 0)
            _ = fruit(self.hex[x], self.game.map, "@")
            spawn_fruit, points1, points2 = \
                self.move_anim(p1_can_play, p2_can_play, spawn_fruit, animal1, animal2, points1, points2)
            self.update_map()
            myApp.processEvents()
            time.sleep(0.5)

        if self.hot_seat:
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
