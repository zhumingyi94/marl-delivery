import json
from collections import deque

import numpy as np


def compute_new_position(position, move):
    r, c = position
    if move == 'S':
        return r, c
    elif move == 'L':
        return r, c - 1
    elif move == 'R':
        return r, c + 1
    elif move == 'U':
        return r - 1, c
    elif move == 'D':
        return r + 1, c
    else:
        print("Error move")
        return r, c

# def valid_position()

def conflict_transport(robots, moves):
    if len(robots) != len(moves):
        print("Error transport")




class Agents_TAD:
    def __init__(self):
        self.n_robots = 0
        self.state = None

        # add feature
        self.board_path = {}
        self.map = []
        self.waiting_packages = []
        self.in_transit_packages = []
        self.finished = [] # Does the robot still need to transport
        self.pos_stay = {} # Store the position when it is in the 'stay' state

    def init_agents(self, state):
        self.state = state
        self.n_robots = len(state['robots'])
        self.map = state['map']
        self.board_path = self.get_shortest_path(state['map'])
        self.finished = [False] * len(state['robots'])
        self.robots = [(robot[0] - 1, robot[1] - 1, 0) for robot in state['robots']]
        self.robots_target = ['free'] * self.n_robots

    def get_path(self, path):
        list_path = {}
        with open(path, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()

                obj = json.loads(line)
                start = tuple(obj["start"])
                target = tuple(obj["target"])
                list_path[(start, target)] = obj["path"]
        return list_path

    def get_shortest_path(self, map):
        list_path = {}
        map_position = []
        n, m = len(map), len(map[0])
        directions = [("U", (-1, 0)), ("L", (0, -1)), ("R", (0, 1)), ("D", (1, 0))]

        for i in range(n):
            for j in range(m):
                if map[i][j] == 0:
                    map_position.append((i, j))

        for i in range(len(map_position)):
            dist = [[-1] * m for _ in range(n)]
            str_path = [[""] * m for _ in range(n)]
            queue = deque()

            start_i, start_j = map_position[i]
            queue.append((start_i, start_j))
            dist[start_i][start_j] = 0
            str_path[start_i][start_j] = ""

            while queue:
                x, y = queue.popleft()

                for (direc_move, (di, dj)) in directions:
                    pos_i = x + di
                    pos_j = y + dj
                    if 0 < pos_i < n and 0 < pos_j < m and dist[pos_i][pos_j] == -1 and map[pos_i][pos_j] == 0:
                        dist[pos_i][pos_j] = dist[x][y] + 1
                        str_path[pos_i][pos_j] = str_path[x][y] + direc_move
                        queue.append((pos_i, pos_j))

                        start = (start_i + 1, start_j + 1)
                        target = (pos_i + 1, pos_j + 1)
                        list_path[(start, target)] = str_path[pos_i][pos_j]
        return list_path

    def compute_valid_position(self, map, position, move):
        """
        Computes the intended new position for a robot given its current position and move command.
        """
        r, c = position
        if move == 'S':
            i, j = r, c
        elif move == 'L':
            i, j = r, c - 1
        elif move == 'R':
            i, j = r, c + 1
        elif move == 'U':
            i, j = r - 1, c
        elif move == 'D':
            i, j = r + 1, c
        else:
            i, j = r, c
        if i <= 1 or i >= len(self.map) or j <= 1 or j >= len(self.map[0]):
            return r, c
        if map[i][j] == 1:
            return r, c
        return i, j


    def valid_position(self, map, position):
        i, j = position
        if i <= 0 or i >= len(self.map) or j <= 0 or j >= len(self.map[0]):
            return False
        if map[i][j] == 1:
            return False
        return True

    def differ_connected(self, start, target):
        return (start, target) not in self.board_path


    def get_action(self, start, target):
        if start == target:
            return ""
        return self.board_path[(start, target)]

    def get_actions(self, state):
        print(state)
        list_actions = ['S', 'L', 'R', 'U', 'D']
        actions = []
        packages = state['packages']
        robots = state['robots']
        map = state['map']
        # Add the newly created packages into waiting_packages
        for package in packages:
            self.waiting_packages.append(package)

        for i in range(len(robots)):
            print("robot", i)
            # move = str(np.random.choice(list_actions))
            move = 'S'
            pkg_act = 0

            pos_robot_i, pos_robot_j, carrying = state['robots'][i]
            pos_robot = (pos_robot_i, pos_robot_j)

            if carrying != 0: # If the robot is transporting a package
                if len(self.in_transit_packages) == 0:
                    actions.append((str('S'), str(0)))
                    self.finished[i] = True
                    self.pos_stay[i] = (robots[i][0], robots[i][1])
                    continue

                # print("In_transit", self.in_transit_packages, carrying)
                for package in self.in_transit_packages:
                    if package[0] == carrying:
                        target_package = (package[3], package[4])
                        move_path = self.get_action(pos_robot, target_package)
                        move = 'S' if len(move_path) == 0 else move_path[0]
                        if len(move_path) > 1:
                            pkg_act = 0
                        else:
                            pkg_act = 2
                            self.in_transit_packages.remove(package)
                        break
            else:
                final_package = (1, 1)
                len_min_path = 10000
                if len(self.waiting_packages) == 0:
                    actions.append((str('S'), str(0)))
                    continue
                transited_package = self.waiting_packages[0]
                print("waiting packages", self.waiting_packages)
                for package in self.waiting_packages:
                    start_package = (package[1], package[2])
                    target_package = (package[3], package[4])
                    if self.differ_connected(pos_robot, start_package):
                        continue
                    if self.differ_connected(start_package, target_package):
                        continue
                    start_path = self.get_action(pos_robot, start_package)
                    target_path = self.get_action(start_package, target_package)
                    len_path = len(start_path) + len(target_path)
                    # print(len_path)
                    if len_path < len_min_path:
                        len_min_path = len_path
                        final_package = start_package
                        transited_package = package

                if not self.differ_connected(pos_robot, final_package):
                    move_path = self.get_action(pos_robot, final_package)
                    move = 'S' if len(move_path) == 0 else move_path[0]
                    if len(move_path) <= 1:
                        pkg_act = 1
                        self.in_transit_packages.append(transited_package)
                        self.waiting_packages.remove(transited_package)
                    else:
                        pkg_act = 0
            print("Move", i, move, pkg_act)
            actions.append((str(move), str(pkg_act)))



        # Handle if there is a cycle
        old_move = {}
        for i in range(len(actions)):
            pos_robot = (robots[i][0], robots[i][1])
            old_move[pos_robot] = i
        for i in range(len(actions)):
            pos_robot = (robots[i][0], robots[i][1])
            next_post = self.compute_valid_position(map, pos_robot, actions[i][0])
            if next_post in old_move:
                for move in ['L', 'R', 'U', 'D']:
                    if move != actions[i][0] and actions[i][1] == 0:
                        new_pos = self.compute_valid_position(map, (robots[i][0], robots[i][1]), move)
                        if new_pos not in old_move:
                            print("new pos", i, new_pos)
                            actions[i] = (move, actions[i][1])
                            return actions

        # If a moving robot would collide with a stationary robot, force the stationary robot to move
        # occupied = {}
        # old_pos = {}
        #
        # for i in range(len(actions)):
        #     pos_robot = (robots[i][0], robots[i][1])
        #     old_pos[pos_robot] = i
        #     if actions[i][0] != 'S':
        #         occupied[self.compute_valid_position(map, (robots[i][0], robots[i][1]), actions[i][0])] = i
        # for i in range(len(actions)):
        #     if actions[i][0] == 'S' and actions[i][1] != 1:
        #         for move in ['L', 'R', 'U', 'D']:
        #             new_pos = self.compute_valid_position(map, (robots[i][0], robots[i][1]), move)
        #             if new_pos not in occupied:
        #                 print("new pos", i, new_pos)
        #                 actions[i] = (move, actions[i][1])
        #                 break


        print("N robots = ", len(self.robots))
        print("Actions = ", actions)
        print(self.robots_target)
        return actions

if __name__ == "__main__":
    agent = Agents_TAD()
    print(len(agent.board_path))
    # print(agent.board_path)