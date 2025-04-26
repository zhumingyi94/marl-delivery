import numpy as np
from collections import deque

class Agents:

    def __init__(self):
        """
            TODO:
        """
        self.agents = []
        self.n_robots = 0
        self.state = None

        # THEM
        self.robot_assignments = {}
        self.robot_paths = {}
        self.pending_packages = {}
        self.time_step = 0
        # Luu y: moi goi hang chi xuat hien dung 1 lan => ID xuat hien dung 1 lan => khong can phai luu them finished_pkgs ma chi can luu pending_packages roi remove ID da hoan thanh 

    def init_agents(self, state):
        """
            TODO:
        """
        self.state = state
        self.n_robots = len(state['robots'])
        self.map = state['map']

    def update_pending_packages(self,state):
        self.time_step = state['time_step']
        for pkg in state.get('package', []):
            pkg_id, start_r, start_c, target_r, target_c, start_time, deadline = pkg
            if start_r != target_r or target_r != target_c:
                if pkg_id not in self.pending_packages.keys():
                    start = (start_r-1, start_c-1)
                    target = (target_r-1, target_c-1)
                    self.pending_packages[pkg_id] = (start, target, deadline)
            elif start_r == target_r and target_r == target_c:
                del self.pending_packages[pkg_id] 
                print(f"LOG AGENT: Package {pkg_id} has been delivered - removing from pending packages")

        for i in range(self.n_robots): 
            _, _, carrying = state['robots'][i]
            if carrying > 0: 
                self.robot_assignments[i] = carrying
    def find_path(self, start, end):
        if start == end:
            return start

        queue = deque([start])
        visited = {start: None}

        while queue:
            current = queue.popleft()
            r,c = current
            if current == end:
                break
            for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < len(self.map) and 0 <= nc < len(self.map[0]) and self.map[nr][nc] == 0 and (nr, nc) not in visited):
                    neighbor = (nr, nc)
                    visited[neighbor] = current
                    queue.append(neighbor)

            if end not in visited:
                return []
            path = []
            current = end
            while current is not None:
                path.append(current)
                current = visited[current]
            return path[::-1]

    def get_move_action(self, current_pos, next_pos):
        if next_pos[0] < current_pos[0]:
            return 'U'
        elif next_pos[0] > current_pos[0]:
            return 'D'
        elif next_pos[1] < current_pos[1]:
            return 'L'
        elif next_pos[1] > current_pos[1]:
            return 'R'
        else:
            return 'S'

    def assign_pkgs(self):
        # step 2: iterate through pkgs to find nearest idle robots
        # step 2.1: find free robots
        idle_robots = []
        for i, robot in enumerate(self.state['robots']):
            if robot[2] != 0 or i in self.robot_assignments.keys():
                continue
            idle_robots.append((i, robot))

        self.pending_packages.sort(key=lambda x: x[3])
        # step 2.2: find robot for each pkgs
        for pkg in self.pending_packages:
            pkg_id = pkg[0] 
            if pkg_id not in self.robot_assignments.values():
                closest_robot_idx = -1
                min_dist = float('inf')
                for idx_robot in idle_robots:
                    path = self.find_path((idx_robot[1], idx_robot[2]), (pkg[1], pkg[2]))
                    if path:
                        dist = len(path) - 1
                        if dist < min_dist:
                            min_dist = dist
                            closest_robot_idx = idx_robot[0]

                if closest_robot_idx != -1:
                    robot_idx, robot_pos = idle_robots.pop(closest_robot_idx)
                    self.robot_assignments[robot_idx] = pkg_id
                    self.robot_paths[robot_idx] = self.find_path((idx_robot[1], idx_robot[2]), (pkg[1], pkg[2]))

    def get_actions(self, state):
        """
            TODO:
        """
        # list_actions = ['S', 'L', 'R', 'U', 'D']
        # actions = []
        # for i in range(self.n_robots):
        #     move = np.random.randint(0, len(list_actions))
        #     pkg_act = np.random.randint(0, 3)
        #     actions.append((list_actions[move], str(pkg_act)))
        self.update_pending_packages(state)
        self.state = state

        return actions