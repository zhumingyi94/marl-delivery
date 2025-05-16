import heapq
import random
import numpy as np
from utils import (manhattan_distance, euclidean_distance, diagonal_distance)


PICKUP = '1'    # Nhặt gói hàng
DELIVER = '2'   # Thả gói hàng
WAIT = '0'      # Chờ/đứng yên

class AStarBase:
    """
    Agent sử dụng thuật toán A* để tìm đường đi
    """
    def get_movement_direction(self, current_pos, next_pos):
        """
        Trả về hướng di chuyển từ current_pos đến next_pos
        Args:
            current_pos: tuple(x1, y1)
            next_pos: tuple(x2, y2)
        Returns:
            str: Hướng di chuyển ('U', 'D', 'L', 'R', 'S')
        """
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]

        if dx == 0 and dy == 0:
            return 'S'  # Stay
        elif dx == 1:
            return 'D'  # Down
        elif dx == -1:
            return 'U'  # Up
        elif dy == 1:
            return 'R'  # Right
        else:  # dy == -1
            return 'L'  # Left

    def get_next_pos(self, start_pos, target_pos):
        """
        Tìm vị trí tiếp theo để di chuyển từ start_pos đến target_pos
        Args:
            start_pos: tuple(x1, y1)
            target_pos: tuple(x2, y2)
        Returns:
            tuple: Vị trí tiếp theo cần di chuyển đến
        """
        # Kiểm tra cache
        path_key = (start_pos, target_pos)
        if path_key in self.path_cache:
            path = self.path_cache[path_key]
            if len(path) > 1:
                return path[1]
            return start_pos

        # Tìm đường đi mới
        path = self.a_star_search(start_pos, target_pos)
        if path and len(path) > 1:
            self.path_cache[path_key] = path
            return path[1]
        return start_pos

    def __init__(self):
        """Khởi tạo agent"""
        self.num_robots = 0
        self.grid_map = None
        self.robot_states = []  # [(x, y, carrying_pkg_id), ...]
        self.package_info = {}  # package_id -> (id, start_x, start_y, target_x, target_y, start_time)
        self.waiting_packages = set()
        self.in_transit_packages = set()
        self.delivered_packages = set()
        self.path_cache = {}

    def init_agents(self, state):
        """
        Khởi tạo trạng thái ban đầu cho agent
        Args:
            state: dict, trạng thái môi trường
        """
        self.grid_map = state['map']
        self.num_robots = len(state['robots'])
        self.robot_states = [(r[0]-1, r[1]-1, r[2]) for r in state['robots']]
        
        # Reset trạng thái
        self.package_info.clear()
        self.waiting_packages.clear()
        self.in_transit_packages.clear()
        self.delivered_packages.clear()
        self.path_cache.clear()
        
        # Khởi tạo thông tin gói hàng
        for pkg in state['packages']:
            pkg_id = pkg[0]
            self.package_info[pkg_id] = (pkg_id, pkg[1]-1, pkg[2]-1, pkg[3]-1, pkg[4]-1, pkg[5])
            if pkg[5] <= state['time_step']:
                self.waiting_packages.add(pkg_id)

    def a_star_search(self, start_pos, goal_pos, heuristic_type='manhattan'):
        """
        Thuật toán A* tìm đường đi từ điểm bắt đầu đến điểm đích
        Args:
            start_pos: tuple(x1, y1)
            goal_pos: tuple(x2, y2)
            heuristic_type: str, loại heuristic ('manhattan', 'euclidean', 'diagonal')
        Returns:
            list: Danh sách các điểm trên đường đi
        """
        # Kiểm tra cache
        path_key = (start_pos, goal_pos)
        if path_key in self.path_cache:
            return self.path_cache[path_key]

        # Chọn hàm heuristic
        heuristic_func = {
            'manhattan': manhattan_distance,
            'euclidean': euclidean_distance,
            'diagonal': diagonal_distance
        }.get(heuristic_type, manhattan_distance)

        # Khởi tạo open set và closed set
        open_set = [(0 + heuristic_func(start_pos, goal_pos), 0, start_pos, [])]
        closed_set = set()

        # Các hướng di chuyển (8 hướng)
        directions = [(0,1), (1,0), (0,-1), (-1,0), 
                     (1,1), (1,-1), (-1,1), (-1,-1)]

        while open_set:
            f_score, g_score, current_pos, path = heapq.heappop(open_set)
            
            if current_pos in closed_set:
                continue
            closed_set.add(current_pos)

            if current_pos == goal_pos:
                final_path = path + [current_pos]
                self.path_cache[path_key] = final_path
                return final_path

            # Xét các ô lân cận
            for dx, dy in directions:
                next_x = current_pos[0] + dx
                next_y = current_pos[1] + dy
                next_pos = (next_x, next_y)

                # Kiểm tra điều kiện hợp lệ
                if (next_x < 0 or next_x >= len(self.grid_map) or 
                    next_y < 0 or next_y >= len(self.grid_map[0]) or
                    self.grid_map[next_x][next_y] == 1 or
                    next_pos in closed_set):
                    continue

                # Tính điểm mới
                movement_cost = 1.4 if dx*dy != 0 else 1.0  # Chi phí cao hơn cho di chuyển chéo
                new_g_score = g_score + movement_cost
                new_h_score = heuristic_func(next_pos, goal_pos)
                new_f_score = new_g_score + new_h_score

                heapq.heappush(open_set, (new_f_score, new_g_score, next_pos, path + [current_pos]))

        return []

    def get_actions(self, state):
        """
        Trả về list các action cho các robot
        Args:
            state: dict, trạng thái môi trường
        Returns:
            list: Danh sách các action [(move_action, package_action), ...]
        """
        # Cập nhật trạng thái robot
        self.robot_states = [(r[0]-1, r[1]-1, r[2]) for r in state['robots']]
        
        # Cập nhật gói hàng mới
        for pkg in state['packages']:
            pkg_id = pkg[0]
            if pkg_id not in self.package_info:
                self.package_info[pkg_id] = (pkg_id, pkg[1]-1, pkg[2]-1, pkg[3]-1, pkg[4]-1, pkg[5])
            if (pkg[5] <= state['time_step'] and 
                pkg_id not in self.in_transit_packages and 
                pkg_id not in self.delivered_packages):
                self.waiting_packages.add(pkg_id)

        actions = []
        for robot_idx, robot_state in enumerate(self.robot_states):
            robot_pos = (robot_state[0], robot_state[1])
            carrying_pkg = robot_state[2]

            if carrying_pkg > 0:  # Robot đang mang gói hàng
                pkg_info = self.package_info[carrying_pkg]
                target_pos = (pkg_info[3], pkg_info[4])

                if robot_pos == target_pos:  # Đã đến đích
                    actions.append(('S', DELIVER))
                    self.in_transit_packages.remove(carrying_pkg)
                    self.delivered_packages.add(carrying_pkg)
                else:  # Di chuyển đến đích
                    next_pos = self.get_next_pos(robot_pos, target_pos)
                    move = self.get_movement_direction(robot_pos, next_pos)
                    actions.append((move, WAIT))
            else:  # Robot chưa mang gói hàng
                if self.waiting_packages:  # Còn gói hàng cần nhặt
                    # Tìm gói hàng gần nhất
                    nearest_pkg = None
                    min_distance = float('inf')
                    for pkg_id in self.waiting_packages:
                        pkg_info = self.package_info[pkg_id]
                        pkg_pos = (pkg_info[1], pkg_info[2])
                        distance = manhattan_distance(robot_pos, pkg_pos)
                        if distance < min_distance:
                            min_distance = distance
                            nearest_pkg = pkg_id

                    if nearest_pkg:
                        pkg_info = self.package_info[nearest_pkg]
                        pkg_pos = (pkg_info[1], pkg_info[2])

                        if robot_pos == pkg_pos:  # Đã đến vị trí gói hàng
                            actions.append(('S', PICKUP))
                            self.waiting_packages.remove(nearest_pkg)
                            self.in_transit_packages.add(nearest_pkg)
                        else:  # Di chuyển đến gói hàng
                            next_pos = self.get_next_pos(robot_pos, pkg_pos)
                            move = self.get_movement_direction(robot_pos, next_pos)
                            actions.append((move, WAIT))
                else:  # Không có gói hàng để nhặt
                    actions.append(('S', WAIT))

        return actions 