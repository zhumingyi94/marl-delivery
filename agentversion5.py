import random
from collections import deque
# import networkx as nx

# Các vị trí các ô trên board, vị trí robots, packages đều tính từ 1

# Tính vị trí hợp lệ của bước đi
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

# Kiểm tra 1 vị trí có hợp lệ không (ô chứa số 0 trên board)
def valid_position(map, position):
    i, j = position
    if i <= 1 or i >= len(map) or j <= 1 or j >= len(map[0]):
        return False
    if map[i-1][j-1] == 1:
        return False
    return True

# Tìm tất cả chu trình sẽ xuất hiện từ các actions thực hiện

def find_all_cycle(map, robots, actions):
    visited = {}
    pos_current = {}
    pos_future = {}

    for i in range(len(robots)):
        pos_robot = (robots[i][0], robots[i][1])
        pos_current[i] = pos_robot
        visited[pos_robot] = False
        next_pos = compute_valid_position(map, pos_robot, actions[i][0])
        pos_future[pos_robot] = next_pos

    list_cycles = []
    list_actions = []

    # Xét các thành phần liên thông
    # Kết quả dễ nhận thấy: Các thành phần chu trình sẽ ở các thành phần liên thông khác nhau
    # Hay mỗi thành phần liên thông chỉ có nhiều nhất một chu trình
    for i in range(len(robots)):
        queue = deque()
        if not visited[pos_current[i]]:
            queue.append(pos_current[i])
            visited[pos_current[i]] = True

        start_pos = None
        history = [pos_current[i]] # Lưu những vị trí đã xuất hiện trong thành phần liên thông này

        while queue:
            start = queue.popleft()
            target = pos_future[start]

            # Thoát luôn vì vị trí này không thể tạo nên chu trình
            # Vì vị trí định đi tới không trùng với vị trí đang có robots đứng
            # Vì chỉ có duy nhất 1 đường đi ra từ mỗi node nên không thể có nhiều hơn 1 nhánh
            if target not in visited:
                break

            if not visited[target]:
                queue.append(target)
                visited[target] = True
                history.append(target)
            else:
                # Nếu vị trí định tới đã được lưu thì đã tồn tại chu trình
                # Thoát luôn vì dù sao cũng không thể còn cạnh nào nữa
                if target in history and target != start:
                    start_pos = target
                break

        cycle = []
        action =[]

        # Nếu tồn tại chu trình thì truy ngược lại toàn bộ chu trình đó
        while start_pos:
            # Nếu node được duyệt lại là đã tìm được đầy đủ chu trình
            if start_pos in cycle:
                break

            # Chỉ cần tìm robot duy nhất đứng tại vị trí xác định
            for j in range(len(robots)):
                if start_pos == (robots[j][0], robots[j][1]):
                    action.append(actions[j])
                    break

            cycle.append(start_pos)
            start_pos = pos_future[start_pos]

        # Nếu có chu trình thì lưu lại thứ tự các robot và các action tạo nên chu trình
        # => Để tìm cách giải quyết
        if len(cycle) > 0:
            list_cycles.append(cycle)
            list_actions.append(action)

    return list_cycles, list_actions

# Tìm 1 đường đi ngắn nhất giữa 2 ô không bị chặn (2 ô phân biệt chứa sô 0 trên board)
def get_shortest_path(map):
    list_path = {}
    valid_pos = []
    m, n = len(map), len(map[0])
    directions = [("U", (-1, 0)), ("L", (0, -1)), ("R", (0, 1)), ("D", (1, 0))]

    # Lưu những vị trí không bị chặn
    for i in range(m):
        for j in range(n):
            if map[i][j] == 0:
                valid_pos.append((i, j))

    # Tại mỗi vị trí không bị chặn, dùng BFS để tìm đường đi ngắn nhất tới tất cả các vị trí khác
    for i in range(len(valid_pos)):
        dist = [[-1] * n for _ in range(m)] # Mảng 2 chiều đánh dấu những vị trí được xét hay chưa (nếu = 0)
        str_path = [[""] * n for _ in range(m)] # Mảng 2 chiều lưu đường đi từ vị trí xét đến vị trí hiện tại
        # Có thể xử lý theo lưu tất cả đường có thể, để sau có chiến thuật lựa chọn nào đó

        queue = deque()
        queue.append(valid_pos[i])

        start_i, start_j = valid_pos[i]
        dist[start_i][start_j] = 0
        str_path[start_i][start_j] = ""

        while queue:
            x, y = queue.popleft()

            # random.shuffle(directions) # có thể shuffle lên để tìm kiếm những hướng đi mới
            for (direc_move, (d_x, d_y)) in directions:
                pos_x = x + d_x
                pos_y = y + d_y
                if 0 < pos_x < m and 0 < pos_y < n and dist[pos_x][pos_y] == -1:
                    if map[pos_x][pos_y] == 0:
                        dist[pos_x][pos_y] = dist[x][y] + 1
                        str_path[pos_x][pos_y] = str_path[x][y] + direc_move
                        queue.append((pos_x, pos_y))

                        start = (start_i + 1, start_j + 1)
                        target = (pos_x + 1, pos_y + 1)
                        list_path[(start, target)] = str_path[pos_x][pos_y]
    return list_path

# Khởi tạo agents
class AgentsVersion5:
    # Khởi tạo mặc định
    def __init__(self):
        self.state = None
        self.map = []
        self.board_path = {} # Ánh xạ (start_pos, target_pos) với đường đi giữa 2 v trí
        self.robots = [] # Lưu thông tin của các robot (trước khi nhận state mới)
        self.packages = {} # Lưu tất cả packages đã xuất hiện (dùng map để dễ truy cập thông qua id mà không cần quan tâm thứ tự trong mảng)
        self.waiting_packages = [] # Danh sách gói hàng trong trạng thái chờ
        self.transiting_packages = [] # Danh sách gói hàng đang được giao
        self.transited_packages = [] # Danh sách gói hàng đã được giao
        self.target_transit = {} # Ánh xạ robot với waiting package đang được chỉ định phải nhặt
        self.count_repeat = [] # Lưu số lần vị trí đã được lặp lại
        self.last_move = [] # Lưu move của step trước

        self.NUM_REPEAT = 10

    # Khởi tạo thông tin dựa trên state được khởi tạo ban đầu
    def init_agents(self, state):
        self.state = state
        self.map = state['map']
        self.board_path = get_shortest_path(state['map'])
        self.robots = [(robot[0], robot[1], 0) for robot in state['robots']]
        self.count_repeat = [0] * len(state['robots'])

    # Kiểm tra 2 vị trí có cùng thành phần liên thông không
    def differ_connected(self, start, target):
        return (start, target) not in self.board_path

    # Lấy str biểu diễn đường đi từ start tới target (khác hoàn toàn target tơi start)
    def get_action(self, start, target):
        # Nếu 2 vị trí trùng nhau tức là không cần di chuyển
        if start == target:
            return ""
        return self.board_path[(start, target)]

    # def optimal_assign(self, robot_list, waiting_package_list):
    #     0

    # Đưa ra action cho từng robot theo thứ tự dựa trên state nhận được
    def get_actions(self, state, alpha=1, beta=1):
        print(state)

        actions = []
        map = state['map']
        robots = state['robots']
        packages = state['packages']

        packages_owned = []

        # Thêm tất cả package mới xuất hiện vào danh sách chờ
        for package in packages:
            self.packages[package[0]] = package
            self.waiting_packages.append(package)

        # Duyệt qua từng robot
        for i in range(len(robots)):
            if (robots[i][0], robots[i][1]) == (self.robots[i][0], self.robots[i][1]):
                self.count_repeat[i] += 1
            else:
                self.count_repeat[i] = 1
            if self.count_repeat[i] >= self.NUM_REPEAT and self.last_move[i][0] != 'S':
                pos_robot = (robots[i][0], robots[i][1])
                moves = ['L', 'R', 'U', 'D']
                moves.remove(self.last_move[i][0])
                for move in moves:
                    new_pos_robot = compute_valid_position(map, pos_robot, move)
                    if valid_position(map, new_pos_robot):
                        actions.append((str(move), str(0)))
                        break
                continue

            last_pos_robot_i, last_pos_robot_j, last_carrying = self.robots[i]
            pos_robot_i, pos_robot_j, carrying = robots[i]
            pos_robot = (pos_robot_i, pos_robot_j)
            print(f"Robot {i} dang o vi tri {pos_robot}")

            if carrying != 0: # Nếu robot đang cầm package
                # Robot vừa nhặt thành công package trong step trước
                if last_carrying == 0:
                    self.transiting_packages.append(self.packages[carrying])
                    self.waiting_packages.remove(self.packages[carrying])

                # Robot đang trên đường đi giao package
                print(f"Transit package set includes: {self.transiting_packages}")
                print(f"Robot {i} in {pos_robot} and carry package_id {carrying}")

                transiting_package = self.packages[carrying] # Gói hàng đang được giao (truy xuất thông qua carrying)
                target_pos = (transiting_package[3], transiting_package[4])
                print(f"Target package {carrying} in {target_pos}")
                # Vì lúc nhặt đã xét chỉ nhặt gói hàng có start và target trong 1 thành phần liên thông, nên luôn tồn tại đường đi rồi
                move_path = self.get_action(pos_robot, target_pos)
                move = 'S' if len(move_path) == 0 else move_path[0]
                pkg_act = 2 if len(move_path) <= 1 else 0
                actions.append((str(move), str(pkg_act)))
                continue
            else: # Nếu robot đang không cầm package nào
                # Robot mới thả package trong step trước
                if last_carrying != 0:
                    transited_package = self.packages[last_carrying]
                    self.transited_packages.append(transited_package)
                    self.transiting_packages.remove(transited_package)

                # Tìm đường đi nhặt gói hàng có tổng quãng đường gần nhất
                # Nếu đang hết package chờ được giao thì cho robot stay
                if len(self.waiting_packages) == 0:
                    actions.append((str('S'), str(0)))
                    continue
                print(f"Waiting package set includes: {self.waiting_packages}")

                # Ánh xạ từ vị trí chứa package tới tập các package_id trong vị trí đó
                valid_pos_package = {}
                for package in self.waiting_packages:
                    pos = (package[1], package[2])
                    # Bỏ qua những package_id đã được nhắm để nhặt
                    if pos in packages_owned:
                        continue
                    # Nếu chưa tồn tại vị trí trong map thì gán giá trị bằng package_id luôn
                    if pos not in valid_pos_package:
                        valid_pos_package[pos] = package[0]
                    # Nếu đã tồn tại thì gán với package_id nhỏ nhất
                    valid_pos_package[pos] = min(valid_pos_package[pos], package[0])

                len_min_path = 10000
                package_id = -1

                # Tìm package tốt nhất
                for start_package in valid_pos_package:
                    package = self.packages[valid_pos_package[start_package]]
                    # if package[0] in packages_owned # Dùng để tránh 2 robot cùng đi nhặt 1 package
                    if True:
                        target_package = (package[3], package[4])

                        # Nếu (pos_package và start_package) hoặc (start_package) khác thành phần liên thông thì bỏ qua không nhặt
                        # (Vì nếu không sẽ lỗi truy xuất đường đi)
                        if self.differ_connected(pos_robot, start_package):
                            continue
                        if self.differ_connected(start_package, target_package):
                            continue

                        # Hàm đánh giá lựa chọn là tổng quãng đường từ vị trí hiện tại với vị trí package và tới vị trí giao package
                        start_path = self.get_action(pos_robot, start_package)
                        target_path = self.get_action(start_package, target_package)
                        len_path = alpha * len(start_path) + beta * len(target_path)

                        if len_path < len_min_path:
                            len_min_path = len_path
                            package_id = package[0]

                # Không tìm thấy package nào phù hợp để nhặt
                if package_id == -1:
                    actions.append((str('S'), str(0)))
                    continue

                # Vì nếu có package_id thỏa mãn thì robot chắc chắn nhặt được (mà đảm bảo không nhặt cùng robot khác)
                waited_package = self.packages[package_id]
                print(f"Robot {i} in way to carry package_id {waited_package}")

                start_package = (waited_package[1], waited_package[2])
                packages_owned.append(start_package)

                move_path = self.get_action(pos_robot, start_package)
                move = 'S' if len(move_path) == 0 else move_path[0]
                pkg_act = 1 if len(move_path) <= 1 else 0
                actions.append((str(move), str(pkg_act)))

            print(f"Robot {i} execute {(move, pkg_act)}")
        print(f"Start Actions : {actions}")

        # Cập nhật vị trí robot của state hiện tại vào bộ nhớ
        for i in range(len(robots)):
            self.robots[i] = robots[i]

        old_pos = {} # Ánh xạ vị trí có robot đang đứng đến id của robot đó
        new_pos = {} # Ánh xạ từ 1 vị trí đến danh sách id các robot muốn tới vị trí đó

        # Lưu thông tin về robot hiện tại và dự định
        for i in range(len(actions)):
            pos_robot = (robots[i][0], robots[i][1])
            old_pos[pos_robot] = i
            next_pos_robot = compute_valid_position(map, pos_robot, actions[i][0])

            # Kiểm tra vị trí muốn tới có trong danh sách chưa, nếu chưa thì tạo 1 mảng để lưu các id robot
            if next_pos_robot not in new_pos:
                new_pos[next_pos_robot] = []
            new_pos[next_pos_robot].append(pos_robot)

        # Tìm tất cả chu trình sẽ xảy ra
        cycles_list, actions_list = find_all_cycle(map, robots, actions)

        # Duyệt qua từng chu trình để phá trạng thái này
        for (element_robot, element_action) in zip(cycles_list, actions_list):
            print(f"Cycle includes robot: {element_robot} and corresponding action: {element_action}")

            check = False # Biến kiểm tra xem có phá trạng thái chu trình bằng cách thay đổi action của 1 robot chưa
            for i in range(len(element_action)):
                pos_robot = (element_robot[i][0], element_robot[i][1])
                next_pos_robot = compute_valid_position(map, pos_robot, element_action[i][0])

                # Vì nó là chu trình, nên không cần xét vị trí mới có thuộc các tập không (chắc chắn phải thuộc tập hợp)
                moves = ['L', 'R', 'U', 'D']
                print(element_action[i][0])
                moves.remove(element_action[i][0])
                # random.shuffle(moves) # Có thể dùng

                # Duyệt từng hướng di chuyển xem có thay đổi được action đang xét không
                for move in moves:
                    new_pos_robot = compute_valid_position(map, pos_robot, move)
                    if new_pos_robot not in old_pos and new_pos_robot not in new_pos:
                        new_pos[new_pos_robot] = [pos_robot] # Có thể gán bằng bất cứ số nào, chỉ ần để new_pos_robot có trong new_pos
                        new_pos[next_pos_robot].remove(pos_robot)
                        check = True

                        for j in range(len(robots)):
                            if pos_robot == (robots[j][0], robots[j][1]):
                                actions[j] = (move, element_action[i][1])
                        break

                # Nếu đã thay đổi thành công 1 action trong cycle thì thoát khỏi cycle luôn (tránh thay đổi tất cả action thì vô nghĩa)
                if check:
                    break

        print(f"Actions after process cycles: {actions}")

        # Xử lý những robot có thể gây chắn đường khi ở trạng thái
        for i in range(len(actions)):
            pos_robot = (robots[i][0], robots[i][1])
            if actions[i][0] == 'S':
                if len(new_pos[pos_robot]) > 1: # Có robot khác muốn đi tới vị trí này
                    moves = ['L', 'R', 'U', 'D']
                    # random.shuffle(moves)

                    # Duyệt từng hướng di chuyển xem có thay đổi được action đang xét không
                    for move in moves:
                        new_pos_robot = compute_valid_position(map, pos_robot, move)
                        if new_pos_robot not in old_pos and new_pos_robot not in new_pos:
                            actions[i] = (move, actions[i][1])
                            new_pos[new_pos_robot] = [pos_robot]
                            break

        self.last_move = actions

        print(f"Robots are in: {self.robots}")
        print(f"Final Actions is: {actions}")
        return actions