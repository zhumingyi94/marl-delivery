from astar_base import AStarBase
import heapq
import numpy as np
import copy
from collections import deque
from utils import manhattan_distance


class CBSAgent(AStarBase):
    """
    Agent sử dụng Conflict-Based Search (CBS) 
    """
    def __init__(self):
        super().__init__()
        # Khởi tạo các biến để lưu trữ
        self.paths = {}  # Đường đi cho mỗi robot
        self.constraints = {}  # Ràng buộc cho mỗi robot
        self.assignments = {}  # Gán gói hàng cho robot
        self.best_solution = None  # Lưu giải pháp tốt nhất tìm được
        self.position_history = {}  # Lưu lịch sử vị trí của robot
        self.stuck_count = {}  # Đếm số lần robot bị kẹt tại một vị trí

    def init_agents(self, state):
        """Khởi tạo agent với trạng thái ban đầu"""
        super().init_agents(state)
        self.assignments = {}
        self.constraints = {}
        self.best_solution = None
        self.position_history = {}
        self.stuck_count = {}
        
    def _a_star_with_constraints(self, start, goal, robot_id, constraints, max_time=100):
        """
        A* tìm đường với các ràng buộc
        start: vị trí bắt đầu (x, y)
        goal: vị trí đích (x, y)
        robot_id: id của robot
        constraints: các ràng buộc trên đường đi
        """
        if start == goal:
            return [start]
        
        # Sử dụng hàm heuristic từ lớp cơ sở
        open_set = [(manhattan_distance(start, goal), 0, start, [])]
        closed_set = set()
        
        # Các hướng di chuyển (4 hướng + đứng yên)
        directions = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
        
        time_step = 0
        while open_set and time_step < max_time:
            f_score, g_score, current, path = heapq.heappop(open_set)
            
            if current == goal:
                # Đã tìm thấy đường đi
                return path + [current]
            
            if (current, g_score) in closed_set:
                continue
            
            closed_set.add((current, g_score))
            
            # Xét các hướng di chuyển
            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy
                next_pos = (nx, ny)
                next_time = g_score + 1
                
                # Kiểm tra vị trí hợp lệ
                if not self._valid_position(next_pos):
                    continue
                
                # Kiểm tra ràng buộc
                if not self._check_constraints(next_pos, current, next_time, robot_id, constraints):
                    continue
                
                # Thêm vào open set
                new_g = next_time
                new_f = new_g + manhattan_distance(next_pos, goal)
                heapq.heappush(open_set, (new_f, new_g, next_pos, path + [current]))
            
            time_step += 1
        
        # Không tìm thấy đường đi
        return None

    def _valid_position(self, position):
        """Kiểm tra vị trí có hợp lệ không"""
        r, c = position
        if r < 0 or r >= len(self.grid_map) or c < 0 or c >= len(self.grid_map[0]):
            return False
        return self.grid_map[r][c] == 0

    def _check_constraints(self, next_pos, current_pos, time_step, robot_id, constraints):
        """Kiểm tra ràng buộc tại một vị trí"""
        for constraint in constraints:
            if constraint['time'] == time_step:
                # Ràng buộc vị trí (vertex constraint)
                if len(constraint['loc']) == 1 and constraint['loc'][0] == next_pos:
                    return False
                # Ràng buộc cạnh (edge constraint)
                elif len(constraint['loc']) == 2 and constraint['loc'][0] == next_pos and constraint['loc'][1] == current_pos:
                    return False
        return True

    def _detect_conflict(self, paths):
        """Phát hiện xung đột giữa các đường đi"""
        max_path_len = 0
        for path in paths.values():
            max_path_len = max(max_path_len, len(path))
        
        # Duyệt qua từng thời điểm
        for t in range(max_path_len):
            # Kiểm tra xung đột theo vị trí (vertex conflict)
            positions_at_t = {}
            for robot_id, path in paths.items():
                if t < len(path):
                    pos_t = path[t]
                    if pos_t in positions_at_t:
                        # Xung đột: hai robot ở cùng vị trí
                        return {
                            'type': 'vertex', 
                            'time': t,
                            'loc': [pos_t],
                            'robots': [robot_id, positions_at_t[pos_t]]
                        }
                    positions_at_t[pos_t] = robot_id
            
            # Kiểm tra xung đột theo cạnh (edge conflict)
            if t < max_path_len - 1:
                for robot_i, path_i in paths.items():
                    for robot_j, path_j in paths.items():
                        if robot_i >= robot_j:
                            continue
                        if t < len(path_i) - 1 and t < len(path_j) - 1:
                            if path_i[t] == path_j[t+1] and path_i[t+1] == path_j[t]:
                                # Xung đột: hai robot di chuyển ngược chiều
                                return {
                                    'type': 'edge',
                                    'time': t+1,
                                    'loc': [path_i[t+1], path_i[t]],
                                    'robots': [robot_i, robot_j]
                                }
        
        # Không phát hiện xung đột
        return None

    def _conflict_based_search(self, starts, goals, max_iterations=400):
        """Thuật toán Conflict-Based Search với cơ chế đơn giản để handle deadlock"""
        # Khởi tạo root node của cây tìm kiếm CBS
        root = {
            'constraints': {robot_id: [] for robot_id in range(len(starts))},
            'paths': {},
            'cost': 0
        }
        
        # Tìm đường đi cho mỗi robot không có ràng buộc
        for robot_id in range(len(starts)):
            path = self._a_star_with_constraints(
                starts[robot_id], 
                goals[robot_id], 
                robot_id, 
                root['constraints'][robot_id]
            )
            if not path:
                # Nếu không tìm thấy đường đi, dùng đường đi đơn giản: ở yên
                path = [starts[robot_id]]
            
            root['paths'][robot_id] = path
            root['cost'] += len(path)
        
        # Lưu giải pháp hiện tại là tốt nhất
        self.best_solution = root['paths']
        
        # Khởi tạo priority queue
        open_list = [root]
        
        # Biến theo dõi stagnation
        iteration = 0
        stagnation_count = 0
        prev_best_cost = float('inf')
        
        while open_list and iteration < max_iterations:
            # Lấy node có chi phí thấp nhất
            node = open_list.pop(0)
            
            # Kiểm tra stagnation
            if node['cost'] >= prev_best_cost:
                stagnation_count += 1
            else:
                stagnation_count = 0
                prev_best_cost = node['cost']
            
            # Nếu bị kẹt quá lâu, thêm yếu tố ngẫu nhiên để thoát khỏi minimum local
            if stagnation_count > 5:
                self._add_random_constraints(node, starts)
                stagnation_count = 0
            
            # Kiểm tra xung đột
            conflict = self._detect_conflict(node['paths'])
            if not conflict:
                # Không tìm thấy xung đột, trả về đường đi
                self.best_solution = node['paths']
                return node['paths']
            
            # Xử lý xung đột
            for robot_id in conflict['robots']:
                # Tạo node con với ràng buộc mới
                new_constraints = copy.deepcopy(node['constraints'])
                if robot_id not in new_constraints:
                    new_constraints[robot_id] = []
                
                new_constraints[robot_id].append({
                    'time': conflict['time'],
                    'loc': conflict['loc']
                })
                
                # Tìm đường đi mới với ràng buộc mới
                new_path = self._a_star_with_constraints(
                    starts[robot_id], 
                    goals[robot_id], 
                    robot_id, 
                    new_constraints[robot_id]
                )
                
                if not new_path:
                    # Nếu không tìm thấy đường đi, dùng đường đi đơn giản
                    new_path = [starts[robot_id]]
                
                # Tạo node con mới
                new_paths = copy.deepcopy(node['paths'])
                new_paths[robot_id] = new_path
                
                # Tính toán chi phí mới
                new_cost = sum(len(path) for path in new_paths.values())
                
                child_node = {
                    'constraints': new_constraints,
                    'paths': new_paths,
                    'cost': new_cost
                }
                
                # Thêm node con vào open_list
                insert_pos = 0
                while insert_pos < len(open_list) and open_list[insert_pos]['cost'] < child_node['cost']:
                    insert_pos += 1
                open_list.insert(insert_pos, child_node)
            
            iteration += 1
        
        # Fallback đến giải pháp tốt nhất đã tìm thấy
        return self.best_solution

    def _add_random_constraints(self, node, starts):
        """
        Thêm ràng buộc ngẫu nhiên để thoát khỏi minimum local
        """
        # Chọn một robot ngẫu nhiên
        robot_id = np.random.randint(0, len(starts))
        if robot_id not in node['constraints']:
            node['constraints'][robot_id] = []
        
        # Lấy đường đi hiện tại của robot
        path = node['paths'].get(robot_id, [])
        if len(path) > 1:
            # Buộc robot không đi theo đường đi hiện tại
            node['constraints'][robot_id].append({
                'time': 1,
                'loc': [path[1]]
            })

    def get_actions(self, state):
        """Trả về các hành động cho tất cả robot"""
        # Cập nhật trạng thái
        self.update_state(state)
        
        # Cập nhật và xử lý trạng thái kẹt
        self._update_stuck_count()
        
        # Tính toán vị trí bắt đầu và đích cho mỗi robot
        starts, goals, robot_goals = self._compute_starts_and_goals()
        
        # Sử dụng CBS để tìm đường đi
        paths = self._conflict_based_search(starts, goals)
        
        # Chuyển đổi đường đi thành hành động
        actions = []
        
        for i, robot in enumerate(self.robot_states):
            robot_pos = (robot[0], robot[1])
            target = robot_goals.get(i, robot_pos)
            carrying_pkg = robot[2]
            
            # Kiểm tra xem robot có bị kẹt quá lâu không
            if i in self.stuck_count and self.stuck_count[i] > 5:
                # Tạo hành động ngẫu nhiên để thoát khỏi trạng thái kẹt
                move = self._get_random_move(robot_pos)
                actions.append((move, '0'))
                # Reset bộ đếm
                self.stuck_count[i] = 0
                continue
            
            if robot_pos == target:
                # Robot đã đến đích
                if carrying_pkg > 0:
                    # Giao hàng
                    actions.append(('S', '2'))
                    if carrying_pkg in self.in_transit_packages:
                        self.in_transit_packages.remove(carrying_pkg)
                    self.delivered_packages.add(carrying_pkg)
                elif i in self.assignments:
                    # Nhặt gói hàng
                    pkg_id = self.assignments[i]
                    pkg_info = self.package_info[pkg_id]
                    if (pkg_info[1], pkg_info[2]) == robot_pos:
                        actions.append(('S', '1'))
                        if pkg_id in self.waiting_packages:
                            self.waiting_packages.remove(pkg_id)
                        self.in_transit_packages.add(pkg_id)
                    else:
                        actions.append(('S', '0'))
                else:
                    actions.append(('S', '0'))
            else:
                # Di chuyển theo đường đi
                path = paths.get(i, [robot_pos])
                if len(path) > 1:
                    move = self._path_to_action(robot_pos, path[1])
                    actions.append((move, '0'))
                else:
                    actions.append(('S', '0'))
        
        return actions

    def update_state(self, state):
        """Cập nhật trạng thái nội bộ"""
        # Cập nhật trạng thái robot
        self.robot_states = [(r[0]-1, r[1]-1, r[2]) for r in state['robots']]
        
        # Cập nhật trạng thái gói hàng
        for pkg in state['packages']:
            pkg_id = pkg[0]
            if pkg_id not in self.package_info:
                self.package_info[pkg_id] = (pkg_id, pkg[1]-1, pkg[2]-1, pkg[3]-1, pkg[4]-1, pkg[5])
            if (pkg[5] <= state['time_step'] and 
                pkg_id not in self.in_transit_packages and 
                pkg_id not in self.delivered_packages and
                pkg_id not in self.waiting_packages):
                self.waiting_packages.add(pkg_id)

    def _update_stuck_count(self):
        """
        Cập nhật bộ đếm cho robot bị kẹt tại chỗ
        """
        for i, robot in enumerate(self.robot_states):
            # Lấy vị trí và trạng thái
            current_pos = (robot[0], robot[1])
            current_status = robot[2]
            
            # Cập nhật lịch sử vị trí
            if i not in self.position_history:
                self.position_history[i] = {
                    'pos': current_pos,
                    'status': current_status,
                    'count': 0
                }
                self.stuck_count[i] = 0
                continue
            
            # Kiểm tra xem robot có bị kẹt tại chỗ không
            if (self.position_history[i]['pos'] == current_pos and 
                self.position_history[i]['status'] == current_status):
                # Robot chưa di chuyển, tăng bộ đếm
                self.position_history[i]['count'] += 1
                self.stuck_count[i] += 1
            else:
                # Robot đã di chuyển, reset bộ đếm
                self.position_history[i] = {
                    'pos': current_pos,
                    'status': current_status,
                    'count': 0
                }
                self.stuck_count[i] = 0

    def _get_random_move(self, position):
        """
        Tạo một hướng di chuyển ngẫu nhiên nhưng hợp lệ từ vị trí hiện tại
        """
        directions = ['U', 'D', 'L', 'R']
        np.random.shuffle(directions)  # Xáo trộn các hướng
        
        for dir in directions:
            next_pos = None
            if dir == 'U':
                next_pos = (position[0] - 1, position[1])
            elif dir == 'D':
                next_pos = (position[0] + 1, position[1])
            elif dir == 'L':
                next_pos = (position[0], position[1] - 1)
            elif dir == 'R':
                next_pos = (position[0], position[1] + 1)
            
            # Kiểm tra vị trí hợp lệ
            if self._valid_position(next_pos):
                return dir
        
        # Nếu không tìm được hướng hợp lệ, đứng yên
        return 'S'

    def _compute_starts_and_goals(self):
        """Tính toán vị trí bắt đầu và đích cho mỗi robot"""
        starts = []
        goals = []
        robot_goals = {}
        
        # Đặt lại assignments
        self.assignments = {}
        
        # Xác định vị trí bắt đầu và đích cho mỗi robot
        for i, robot in enumerate(self.robot_states):
            robot_pos = (robot[0], robot[1])
            carrying_pkg = robot[2]
            
            starts.append(robot_pos)
            
            if carrying_pkg > 0:
                # Robot đang mang gói hàng
                pkg_info = self.package_info[carrying_pkg]
                target_pos = (pkg_info[3], pkg_info[4])
                goals.append(target_pos)
                robot_goals[i] = target_pos
            else:
                # Robot không mang gói hàng
                best_pkg = self._find_best_package(robot_pos)
                
                if best_pkg:
                    # Gán gói hàng cho robot
                    self.assignments[i] = best_pkg
                    pkg_info = self.package_info[best_pkg]
                    pickup_pos = (pkg_info[1], pkg_info[2])
                    goals.append(pickup_pos)
                    robot_goals[i] = pickup_pos
                else:
                    # Không có gói hàng, robot đứng yên
                    goals.append(robot_pos)
                    robot_goals[i] = robot_pos
        
        return starts, goals, robot_goals

    def _path_to_action(self, curr_pos, next_pos):
        """Chuyển đổi từ đường đi thành hành động di chuyển"""
        dx, dy = next_pos[0] - curr_pos[0], next_pos[1] - curr_pos[1]
        
        if dx == 0 and dy == 0:
            return 'S'
        elif dx == -1 and dy == 0:
            return 'U'
        elif dx == 1 and dy == 0:
            return 'D'
        elif dx == 0 and dy == -1:
            return 'L'
        elif dx == 0 and dy == 1:
            return 'R'
        
        return 'S'  # Fallback

    def _find_best_package(self, robot_pos):
        """
        Tìm gói hàng tốt nhất cho một robot
        Ưu tiên gói hàng gần nhưng cũng xem xét khoảng cách để giao hàng
        """
        best_pkg = None
        best_score = float('inf')
        
        for pkg_id in self.waiting_packages:
            if pkg_id in self.assignments.values():
                continue  # Gói đã được gán cho robot khác
            
            pkg_info = self.package_info[pkg_id]
            pickup_pos = (pkg_info[1], pkg_info[2])
            target_pos = (pkg_info[3], pkg_info[4])
            
            # Tính toán điểm dựa trên khoảng cách Manhattan
            pickup_distance = manhattan_distance(robot_pos, pickup_pos)
            delivery_distance = manhattan_distance(pickup_pos, target_pos)
            
            # Công thức tính điểm: ưu tiên gói gần nhưng cũng xem xét đường đi giao hàng
            score = 3 * pickup_distance + delivery_distance
            
            if score < best_score:
                best_score = score
                best_pkg = pkg_id
        
        return best_pkg
