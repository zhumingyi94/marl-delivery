import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.colors import ListedColormap

class DeliveryVisualizer:
    def __init__(self, env):
        self.env = env
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.states_history = []
        self.actions_history = []
        
        # Colors for visualization
        self.colors = {
            'obstacle': '#333333',  # Dark grey
            'free': '#FFFFFF',      # White
            'robot': '#3498DB',     # Blue
            'package_start': '#E74C3C',  # Red
            'package_target': '#2ECC71',  # Green
            'carrying': '#9B59B6',  # Purple for robot carrying package
        }

    def record_state(self, state, actions=None):
        """Record a state and actions for later visualization"""
        self.states_history.append(state.copy())
        if actions:
            self.actions_history.append(actions.copy())

    def plot_state(self, state):
        """Plot a single state of the environment"""
        self.ax.clear()
        
        # Plot the grid
        grid_display = np.array(self.env.grid).copy()
        cmap = ListedColormap([self.colors['free'], self.colors['obstacle']])
        self.ax.imshow(grid_display, cmap=cmap)
        
        # Plot packages
        for pkg in state.get('packages', []):
            pkg_id, start_r, start_c, target_r, target_c, start_time, deadline = pkg
            
            # Only show packages that have appeared
            if start_time <= state['time_step']:
                # Plot start position
                self.ax.plot(start_c-1, start_r-1, 'o', color=self.colors['package_start'], 
                         markersize=10, label=f'Package {pkg_id} Start')
                
                # Plot target position
                self.ax.plot(target_c-1, target_r-1, '*', color=self.colors['package_target'], 
                         markersize=10, label=f'Package {pkg_id} Target')
                
                # Add text for package ID and deadline
                self.ax.text(start_c-1, start_r-1-0.3, f"{pkg_id}", fontsize=9, ha='center')
                self.ax.text(target_c-1, target_r-1-0.3, f"{pkg_id}", fontsize=9, ha='center')
        
        # Plot robots
        for i, (r, c, carrying) in enumerate(state['robots']):
            color = self.colors['carrying'] if carrying > 0 else self.colors['robot']
            self.ax.plot(c-1, r-1, 's', color=color, markersize=15, label=f'Robot {i}')
            
            # Display robot ID and carried package (if any)
            if carrying > 0:
                self.ax.text(c-1, r-1, f"R{i}:{carrying}", fontsize=9, ha='center', color='white')
            else:
                self.ax.text(c-1, r-1, f"R{i}", fontsize=9, ha='center', color='white')
        
        # Set grid lines
        self.ax.grid(True, which='both', color='lightgrey', linewidth=0.5)
        self.ax.set_xticks(np.arange(-0.5, self.env.n_cols, 1))
        self.ax.set_yticks(np.arange(-0.5, self.env.n_rows, 1))
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])
        
        # Add title with time step
        self.ax.set_title(f'Time Step: {state["time_step"]}')
        
        plt.tight_layout()
    
    def animate(self):
        """Create animation from recorded states"""
        if not self.states_history:
            print("No states recorded. Call record_state() first.")
            return None
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        def update(frame):
            ax.clear()
            state = self.states_history[frame]
            
            # Plot the grid
            grid_display = np.array(self.env.grid).copy()
            cmap = ListedColormap([self.colors['free'], self.colors['obstacle']])
            ax.imshow(grid_display, cmap=cmap)
            
            # Plot packages
            for pkg in state.get('packages', []):
                pkg_id, start_r, start_c, target_r, target_c, start_time, deadline = pkg
                
                if start_time <= state['time_step']:
                    # Plot start position
                    ax.plot(start_c-1, start_r-1, 'o', color=self.colors['package_start'], 
                             markersize=10)
                    
                    # Plot target position
                    ax.plot(target_c-1, target_r-1, '*', color=self.colors['package_target'], 
                             markersize=10)
                    
                    # Add text for package ID and deadline
                    ax.text(start_c-1, start_r-1-0.3, f"{pkg_id}:{deadline}", fontsize=8, ha='center')
                    ax.text(target_c-1, target_r-1-0.3, f"{pkg_id}", fontsize=8, ha='center')
            
            # Plot robots
            for i, (r, c, carrying) in enumerate(state['robots']):
                color = self.colors['carrying'] if carrying > 0 else self.colors['robot']
                ax.plot(c-1, r-1, 's', color=color, markersize=15)
                
                if carrying > 0:
                    ax.text(c-1, r-1, f"R{i}:{carrying}", fontsize=9, ha='center', color='white')
                else:
                    ax.text(c-1, r-1, f"R{i}", fontsize=9, ha='center', color='white')
            
            # Show actions if available
            if frame < len(self.actions_history):
                actions_text = ', '.join([f"R{i}:{move},{pkg}" for i, (move, pkg) in enumerate(self.actions_history[frame])])
                ax.set_xlabel(f"Actions: {actions_text}")
            
            # Set grid lines
            ax.grid(True, which='both', color='lightgrey', linewidth=0.5)
            ax.set_xticks(np.arange(-0.5, self.env.n_cols, 1))
            ax.set_yticks(np.arange(-0.5, self.env.n_rows, 1))
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            
            # Title with time step
            ax.set_title(f'Time Step: {state["time_step"]}')
            
            return ax,
        
        ani = animation.FuncAnimation(fig, update, frames=len(self.states_history), 
                                      interval=500, blit=False)
        
        plt.tight_layout()
        return ani
    
    def save_animation(self, filename="delivery_animation.gif"):
        """Save the animation as a GIF file"""
        ani = self.animate()
        if ani:
            ani.save(filename, writer='pillow', fps=2)
            print(f"Animation saved as {filename}")