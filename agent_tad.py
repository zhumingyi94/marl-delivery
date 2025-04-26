import json

import numpy as np

class Agents:

    def __init__(self, path):
        """
            TODO:
        """
        self.agents = []
        self.n_robots = 0
        self.state = None


        self.board_path = self.get_path(path)
        self.map = []

    def init_agents(self, state):
        self.state = state
        self.n_robots = len(state['robots'])
        self.map = state['map']

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

    def get_action(self, start, target):
        return self.board_path[(start, target)]

    def get_actions(self, state):
        """
            TODO:
        """
        list_actions = ['S', 'L', 'R', 'U', 'D']
        actions = []
        for i in range(self.n_robots):
            move = np.random.choice(list_actions)
            pkg_act = np.random.randint(0, 3)

            pos_robot_i, pos_robot_j, carrying = state['robots'][i]
            pos_robot = (pos_robot_i, pos_robot_j)

            if carrying != 0:
                target_package = (1, 1)
                for package in state['packages']:
                    if package[0] == carrying:
                        target_package = (package[3], package[4])
                move = self.get_action(pos_robot, target_package)[0]
                if len(self.get_action(pos_robot, target_package)) != 1:
                    pkg_act = 0
                else:
                    pkg_act = 2
            else:
                start_package = (1, 1)
                target_package = (1, 1)
                len_min_path = 10000
                carry = 0
                for package in state['packages']:
                    if package[0] == carrying:
                        start_package = (package[1], package[2])
                        target_package = (package[3], package[4])
                        len_path = len(self.get_action(pos_robot, start_package)) + len(self.get_action(pos_robot, start_package))
                        if len_path < len_min_path:
                            len_min_path = len_path
                            carry = package[0]
                for package in state['packages']:
                    if package[0] == carry:
                        target_package = (package[1], package[2])
                move = self.get_action(pos_robot, target_package)[0]
                if len(self.get_action(pos_robot, target_package)) != 1:
                    pkg_act = 0
                else:
                    pkg_act = 1
            actions.append((str(move), str(pkg_act)))
        return actions

# if __name__ == "__main__":
#     agent = Agents("map_path/map5.txt")
#     start = (1, 1)
#     target = (10, 3)
#     print(len(agent.board_path))
#     print(agent.get_action(start, target))
    # print(agent.board_path)