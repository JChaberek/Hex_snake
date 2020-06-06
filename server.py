import socket
import Snake
import threading
import pickle
import numpy as np
import time
from threading import Thread
from socket import  AF_INET, SOCK_STREAM
from Snake import snake_map, snake, fruit

animal1, animal2 = [], []
keys_1, keys_2 = ["."], ["."]
width, height = 78, 20

class Server:
    # server and game settings
    def __init__(self):
        self.clients = []
        self.no_clients = 0
        self.host = "127.0.0.1"
        self.port = 1235
        self.addr = (self.host, self.port)
        self.server = socket.socket(AF_INET, SOCK_STREAM)
        self.server.bind(self.addr)
        self.game_env = None
        self.points1 = 0
        self.points2 = 0
        self.fruit = 0
        self.end_game = False
        self.hex = []
        self.spawn_fruit = False

    # accept connection and start new thread
    def accept_client(self):
        while True:
            client, client_addr = self.server.accept()
            Thread(target=self.client_keyboard, args=(client,client_addr)).start()

    def client_keyboard(self, client, client_addr):
        # if someone joins on the server, prepare game configuration
        if len(self.clients) == 0:
            self.game_env = Snake.snake_map(width, height)
            self.game_env.init_map()
            Snake.get_hex(self.hex, self.game_env)
            spawn_p1, spawn_p2, spawn_f = False, False, False
            while spawn_p1 is not True and spawn_p2 is not True and self.spawn_fruit is not True:

                if not spawn_p1:
                    x = np.random.randint(0, len(self.hex))
                    spawn_p1, _ = Snake.check_space(self.game_env.map, self.hex[x], 1, [0, 0, "#", "+"], 0)
                    if self.hex[x][1] < 4 or self.hex[x][1] > 70:
                        spawn_p1 = False

                if not spawn_p2:
                    y = np.random.randint(0, len(self.hex))
                    spawn_p2, _ = Snake.check_space(self.game_env.map, self.hex[x], 1, [0, 0, "#", "+"], 0)
                    if self.hex[x][1] < 4 or self.hex[x][1] > 70:
                        spawn_p2 = False

                if not self.spawn_fruit:
                    z = np.random.randint(0, len(self.hex))
                    self.spawn_fruit, _ = Snake.check_space(self.game_env.map, self.hex[z], 1, [0, 0, "#", "+"], 0)

            animal1.insert(0, snake(self.hex[x], self.game_env.map, "#"))
            animal2.insert(0, snake(self.hex[y], self.game_env.map, "+"))
            _ = fruit(self.hex[z], self.game_env.map, "@")

        # append client to the list
        self.clients.append([client, client_addr, self.no_clients])
        self.no_clients = self.no_clients + 1

        if len(self.clients) == 2:
            for i in self.clients:
                i[0].send(bytes("Start " + str(i[2]), "utf-8"))
            time.sleep(2)
            Thread(target=self.game_loop).start()

        # receive pressed keys from clients
        while True:
            if self.end_game:
                break
            for i in self.clients:
                msg = i[0].recv(1024).decode("utf-8")
                if i[-1] == 0:
                    keys_1.append(msg[0])
                elif i[-1] == 1:
                    keys_2.append(msg[0])

    # main game loop
    def game_loop(self):
        p1_can_play, p2_can_play = True, True
        client_1 = self.clients[0][1]
        client_2 = self.clients[1][1]
        if len(keys_2) > 0 and len(keys_1) > 0:
            while True:
                time.sleep(0.25)

                # pickle map and send it to the clients
                for i in self.clients:
                    time.sleep(0.25)
                    msg = [self.game_env.map, self.points1, self.points2]
                    i[0].send(pickle.dumps(msg))

                if p1_can_play:
                    p1_can_play, spawn_f1 = Snake.move(self.game_env, animal1, keys_1[-1], self.hex)

                if p2_can_play:
                    p2_can_play, spawn_f2 = Snake.move(self.game_env, animal2, keys_2[-1], self.hex)

                if spawn_f1 is not True:
                    self.points1 = self.points1 + 10
                    self.spawn_fruit = False
                    if self.spawn_fruit is False:
                        while self.spawn_fruit is False:
                            z = np.random.randint(0, len(self.hex))
                            self.spawn_fruit, _ = Snake.check_space(self.game_env.map, self.hex[z], 1, [0, 0, "#", "+"],
                                                                    0)
                    _ = fruit(self.hex[z], self.game_env.map, "@")

                elif spawn_f2 is not True:
                    self.points2 = self.points2 + 10
                    self.spawn_fruit = False
                    if self.spawn_fruit is False:
                        while self.spawn_fruit is False:
                            z = np.random.randint(0, len(self.hex))
                            self.spawn_fruit, _ = Snake.check_space(self.game_env.map, self.hex[z], 1, [0, 0, "#", "+"],
                                                                    0)
                    _ = fruit(self.hex[z], self.game_env.map, "@")

                # if all players cant play, send final message and break connection with clients
                if p1_can_play is False and p2_can_play is False:
                    msg = ["end", str(client_1), str(client_2)]
                    for i in self.clients:
                        i[0].send(pickle.dumps(msg))
                    for i in self.clients:
                        self.clients.remove(i)
                    self.end_game = True
                    if len(self.clients) > 2:
                        break

server = Server()
server.game_env = Snake.snake_map(width, height)
server.game_env.init_map()
server.server.listen(5)
accept_thread = Thread(target=server.accept_client)
accept_thread.start()
accept_thread.join()
server.server.close()
