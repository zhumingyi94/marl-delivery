import json
from collections import deque

import numpy as np

class Agents_TAD:

    def __init__(self):
        """
            TODO:
        """
        self.agents = []
        self.n_robots = 0
        self.state = None


        self.board_path = {}
        self.map = []
        self.waiting_packages = []
        self.in_transit_packages = []

    def init_agents(self, state):
        self.state = state
        self.n_robots = len(state['robots'])
        self.map = state['map']
        self.board_path = self.get_shortest_path(state['map'])

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

    def get_action(self, start, target):
        if start == target:
            return ""
        return self.board_path[(start, target)]

    def get_actions(self, state):
        """
            TODO:
        """
        print(state)
        list_actions = ['S', 'L', 'R', 'U', 'D']
        actions = []
        packages = state['packages']
        for package in packages:
            self.waiting_packages.append(package)

        for i in range(self.n_robots):
            print("ROBOT", i)
            move = str(np.random.choice(list_actions))
            pkg_act = np.random.randint(0, 3)

            pos_robot_i, pos_robot_j, carrying = state['robots'][i]
            pos_robot = (pos_robot_i, pos_robot_j)

            if carrying != 0:
                target_package = (1, 1)
                if len(self.in_transit_packages) == 0:
                    actions.append((str('S'), str(0)))
                    continue
                print("In_transit", self.in_transit_packages, carrying)
                for package in self.in_transit_packages:
                    if package[0] == carrying:
                        target_package = (package[3], package[4])
                        move = self.get_action(pos_robot, target_package)
                        if move:
                            move = move[0]
                        else:
                            move = 'S'
                        if len(self.get_action(pos_robot, target_package)) != 1:
                            pkg_act = 0
                        else:
                            pkg_act = 2
                            self.in_transit_packages.remove(package)
                            carrying = 0
                            print(22222222222222)
                        break
                print(pos_robot, target_package, carrying)
                print(len(self.get_action(pos_robot, target_package)))
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
                    len_path = len(self.get_action(pos_robot, start_package)) + len(self.get_action(start_package, target_package))
                    print(len_path)
                    if len_path < len_min_path:
                        len_min_path = len_path
                        final_package = start_package
                        transited_package = package

                print(pos_robot, final_package, carrying, 1)
                print(len(self.get_action(pos_robot, final_package)))
                move = self.get_action(pos_robot, final_package)
                if move:
                    move = move[0]
                else:
                    move = 'S'
                if len(self.get_action(pos_robot, final_package)) != 1:
                    pkg_act = 0
                else:
                    pkg_act = 1
                    self.in_transit_packages.append(transited_package)
                    self.waiting_packages.remove(transited_package)

            print(move, pkg_act)
            actions.append((str(move), str(pkg_act)))
        return actions

if __name__ == "__main__":
    agent = Agents_TAD("map_path/map5.txt")
    print(len(agent.board_path))
    # print(agent.board_path)