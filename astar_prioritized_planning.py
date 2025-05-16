import time as timer
from astar_base import AStarBase
import numpy as np
import heapq

class AgentsPrioritizedPlanning(AStarBase):
    """
    Agent sử dụng A* với Prioritized Planning cho bài toán tìm đường cho nhiều robot
    
    Thuật toán Prioritized Planning:
    - Sắp xếp các robot theo thứ tự ưu tiên
    - Tìm đường cho robot có độ ưu tiên cao nhất trước
    - Các robot có độ ưu tiên thấp hơn phải tránh va chạm với các robot có độ ưu tiên cao hơn
    """
    def __init__(self):
        super().__init__()
        self.paths = {}  # Lưu trữ đường đi đã tính toán cho mỗi robot
        self.constraints = []  # Lưu trữ các ràng buộc cho việc tìm đường
        self.heuristics = {}  # Lưu trữ giá trị heuristic cho mỗi vị trí đích
        
    def compute_heuristics(self, target_pos):
        """
        Tính toán heuristic khoảng cách Manhattan đến vị trí đích cho tất cả các ô trên lưới
        
        Args:
            target_pos: Vị trí đích cần tính heuristic
        Returns:
            Dictionary chứa giá trị heuristic từ mỗi ô đến đích
        """
        if target_pos in self.heuristics:
            return self.heuristics[target_pos]
            
        heuristic = {}
        for i in range(len(self.grid_map)):
            for j in range(len(self.grid_map[0])):
                if self.grid_map[i][j] == 0:  # Chỉ tính cho các ô không phải vật cản
                    heuristic[(i, j)] = abs(target_pos[0] - i) + abs(target_pos[1] - j)
                    
        self.heuristics[target_pos] = heuristic
        return heuristic

    def check_constraints(self, pos, next_pos, time_step, agent_id, constraints):
        """
        Kiểm tra xem di chuyển từ pos đến next_pos có hợp lệ dựa trên các ràng buộc hay không
        
        Args:
            pos: Vị trí hiện tại
            next_pos: Vị trí kế tiếp
            time_step: Thời điểm hiện tại
            agent_id: ID của robot
            constraints: Danh sách các ràng buộc
        Returns:
            True nếu di chuyển hợp lệ, False nếu vi phạm ràng buộc
        """
        for constraint in constraints:
            if constraint['agent'] == agent_id and constraint['timestep'] == time_step:
                if len(constraint['loc']) == 1 and constraint['loc'][0] == next_pos:
                    return False  # Vi phạm ràng buộc vị trí (vertex constraint)
                elif len(constraint['loc']) == 2 and constraint['loc'][0] == next_pos and constraint['loc'][1] == pos:
                    return False  # Vi phạm ràng buộc cạnh (edge constraint)
        return True

    def a_star_with_constraints(self, start_pos, goal_pos, agent_id, constraints):
        """
        Thuật toán A* có xét đến các ràng buộc thời gian
        
        Args:
            start_pos: Vị trí bắt đầu
            goal_pos: Vị trí đích
            agent_id: ID của robot
            constraints: Danh sách các ràng buộc
        Returns:
            Đường đi từ vị trí bắt đầu đến đích nếu tìm thấy, ngược lại trả về None
        """
        # Kiểm tra cache
        path_key = (start_pos, goal_pos)
        if path_key in self.path_cache:
            return self.path_cache[path_key]

        # Khởi tạo open set và closed set
        heuristic = self.compute_heuristics(goal_pos)
        open_set = [(heuristic[start_pos], 0, start_pos, [])]  # (f_score, time_step, current_pos, path)
        closed_set = set()

        # Các hướng di chuyển (4 hướng)
        directions = [(0,1), (1,0), (0,-1), (-1,0)]

        while open_set:
            f_score, time_step, current_pos, path = heapq.heappop(open_set)
            
            state_key = (current_pos, time_step)
            if state_key in closed_set:
                continue
            closed_set.add(state_key)

            if current_pos == goal_pos:
                final_path = path + [current_pos]
                self.path_cache[path_key] = final_path
                return final_path

            # Xét trường hợp đứng yên tại vị trí hiện tại
            next_pos = current_pos
            if self.check_constraints(current_pos, next_pos, time_step + 1, agent_id, constraints):
                new_path = path + [next_pos]
                new_f = len(new_path) - 1 + heuristic[next_pos]
                heapq.heappush(open_set, (new_f, time_step + 1, next_pos, new_path))

            # Xét các ô lân cận
            for dx, dy in directions:
                next_x = current_pos[0] + dx
                next_y = current_pos[1] + dy
                next_pos = (next_x, next_y)

                # Kiểm tra điều kiện hợp lệ
                if (next_x < 0 or next_x >= len(self.grid_map) or 
                    next_y < 0 or next_y >= len(self.grid_map[0]) or
                    self.grid_map[next_x][next_y] == 1 or
                    (next_pos, time_step + 1) in closed_set):
                    continue

                # Kiểm tra ràng buộc
                if not self.check_constraints(current_pos, next_pos, time_step + 1, agent_id, constraints):
                    continue

                # Tính điểm mới
                new_g_score = time_step + 1
                new_h_score = heuristic[next_pos]
                new_f_score = new_g_score + new_h_score

                heapq.heappush(open_set, (new_f_score, time_step + 1, next_pos, path + [current_pos]))

        return None  # Không tìm thấy đường đi

    def get_actions(self, state):
        """
        Lấy hành động cho tất cả robot sử dụng phương pháp Prioritized Planning
        
        Args:
            state: Trạng thái môi trường hiện tại
        Returns:
            Danh sách các hành động cho từng robot
        """
        # Reset trạng thái
        self.paths.clear()
        self.constraints.clear()
        
        # Cập nhật trạng thái robot
        self.robot_states = [(r[0]-1, r[1]-1, r[2]) for r in state['robots']]
        
        # Cập nhật trạng thái gói hàng
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
                
                if robot_pos == target_pos:  # Tại vị trí giao hàng
                    actions.append(('S', '2'))  # Thả gói hàng
                    self.in_transit_packages.remove(carrying_pkg)
                    self.delivered_packages.add(carrying_pkg)
                else:  # Cần di chuyển đến vị trí giao hàng
                    path = self.a_star_with_constraints(robot_pos, target_pos, robot_idx, self.constraints)
                    if path and len(path) > 1:
                        next_pos = path[1]
                        move = self.get_movement_direction(robot_pos, next_pos)
                        actions.append((move, '0'))
                        # Thêm ràng buộc cho các robot khác
                        for other_robot in range(len(self.robot_states)):
                            if other_robot != robot_idx:
                                self.constraints.append({
                                    'agent': other_robot,
                                    'loc': [next_pos],
                                    'timestep': state['time_step'] + 1,
                                    'final': False
                                })
                    else:
                        actions.append(('S', '0'))  # Đứng yên nếu không tìm thấy đường đi
                        
            else:  # Robot không mang gói hàng
                if self.waiting_packages:  # Có gói hàng cần nhặt
                    # Tìm gói hàng gần nhất
                    nearest_pkg = None
                    min_distance = float('inf')
                    for pkg_id in self.waiting_packages:
                        pkg_info = self.package_info[pkg_id]
                        pkg_pos = (pkg_info[1], pkg_info[2])
                        distance = abs(robot_pos[0] - pkg_pos[0]) + abs(robot_pos[1] - pkg_pos[1])
                        if distance < min_distance:
                            min_distance = distance
                            nearest_pkg = pkg_id

                    if nearest_pkg:
                        pkg_info = self.package_info[nearest_pkg]
                        pkg_pos = (pkg_info[1], pkg_info[2])
                        
                        if robot_pos == pkg_pos:  # Tại vị trí nhặt hàng
                            actions.append(('S', '1'))  # Nhặt gói hàng
                            self.waiting_packages.remove(nearest_pkg)
                            self.in_transit_packages.add(nearest_pkg)
                        else:  # Cần di chuyển đến vị trí nhặt hàng
                            path = self.a_star_with_constraints(robot_pos, pkg_pos, robot_idx, self.constraints)
                            if path and len(path) > 1:
                                next_pos = path[1]
                                move = self.get_movement_direction(robot_pos, next_pos)
                                actions.append((move, '0'))
                                # Thêm ràng buộc cho các robot khác
                                for other_robot in range(len(self.robot_states)):
                                    if other_robot != robot_idx:
                                        self.constraints.append({
                                            'agent': other_robot,
                                            'loc': [next_pos],
                                            'timestep': state['time_step'] + 1,
                                            'final': False
                                        })
                            else:
                                actions.append(('S', '0'))  # Đứng yên nếu không tìm thấy đường đi
                    else:
                        actions.append(('S', '0'))  # Đứng yên nếu không tìm thấy gói hàng
                else:
                    actions.append(('S', '0'))  # Không có gói hàng để nhặt
                    
        return actions
