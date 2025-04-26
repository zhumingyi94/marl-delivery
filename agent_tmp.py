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
        self.map = None
        self.time_step = 0


        # THEM
        self.robot_assignments = {}
        self.robot_paths = {}
        self.pending_packages = {}
        # Luu y: moi goi hang chi xuat hien dung 1 lan => ID xuat hien dung 1 lan => khong can phai luu them finished_pkgs ma chi can luu pending_packages roi remove ID da hoan thanh 

    def init_agents(self, state):
        """
            TODO:
        """
        self.state = state
        self.n_robots = len(state['robots'])
        self.map = state['map']
        self.time_step = state['time_step']

        # THEM
        self.robot_assignments = {i: 0 for i in range(self.n_robots)}
        self.robot_paths = {i: [] for i in range(self.n_robots)}
        self.pending_packages = {}
        self.update_pending_packages(state)

    ########-----UTIL FUNCTIONS------#######
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
            print(current_pos, next_pos)
            return 'D'
        elif next_pos[1] < current_pos[1]:
            return 'L'
        elif next_pos[1] > current_pos[1]:
            return 'R'
        else:
            return 'S'
        
    def update_pending_packages(self,state):
        for pkg in state.get('packages', []):
            pkg_id, start_r, start_c, target_r, target_c, start_time, deadline = pkg
            # print(start_r, start_c, target_r, target_c)
            if (start_r != target_r) or (target_r != target_c):
                    start = (start_r-1, start_c-1)
                    target = (target_r-1, target_c-1)
                    self.pending_packages[pkg_id] = (start, target, deadline)

    def get_package_action(self, robot_idx, robot_pos, carrying):
        if carrying in self.pending_packages.keys():
            start, target, deadline = self.pending_packages[carrying]
            if target == robot_pos:
                self.robot_assignments[robot_idx] = 0
                self.robot_paths[robot_idx] = []
                del self.pending_packages[carrying]
                return '2'
            
        pkg_id = self.robot_assignments[robot_idx]
        if pkg_id != 0 and pkg_id in self.pending_packages.keys():
            start, target, deadline = self.pending_packages[pkg_id]
            if start == robot_pos:
                self.robot_paths[robot_idx] = self.find_path(start, target)
                return '1'
        return '0'
    
    #######----ALGORITHM LOGIC FUNCTIONS----#######
    def assign_packages(self):
        # step 1: find unassigned packages
        unassigned_packages = []
        for pkg_id, (start, target, deadline) in self.pending_packages.items():
            if pkg_id not in self.robot_assignments.values():
                unassigned_packages.append((pkg_id, start, target, deadline))

        # step 2: iterate through pkgs to find nearest idle robots
        # step 2.1: find free robots
        idle_robots = {}
        for i, robot in enumerate(self.state['robots']):
            if robot[2] != 0 and self.robot_assignments[i] != 0:
                continue
            idle_robots[i] = robot

        unassigned_packages.sort(key=lambda x: x[3])

        # step 2.2: find robot for each pkg
        for pkg_id, pkg_start, pkg_target, deadline in unassigned_packages: 
            closest_robot_idx = -1
            min_dist = float('inf')
            for (robot_idx, robot) in idle_robots.items():
                r, c, carrying = robot
                robot_pos = (r-1, c-1) 
                path = self.find_path(robot_pos, pkg_start)
                if path:
                    dist = len(path) - 1
                    if dist < min_dist:
                        min_dist = dist
                        closest_robot_idx = robot_idx

            if closest_robot_idx != -1:
                robot = idle_robots[closest_robot_idx]
                r, c, carrying = robot
                self.robot_assignments[closest_robot_idx] = pkg_id
                self.robot_paths[closest_robot_idx] = self.find_path((r-1,c-1), pkg_start)

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
        self.assign_packages()
        robot_moves = []
        for i in range(self.n_robots): 
            r, c, carrying = state['robots'][i]
            current_pos = (r-1, c-1)  # Convert to 0-indexed
            if self.robot_paths[i]:
                next_pos = self.robot_paths[i][0]
                # print(f"current_pos {current_pos}, next_pos {next_pos} cho robot {i}")
                move = self.get_move_action(current_pos, next_pos)
                if move != 'S':
                    self.robot_paths[i] = self.robot_paths[i][1:]    
            else:
                move = 'S'
            robot_moves.append(move)

        actions = []
        for i in range(self.n_robots):
            r, c, carrying = state['robots'][i]
            robot_pos = (r-1, c-1)
            move = robot_moves[i]
            pkg_act = self.get_package_action(i, robot_pos, carrying)
            actions.append((move, pkg_act))
        return actions