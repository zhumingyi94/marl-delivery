import numpy as np
from collections import deque

class Agents:
    def __init__(self):
        self.n_robots = 0
        self.state = None
        self.map = None
        self.robot_assignments = {}  # Maps robot index to assigned package id
        self.robot_paths = {}        # Maps robot index to planned path
        self.pending_packages = {} # Maps package_id to (start, target, deadline)
        self.time_step = 0

    def init_agents(self, state):
        self.state = state
        self.n_robots = len(state['robots'])
        self.map = state['map']
        self.time_step = state['time_step']
        self.robot_assignments = {i: None for i in range(self.n_robots)}
        self.robot_paths = {i: [] for i in range(self.n_robots)}
        self.pending_packages = {}
        self._update_pending_packages(state)

    ############---UTIL FUNCTIONS---###############
    def _update_pending_packages(self, state): 
        self.time_step = state['time_step']

        for pkg in state.get('packages', []): # check xem co nhung package nao moi
            pkg_id, start_r, start_c, target_r, target_c, start_time, deadline = pkg
            if start_r != target_r or target_r != target_c: 
                if pkg_id not in self.pending_packages:
                    start = (start_r-1, start_c-1)
                    target = (target_r-1, target_c-1)
                    self.pending_packages[pkg_id] = (start, target, deadline)

        for i in range(self.n_robots): 
            _, _, carrying = state['robots'][i]
            if carrying > 0: 
                self.robot_assignments[i] = carrying
            # elif carrying == 0 and self.robot_assignments[i] is not None:
            # # Robot was carrying a package but now it's not - package was delivered
            #     delivered_pkg_id = self.robot_assignments[i]
            #     if delivered_pkg_id in self.pending_packages:
            #         print(f"LOG: {self.pending_packages[delivered_pkg_id]}")
            #         del self.pending_packages[delivered_pkg_id]
            #     self.robot_assignments[i] = None

    # Find shortest path between two points using BFS.
    def _find_path(self, start, end):
        if start == end:
            return [start]
        queue = deque([start])
        visited = {start: None}
        
        while queue:
            current = queue.popleft()
            r, c = current
            if current == end:
                break
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
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
        print(f"LOG: path from {start} to {end}", path[::-1])
        return path[::-1] # Reverse the path to get from start to end
    
    def _get_move_action(self, current_pos, next_pos):
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
        
    def _get_package_action(self, robot_idx, robot_pos, carrying):
        # TH1: Robot is carrying a package
        if carrying > 0:
            # Tìm đích đến của package này
            for pkg_id, (_, target, _) in self.pending_packages.items():
                if pkg_id == carrying:
                    # Nếu robot đã ở đích của package này thì thả 
                    if target == robot_pos:
                        print("I AM DONE")
                        self.robot_assignments[robot_idx] = None
                        self.robot_paths[robot_idx] = []
                        return '2'  # drop
                    break
            return '0'  # không thì tiếp tục cầm
        
        # TH2: Robot not carrying a package
        pkg_id = self.robot_assignments.get(robot_idx)
        if pkg_id is not None and pkg_id in self.pending_packages:
            start, target, _ = self.pending_packages[pkg_id]
            # If at package location, pick it up
            if start == robot_pos:
                # Update path to target
                self.robot_paths[robot_idx] = self._find_path(start, target)
                return '1'  # pickup
        
        return '0'  # do nothing
        
    ############---ALGORITHM LOGIC FUNCTIONS---###############

    # ASSIGN & FIND PATHS
    def _assign_packages(self): 
        # 1. Find unassigned_packages
        unassigned_packages = []
        for pkg_id, (start, target, deadline) in self.pending_packages.items():
            if pkg_id not in self.robot_assignments.values():
                unassigned_packages.append((pkg_id, start, target, deadline))
        # Sort packages by deadline: 0 - pkg_id, 1 - start, 2 - target, 3 - deadline
        unassigned_packages.sort(key=lambda x: x[3])

        # 2. Find idle robots
        idle_robots = []
        for i in range(self.n_robots):
            _, _, carrying = self.state['robots'][i]
            # len(self.robot_paths[i]) == 0: The robot doesn't have a planned path (it's not currently moving to a destination)
            if carrying == 0 and self.robot_assignments[i] is None and len(self.robot_paths[i]) == 0:
                r, c, _ = self.state['robots'][i]
                robot_pos = (r-1, c-1)  # Convert to 0-indexed
                idle_robots.append((i, robot_pos))
                # print(f"LOG: Tim duoc idle robots tai thoi diem {self.time_step}")
        
        # 3. Assign packages to closest idle robots
        for pkg_id, pkg_start, pkg_target, deadline in unassigned_packages: 
            if not idle_robots:
                break
            closest_robot_idx = -1 # Find closest idle robot to this package
            min_dist = float('inf')
            print(f"LOG: Tim robot de gan cho goi hang o vi tri {pkg_start[0], pkg_start[1]}")
            for idx, (robot_idx, robot_pos) in enumerate(idle_robots):
                path = self._find_path(robot_pos, pkg_start)
                if path:
                    dist = len(path) - 1
                    if dist < min_dist:
                        min_dist = dist
                        closest_robot_idx = idx

            
            if closest_robot_idx != -1:
                robot_idx, robot_pos = idle_robots.pop(closest_robot_idx)
                self.robot_assignments[robot_idx] = pkg_id
                # print(f"LOG: Gan goi hang o vi tri {pkg_start[0] + 1, pkg_start[1] + 1} cho robot {robot_pos[0] + 1, robot_pos[1] + 1}")
                self.robot_paths[robot_idx] = self._find_path(robot_pos, pkg_start)

    def get_actions(self, state):
        self.state = state
        # Bước 1: cập nhật trạng thái gói hàng
        self._update_pending_packages(state) 
        # Bước 2: gán gói hàng nào do con robot nào
        self._assign_packages() 
        robot_moves = [] 
        for i in range(self.n_robots):
            r, c, carrying = state['robots'][i]
            current_pos = (r-1, c-1)  # Convert to 0-indexed
            if self.robot_paths[i]:
                next_pos = self.robot_paths[i][0]
                move = self._get_move_action(current_pos, next_pos)
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
            pkg_act = self._get_package_action(i, robot_pos, carrying)
            actions.append((move, pkg_act))
        # print("LOG: Actions cua robot sau khi chay ham get_actions", actions)
        return actions
