import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import animation
import numpy as np
from matplotlib.lines import Line2D

COLOR_OBST = "#333333"
COLOR_FREE  = "#FFFFFF"
COLOR_ROBOT = "#1f77b4"
COLOR_PK    = "#ff7f0e"

def draw_robot(ax, center_x, center_y, carrying=0, size=0.8):
    # Draw a robot with head and body
    body_w = size * 0.6
    body_h = size * 0.6
    x0 = center_x - body_w / 2
    y0 = center_y - size / 2
    # Body rectangle
    body = patches.Rectangle((x0, y0), body_w, body_h,
                             facecolor=COLOR_ROBOT, edgecolor='k', linewidth=1.5)
    ax.add_patch(body)
    # Head circle
    head_r = size * 0.2
    head_center = (center_x, y0 + body_h + head_r)
    head = patches.Circle(head_center, head_r,
                          facecolor=COLOR_ROBOT, edgecolor='k', linewidth=1.5)
    ax.add_patch(head)
    # Carrying count overlay
    if carrying:
        ax.text(center_x, y0 + body_h * 0.2, str(carrying), color='white',
                ha='center', va='center', fontsize=8)

def draw_frame(ax, grid, robots, packages):
    ax.clear()
    n, m = len(grid), len(grid[0])
    ax.set_xlim(0, m)
    ax.set_ylim(0, n)
    # draw grid lines and coordinate ticks
    ax.set_xticks(np.arange(0.5, m, 1))
    ax.set_xticklabels([str(j+1) for j in range(m)])
    ax.set_yticks(np.arange(0.5, n, 1))
    ax.set_yticklabels([str(i+1) for i in reversed(range(n))])
    ax.grid(True, color='gray', linestyle='--', linewidth=0.5)
    # draw cells
    for i in range(n):
        for j in range(m):
            c = COLOR_FREE if grid[i][j]==0 else COLOR_OBST
            rect = patches.Rectangle((j, n-1-i), 1,1, facecolor=c, edgecolor="#CCCCCC")
            ax.add_patch(rect)
    # draw package start and target with annotations
    for pkg in packages:
        pkg_id, sr, sc, tr, tc, _, _ = pkg
        # start location
        ax.add_patch(patches.Circle((sc-0.5, n-sr+0.5), .3, color=COLOR_PK, alpha=0.6))
        ax.text(sc-0.5, n-sr+0.5 + 0.3, f"{pkg_id}({sr},{sc})", color=COLOR_PK, fontsize=6, ha='center')
        # target location
        ax.scatter(tc-0.5, n-tr+0.5, marker='X', color='green', s=80)
        ax.text(tc-0.5, n-tr+0.5 - 0.3, f"{pkg_id}({tr},{tc})", color='green', fontsize=6, ha='center')
    # draw robots with custom shape
    for r in robots:
        rr, rc, carrying = r
        x = rc - 0.5
        y = n - rr + 0.5
        draw_robot(ax, x, y, carrying)
    return ax

def animate(env, agents, interval=200):
    fig, ax = plt.subplots(figsize=(6,6))
    # Legend elements
    legend_elements = [
        patches.Patch(facecolor=COLOR_OBST, edgecolor='k', label='Obstacle'),
        patches.Patch(facecolor=COLOR_FREE, edgecolor='k', label='Free Cell'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor=COLOR_ROBOT, markersize=10, label='Robot'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=COLOR_PK, markersize=10, label='Pkg Start'),
        Line2D([0], [0], marker='X', color='green', linestyle='None', markersize=10, label='Pkg Target'),
        Line2D([0], [0], marker='X', color='gray', linestyle='None', markersize=10, label='Delivered'),
    ]
    # Collect states and trajectories
    states = []
    trajectories = []
    state = env.reset()
    done = False
    states.append(state)
    # initialize robot trails
    for rr, rc, _ in state['robots']:
        x = rc - 0.5
        y = len(state['map']) - rr + 0.5
        trajectories.append([(x, y)])
    while not done:
        acts = agents.get_actions(state)
        state, _, done, _ = env.step(acts)
        states.append(state)
        for i, (rr, rc, _) in enumerate(state['robots']):
            x = rc - 0.5; y = len(state['map']) - rr + 0.5
            trajectories[i].append((x, y))
    # set up robot colors
    num_agents = len(trajectories)
    if num_agents <= 10:
        colors = plt.cm.tab10.colors[:num_agents]
    else:
        colors = plt.cm.rainbow(np.linspace(0, 1, num_agents))
    def update(k):
        st = states[k]
        grid, robots, packages, t = st['map'], st['robots'], st['packages'], st['time_step']
        draw_frame(ax, grid, robots, packages)
        # draw trails
        for i, traj in enumerate(trajectories):
            xs, ys = zip(*traj[:k+1])
            ax.plot(xs, ys, color=colors[i], linewidth=1)
        # draw package targets and delivered
        n = len(grid)
        for pkg in env.packages:
            if pkg.status == 'waiting':
                x = pkg.start[1] + 0.5; y = n - pkg.start[0] - 0.5
                ax.scatter(x, y, marker='o', color=COLOR_PK, s=80, alpha=0.6)
            elif pkg.status == 'delivered':
                x = pkg.target[1] + 0.5; y = n - pkg.target[0] - 0.5
                ax.scatter(x, y, marker='X', color='gray', s=80, alpha=0.8)
        # add legend and title
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        ax.set_title(f"Step {t}/{len(states)-1}")
        return ax
    return animation.FuncAnimation(fig, update, frames=len(states), interval=interval, blit=False, repeat=False)