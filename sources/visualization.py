import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, Patch, Circle
from matplotlib.widgets import Button, Slider
from matplotlib.lines import Line2D

from env import Environment
from sources.agents.agentversion6 import AgentsVersion6 as Agents
import argparse

class DeliveryVisualizer:
    def __init__(self, env):
        self.env = env
        self.map = np.array(env.grid)
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.robot_markers = []
        self.package_markers = {}
        self.time_text = None
        self.reward_text = None
        self.state_history = []
        self.reward_history = []

        self.colors = {
            'wall': 'black',
            'free': 'white',
            'robot': 'blue',
            'package_waiting': 'green',
            'package_transit': 'orange',
            'package_delivered': 'white',
            'target': 'purple'
        }

        self.animation_speed = 0.00001
        self.animation_running = True
        self.pause_button = None
        self.speed_slider = None

        self.setup_plot()
        self.setup_controls()

    def setup_plot(self):
        cmap = ListedColormap(['white', 'black'])

        self.ax.imshow(self.map, cmap=cmap)
        self.ax.grid(True, color='gray', linestyle='-', linewidth=0.5)
        self.ax.set_title('Multi-Agent Package Delivery Simulation')
        self.ax.set_xlabel('Column')
        self.ax.set_ylabel('Row')

        self.time_text = self.ax.text(0.02, 0.95, 'Time Step: 0',
                                      transform=self.ax.transAxes,
                                      fontsize=12, fontweight='bold',
                                      bbox=dict(facecolor='white', alpha=0.7))
        self.reward_text = self.ax.text(0.02, 0.90, 'Total Reward: 0.00',
                                        transform=self.ax.transAxes,
                                        fontsize=12, fontweight='bold',
                                        bbox=dict(facecolor='white', alpha=0.7))
        self._create_legend()

    def setup_controls(self):
        self.fig.subplots_adjust(bottom=0.15)

        pause_ax = self.fig.add_axes([0.45, 0.05, 0.1, 0.04])
        speed_ax = self.fig.add_axes([0.2, 0.05, 0.2, 0.03])

        self.pause_button = Button(pause_ax, 'Pause')
        self.pause_button.on_clicked(self.toggle_pause)

        self.speed_slider = Slider(speed_ax, 'Speed', 0.1, 2.0,
                                   valinit=self.animation_speed, valstep=0.1)
        self.speed_slider.on_changed(self.update_speed)

        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def toggle_pause(self, event):
        self.animation_running = not self.animation_running
        self.pause_button.label.set_text('Play' if not self.animation_running else 'Pause')
        self.fig.canvas.draw_idle()

    def update_speed(self, val):
        self.animation_speed = val

    def on_key_press(self, event):
        if event.key == ' ':
            self.toggle_pause(event)
        elif event.key == 'right':  # Right arrow - advance one frame when paused
            if not self.animation_running:
                self.step_animation()

    def step_animation(self):
        pass

    def _create_legend(self):
        self.fig.subplots_adjust(right=0.8)

        legend_elements = [
            Patch(facecolor='black', edgecolor='black', label='Wall'),
            Patch(facecolor='white', edgecolor='gray', label='Free Space'),
            Circle((0, 0), radius=1, facecolor=self.colors['robot'], edgecolor='black', label='Robot'),
            Patch(facecolor=self.colors['package_waiting'], edgecolor='black', alpha=0.5, label='Waiting Package'),
            Patch(facecolor=self.colors['package_transit'], edgecolor='black', alpha=0.5, label='Package in Transit'),
            Patch(facecolor=self.colors['package_delivered'], edgecolor='black', alpha=0.5, label='Delivered Package'),
            Patch(facecolor=self.colors['target'], edgecolor='black', alpha=0.5, label='Target Location'),
            Line2D([0], [0], marker='$R0$', color='w', markerfacecolor='black', markersize=15, label='Robot ID'),
            Line2D([0], [0], marker='$P1$', color='w', markerfacecolor='black', markersize=15, label='Package ID'),
            Line2D([0], [0], marker='$T1$', color='w', markerfacecolor='black', markersize=15, label='Target ID')
        ]

        self.ax.legend(handles=legend_elements,
                       loc='center left',
                       bbox_to_anchor=(1.02, 0.5),
                       fontsize=10,
                       title="Map Legend",
                       frameon=True)

    def update_visualization(self, state, reward=0, actions=None):
        self.reward_history.append(reward)

        if actions:
            if not hasattr(self, 'action_history'):
                self.action_history = []
            self.action_history.append(actions)
        self.update_display(state, reward, actions)
        plt.pause(0.1)

    def update_display(self, state, reward, actions=None):
        for marker in self.robot_markers:
            marker.remove()
        self.robot_markers = []

        self.time_text.set_text(f'Time Step: {state["time_step"]}')

        self.reward_text.set_text(f'Total Reward: {reward}')

        for i, robot in enumerate(state['robots']):
            row, col, carrying = robot[0] - 1, robot[1] - 1, robot[2]

            # Draw the robot circle
            robot_circle = Circle((col, row), 0.3, color=self.colors['robot'],
                                  alpha=0.7, zorder=3)
            self.ax.add_patch(robot_circle)
            self.robot_markers.append(robot_circle)

            # Add robot ID text
            robot_text = self.ax.text(col, row, f'R{i}',
                                      ha='center', va='center', color='white',
                                      fontsize=8, zorder=4)
            self.robot_markers.append(robot_text)

            # Add movement direction indicator if actions are provided
            if actions and i < len(actions):
                move_direction = actions[i][0]  # First element is the movement direction

                # Define arrow endpoints based on direction
                dx, dy = 0, 0
                if move_direction == 'U':
                    dx, dy = 0, -0.5
                elif move_direction == 'D':
                    dx, dy = 0, 0.5
                elif move_direction == 'L':
                    dx, dy = -0.5, 0
                elif move_direction == 'R':
                    dx, dy = 0.5, 0

                # Only draw arrow if robot is actually moving (not staying still)
                if move_direction != 'S':
                    arrow = self.ax.arrow(col, row, dx, dy, head_width=0.2,
                                          head_length=0.2, fc='yellow', ec='black',
                                          zorder=5, alpha=0.8)
                    self.robot_markers.append(arrow)

            # Add carried package indicator if carrying
            if carrying > 0:
                carried_text = self.ax.text(col, row - 0.4, f'P{carrying}',
                                            ha='center', va='center', color='black',
                                            fontsize=7, zorder=4)
                self.robot_markers.append(carried_text)

        # Process current packages
        self.process_packages(state)

        # Refresh the canvas
        self.fig.canvas.draw()

    def process_packages(self, state):
        """Process package visualization with respect to time"""
        # Get current time step
        current_time = state['time_step']

        # Get packages from the environment's internal state
        env_packages = self.env.packages

        # First, hide any package markers that shouldn't be visible
        # (those with start time > current_time and not yet in transit/delivered)
        for pkg_id in list(self.package_markers.keys()):
            pkg = next((p for p in env_packages if p.package_id == pkg_id), None)
            if pkg and pkg.start_time > current_time and pkg.status == 'None':
                # Remove the visual elements if they exist
                marker = self.package_markers[pkg_id]
                marker['pickup'].remove()
                marker['target'].remove()
                marker['pickup_text'].remove()
                marker['target_text'].remove()
                del self.package_markers[pkg_id]

        # Process only packages that should be visible now
        for pkg in env_packages:
            pkg_id = pkg.package_id

            # Skip packages that haven't appeared yet
            if pkg.start_time > current_time or pkg.status == 'delivered':
                continue

            start_row, start_col = pkg.start[0], pkg.start[1]
            target_row, target_col = pkg.target[0], pkg.target[1]
            status = pkg.status  # 'None', 'waiting', 'in_transit', or 'delivered'

            # Create marker if it doesn't exist
            if pkg_id not in self.package_markers:
                # Pickup location marker
                pickup_marker = Rectangle((start_col - 0.4, start_row - 0.4), 0.8, 0.8,
                                          color=self.colors['package_waiting'], alpha=0.5, zorder=2)
                self.ax.add_patch(pickup_marker)

                # Target location marker
                target_marker = Rectangle((target_col - 0.4, target_row - 0.4), 0.8, 0.8,
                                          color=self.colors['target'], alpha=0.3, zorder=1)
                self.ax.add_patch(target_marker)

                # Package ID at pickup
                pickup_text = self.ax.text(start_col, start_row, f'P{pkg_id}',
                                           ha='center', va='center', color='black',
                                           fontsize=7, zorder=2)

                # Package ID at target
                target_text = self.ax.text(target_col, target_row, f'T{pkg_id}',
                                           ha='center', va='center', color='black',
                                           fontsize=7, zorder=1)

                self.package_markers[pkg_id] = {
                    'pickup': pickup_marker,
                    'target': target_marker,
                    'pickup_text': pickup_text,
                    'target_text': target_text,
                    'status': status
                }

            # Update color based on status
            marker = self.package_markers[pkg_id]
            current_status = marker['status']

            if status != current_status:
                marker['status'] = status
                if status == 'in_transit':
                    marker['pickup'].set_color(self.colors['package_transit'])
                elif status == 'delivered':
                    marker['target'].set_color(self.colors['package_delivered'])
                elif status == 'waiting':
                    marker['pickup'].set_color(self.colors['package_waiting'])

    def run_animation(self, env, agents, steps=100):
        state = env.reset()
        agents.init_agents(state)

        self.package_markers = {}
        self.robot_markers = []

        done = False
        t = 0

        while not done and t < steps:
            while not self.animation_running:
                plt.pause(0.001)
                if not plt.fignum_exists(self.fig.number):
                    return {}
            actions = agents.get_actions(state)
            self.setup_plot()
            self.setup_controls()
            self.update_visualization(state, round(env.total_reward, 2), actions)

            plt.pause(self.animation_speed)

            next_state, reward, done, infos = env.step(actions)
            state = next_state
            t += 1

            if done:
                final_reward = infos.get('total_reward', env.total_reward)
                self.update_visualization(state, round(final_reward, 2), actions)

            if not plt.fignum_exists(self.fig.number):
                return {}

        return infos


def visualize_delivery(map_file='map5.txt', num_agents=5, n_packages=10, max_steps=100, seed=2025):
    env = Environment(map_file=map_file, max_time_steps=max_steps,
                      n_robots=num_agents, n_packages=n_packages,
                      seed=seed)

    agents = Agents()
    visualizer = DeliveryVisualizer(env)

    infos = visualizer.run_animation(env, agents, steps=max_steps)

    print("Simulation complete!")
    print(f"Total reward: {infos.get('total_reward', 'N/A')}")
    print(f"Total time steps: {infos.get('total_time_steps', 'N/A')}")

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize Multi-Agent Package Delivery")
    parser.add_argument("--num_agents", type=int, default=5, help="Number of agents")
    parser.add_argument("--n_packages", type=int, default=100, help="Number of packages")
    parser.add_argument("--max_steps", type=int, default=1000, help="Maximum number of steps")
    parser.add_argument("--seed", type=int, default=2025, help="Random seed")
    parser.add_argument("--map", type=str, default="map1.txt", help="Map file")

    args = parser.parse_args()
    visualize_delivery(
        map_file=args.map,
        num_agents=args.num_agents,
        n_packages=args.n_packages,
        max_steps=args.max_steps,
        seed=args.seed
    )