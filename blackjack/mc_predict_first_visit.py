from __future__ import annotations

from collections import defaultdict
from typing import List, Tuple
from typing import Tuple, Dict, Callable
import numpy as np


from gym.envs.toy_text import BlackjackEnv

from blackjack.plotting import plot_value_function


State: Tuple[int, bool, int]
Action: bool
Reward: float
Actions: np.ndarray
StateValue: Dict[State, float]
ActionValue: Dict[State, np.ndarray]
Policy: Callable[[State], Actions]
DeterministicPolicy: Callable[[State], Action]

def gen_episode_data(policy: DeterministicPolicy, env: BlackjackEnv) -> List[Tuple[State, Action, Reward]]:
    episode_history = []
    state = env.reset()
    done = False
    while not done:
        action = policy(state)
        next_state, reward, done, _ = env.step(action)
        episode_history.append((state, action, reward))
        state = next_state
    return episode_history


def mc_prediction_first_visit(policy: DeterministicPolicy, env: BlackjackEnv,
                              num_episodes, discount_factor=1.0) -> StateValue:
    returns_sum = defaultdict(float)
    returns_count = defaultdict(float)

    for episode_i in range(1, num_episodes + 1):
        episode_history = gen_episode_data(policy, env)

        episodes_seen = set()
        G = 0
        for t in range(len(episode_history) - 1, -1, -1):
            s, a, r = episode_history[t]
            G = discount_factor * G + r
            if s in episodes_seen:
                returns_sum[s] += G
                returns_count[s] += 1.0
            else:
                episodes_seen.add(s)

    V = {s: returns_sum[s] / returns_count[s] for s in returns_sum.keys()}
    return V

def fixed_policy(observation):
    """
    sticks if the player score is >= 20 and hits otherwise.
    """
    score, dealer_score, usable_ace = observation
    return 0 if score >= 20 else 1

if __name__ == "__main__":
    env = BlackjackEnv()
    V = mc_prediction_first_visit(fixed_policy, env, num_episodes=1000)
    plot_value_function(V, title="10,000 Steps")

    # V_500k = mc_prediction(sample_policy, env, num_episodes=50000)
    # plotting.plot_value_function(V_500k, title="500,000 Steps")
