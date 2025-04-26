# marl-delivery
MARL samples code for Package Delivery

# Thuật BFS
Baseline 1: 
- Cứ gán gói hàng tới con robot rảnh gần gói hàng đó nhất => iterate theo gói hàng.
    - Một khi đã gán gói hàng nào do robot giao thì sẽ con robot chỉ được phép đến chỗ gói hàng đó, không được tơ tưởng gói hàng khác.
- Các con robot đụng độ thì cho con robot có index bé nhất đi trước (đã được implement logic trong file `env.py`)

# Các attribute trong class `Agents`
- `self.robot_assignments`: là 1 dictionary, key: idx robot - values: idx gói hàng
- `self.robot_paths`: là 1 dictionary, key: idx robot - values: đường đi => đường đi này chỉ thay đổi, được xóa nếu robot đã đi đến cuối đường. 
- `self.pending_packages`: là 1 dictionary package cần được di chuyển, key: idx package - values: vị trí hiện tại package
# Ý tưởng code
## `class Agents` 
    - self.robot_assignments: key là robot_idx, value là package_idx
    - self.robot_paths: key là robot_idx, value là đường đi
    - self.pending_packages: key là package idx, value là vị trí của packages
    - self.time_step
## Các hàm utils
- `def update_pending_packages`: update các package nào đang cần di chuyển => logic hàm này đang chưa được rõ
- `def find_path`: tìm đường giữa 2 tuple start - end
- `def get_move_action`: convert bước đi từ vị trí sang các biến 'S', 'L', 'R', 'U', 'D' => quy định hành động đi của robot
- `def get_package_action`: lựa chọn hành động đi của robot => logic hàm này đang chưa được rõ
## Các hàm logic thuật toán 
- Hàm `def assign_packages()`:
    - Gán gói hàng nào ứng với robot nào
- Hàm `def get_actions(self, state)`: cần hoàn thiện
    - Input `state` sẽ có các key như sau:
        - `time_step`: thời điểm trong simulation
        - `map`: static, không bao giờ đổi do load từ file `map.txt` có sẵn
        - `robots`:  có `(robot.position[0] + 1, robot.position[1] + 1, robot.carrying)` => giá trị thực trên grid (giá trị đánh theo 0-indexed, dùng để chạy thuật toán tìm đường) và robot.carrying = idx package đang carry
        - `packages`: có `(id, start[0] + 1, start[1] + 1, target[0] + 1, target[1] + 1, start_time, deadline)`
    - Output sẽ là `actions.append((list_actions[move], str(pkg_act)))`:
        - Kích cỡ `n_robots` x 2: `n_robots` tuple - mỗi tuple có 2 giá trị.
    - Logic hàm:
        - Bước 1: cập nhật trạng thái gói hàng: `_update_pending_packages(state)`
        - Bước 2: gán gói hàng nào do con robot nào `_assign_packages()` 
            - lưu ý trong hàm này đã gán đường cho robot nếu robot được giao đi nhận gói hàng nào đó; nếu không được giao gì thì không đi đâu cả đứng yên
        - Bước 3: các con robot nhận thông tin về nhiệm vụ và tiến hành nhiệm vụ (đi đến chỗ đó, thả gói hàng ...)
            - Move: đi theo`_get_move_action(current_pos, next_pos)` => nếu được giao thì đã có đường tìm sẵn cho nó đi từ hàm `_assign_packages()` trước đó
            - Pkg_act: đi theo `_get_package_action` 
