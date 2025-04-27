import sys

from env import Environment
from agent_tad import Agents_TAD
from greedyagent import GreedyAgents
from greedyagent_optimal import GreedyAgentsOptimal
# from greedyagent import GreedyAgents as Agents
from visualization import animate
import matplotlib.pyplot as plt
import numpy as np

import numpy as np

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Agent Reinforcement Learning for Delivery")
    parser.add_argument("--num_agents", type=int, default=5, help="Number of agents")
    parser.add_argument("--n_packages", type=int, default=10, help="Number of packages")
    parser.add_argument("--max_steps", type=int, default=100, help="Maximum number of steps per episode")
    parser.add_argument("--seed", type=int, default=2025, help="Random seed for reproducibility")
    parser.add_argument("--max_time_steps", type=int, default=1000, help="Maximum time steps for the environment")
    parser.add_argument("--map", type=str, default="map5.txt", help="Map name")

    args = parser.parse_args()
    np.random.seed(args.seed)

    env = Environment(map_file=args.map, max_time_steps=args.max_time_steps,
                      n_robots=args.num_agents, n_packages=args.n_packages,
                      seed=args.seed)

    state = env.reset()
    agents = Agents_TAD()
    # agents = GreedyAgents()
    # agents = GreedyAgentsOptimal()
    agents.init_agents(state)
    print(state)
    done = False
    t = 0
    max_reward = 0
    sum_reward = 0
    while not done:
        env.render()
        actions = agents.get_actions(state)
        next_state, reward, done, infos = env.step(actions)
        print(infos)
        sum_reward += reward
        max_reward = max(max_reward, sum_reward)
        state = next_state

        t += 1

    print("Episode finished")
    print("Total reward:", infos['total_reward'])
    print("Total time steps:", infos['total_time_steps'])
    print(max_reward)
    print(args)
    # print(agents.finished)
    # print("Waiting_packages", agents.waiting_packages)
    # print("In_transit_packages", agents.in_transit_packages)
    # print(agents.pos_stay)

    # anim = animate(env, agents, interval=args.interval)
    # plt.show()
    # anim.save("run.mp4", fps=3)
    # sys.exit(0)
