import random
from collections import deque

def compute_valid_position(map, position, move):
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
    if i <= 1 or i >= len(map) or j <= 1 or j >= len(map[0]):
        return r, c
    if map[i-1][j-1] == 1:
        return r, c
    return i, j

def valid_position(map, position):
    i, j = position
    if i <= 0 or i >= len(map) or j <= 0 or j >= len(map[0]):
        return False
    if map[i-1][j-1] == 1:
        return False
    return True

def find_all_cycle(map, robots, actions):
    visited = {}
    pos = {}
    future_pos = {}
    for i in range(len(robots)):
        pos_robot = (robots[i][0], robots[i][1])
        pos[i] = pos_robot
        visited[pos_robot] = False
        next_post = compute_valid_position(map, pos_robot, actions[i][0])
        future_pos[pos_robot] = next_post

    list_cycles = []
    list_actions = []
    for i in range(len(robots)):
        queue = deque()
        if not visited[pos[i]]:
            queue.append(pos[i])
            visited[pos[i]] = True
        start_pos = None
        history = []
        history.append(pos[i])

        while queue:
            start = queue.popleft()
            target = future_pos[start]
            if target not in visited:
                break

            if not visited[target]:
                queue.append(target)
                visited[target] = True
                history.append(target)
            else:
                if target in history:
                    start_pos = target
                break

        cycle = []
        action =[]
        while start_pos:
            if start_pos in cycle:
                break
            for i in range(len(robots)):
                if start_pos == (robots[i][0], robots[i][1]):
                    action.append(actions[i])
                    break
            cycle.append(start_pos)
            start_pos = future_pos[start_pos]

        if len(cycle) > 0:
            list_cycles.append(cycle)
            list_actions.append(action)
    return list_cycles, list_actions

def get_shortest_path(map):
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
                if 0 < pos_i < n and 0 < pos_j < m and dist[pos_i][pos_j] == -1:
                    if map[pos_i][pos_j] == 0:
                        dist[pos_i][pos_j] = dist[x][y] + 1
                        str_path[pos_i][pos_j] = str_path[x][y] + direc_move
                        queue.append((pos_i, pos_j))

                        start = (start_i + 1, start_j + 1)
                        target = (pos_i + 1, pos_j + 1)
                        list_path[(start, target)] = str_path[pos_i][pos_j]
    return list_path

class AgentsVersion2:
    def __init__(self):
        self.n_robots = 0
        self.state = None

        # add feature
        self.robots = []
        self.packages = []
        self.board_path = {}
        self.map = []

        self.waiting_packages = []
        self.in_transit_packages = []
        self.transited_packages = []
        self.transit_succes = 0


    def init_agents(self, state):
        self.state = state
        self.n_robots = len(state['robots'])
        self.map = state['map']
        self.board_path = get_shortest_path(state['map'])
        self.robots = [(robot[0], robot[1], 0) for robot in state['robots']]

    def compute_valid_position(self, map, position, move):
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
        if map[i-1][j-1] == 1:
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
        actions = []
        packages = state['packages']
        robots = state['robots']
        map = state['map']

        # Add the newly created packages into waiting_packages
        for package in packages:
            self.packages.append(package)
            self.waiting_packages.append(package)
        for i in range(len(robots)):
            self.robots[i] = robots[i]

        for i in range(len(robots)):
            # move = str(np.random.choice(list_actions))
            move = 'S'
            pkg_act = 0

            pos_robot_i, pos_robot_j, carrying = robots[i]
            pos_robot = (pos_robot_i, pos_robot_j)
            print(f"Robot {i} dang o vi tri {pos_robot}")

            if carrying != 0: # If the robot is transporting a package
                print(f"Package set in transit {self.in_transit_packages}")
                print(f"Robot {i} o vi tri {pos_robot} va dang cam package_id {carrying}")
                for package in self.in_transit_packages.copy():
                    if package[0] == carrying:
                        target_package = (package[3], package[4])
                        print(f"Diem tra goi hang {package[0]} la", target_package)
                        # As only deliverable packages are selected during traversal, paths that do not exist are ignored
                        move_path = self.get_action(pos_robot, target_package)
                        move = 'S' if len(move_path) == 0 else move_path[0]
                        if len(move_path) > 1:
                            pkg_act = 0
                        else:
                            pkg_act = 2
                            self.transited_packages.append(package)
                            self.transit_succes += 1
                            self.in_transit_packages.remove(package)
                        break
            else: # The robot is on its way to find the package with the shortest delivery pat
                final_package = (1, 1)
                len_min_path = 10000
                if len(self.waiting_packages) == 0:
                    actions.append((str('S'), str(0)))
                    continue
                print(f"Package set in waiting {self.waiting_packages}")

                pos_pack = (1, 1)

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
                    # len_path = len(start_path)

                    if len_path <= len_min_path:
                        len_min_path = len_path
                        pos_pack = start_package
                    # elif len_path == len_min_path:
                    #     package_id = min(package_id, package[0])

                if pos_pack == (1, 1):
                    actions.append((str('S'), str(0)))
                    continue

                package_id = 10000
                for package in self.waiting_packages.copy():
                    if pos_pack == (package[1], package[2]):
                        package_id = min(package_id, package[0])

                for package in self.waiting_packages.copy():
                    if package[0] == package_id:
                        print(f"Robot {i} dang tren duong di nhan goi hang {package}")
                        pos_package = (package[1], package[2])
                        move_path = self.get_action(pos_robot, pos_package)
                        move = 'S' if len(move_path) == 0 else move_path[0]
                        if len(move_path) <= 1:
                            pkg_act = 1
                            self.in_transit_packages.append(package)
                            self.waiting_packages.remove(package)
                        else:
                            pkg_act = 0
                        break

            print("Move", i, move, pkg_act)
            actions.append((str(move), str(pkg_act)))

        # find all cycle in move actions
        # print(len(robots), len(actions), robots, actions)
        cycles_list, actions_list = find_all_cycle(map, robots, actions)
        old_pos = {}
        new_pos = {}
        for i in range(len(actions)):
            pos_robot = (robots[i][0], robots[i][1])
            old_pos[pos_robot] = i
            new_pos[self.compute_valid_position(map, pos_robot, actions[i][0])] = i

        for (element_robot, element_action) in zip(cycles_list, actions_list):
            print(len(element_robot), element_robot, element_action)
            # Handle if there is multi cycle
            for i in range(len(element_action)):
                pos_robot = (element_robot[i][0], element_robot[i][1])
                next_pos = self.compute_valid_position(map, pos_robot, element_action[i][0])
                if pos_robot in new_pos and next_pos in old_pos and pos_robot != next_pos:
                    moves = ['L', 'R', 'U', 'D']
                    moves.remove(element_action[i][0])
                    # random.shuffle(moves)
                    # for move in ['L', 'R', 'U', 'D']:
                    for move in moves:
                        # print(i, move, actions[i][0], actions[i][1], type( actions[i][0]), type( actions[i][1]))
                        # if move != element_action[i][0] and int(element_action[i][1]) == 0:
                        if move != element_action[i][0]:
                            new_pos_robot = self.compute_valid_position(map, pos_robot, move)
                            if new_pos_robot not in old_pos and new_pos_robot not in new_pos and valid_position(map, new_pos_robot):
                                print("new pos", 1, i, new_pos_robot)
                                new_pos[new_pos_robot] = i
                                element_action[i] = (move, element_action[i][1])
                                # return actions
                for j in range(len(robots)):
                    if pos_robot == (robots[j][0], robots[j][1]):
                        actions[j] = element_action[i]

        # If a moving robot would collide with a stationary robot, force the stationary robot to move
        for i in range(len(actions)):
            pos_robot = (robots[i][0], robots[i][1])
            if actions[i][0] == 'S' and actions[i][1] != '1':
                for move in ['L', 'R', 'U', 'D']:
                    new_pos_robot = self.compute_valid_position(map, pos_robot, move)
                    # if new_pos not in occupied and valid_position(map, new_pos):
                    if new_pos_robot not in old_pos and new_pos_robot not in new_pos and pos_robot in new_pos and valid_position(map, new_pos_robot):
                        actions[i] = (move, actions[i][1])
                        new_pos[new_pos_robot] = i
                        # break
        # cycle_list, action_list = find_all_cycle(map, robots, actions)
        # print(len(cycle_list))
        # print(cycle_list, action_list)


        print("N robots = ", len(self.robots))
        print("Actions = ", actions)
        return actions

if __name__ == "__main__":
    agent = AgentsVersion2()
    print(len(agent.board_path))