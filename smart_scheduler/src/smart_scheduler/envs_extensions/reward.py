import numpy as np
from typing import Tuple, Dict, Any

latency_option = 5
consolidation_option = 2
# latency_lower = 0.75
# latency_upper = 2
# consolidation_lower = 0
# consolidation_upper_bound = 0.75

def _reward(
    self, *, num_moves: int,
    num_overloaded: int,
    users_distances: np.array = None) -> Tuple[
        float, Dict[str, Any]]:
    if num_overloaded > 0:
        reward_illegal = _reward_illegal(self, num_overloaded)
        return reward_illegal, {
            "reward_move": 0,
            "reward_illegal": reward_illegal,
            "reward_consolidation": 0,
            "reward_variance": 0,
            "reward_latency": 0
            }


    rewards_consolidation = {
        # 1: _reward_consolidation_1(self),
        2: _reward_consolidation_2(self)
    }
    reward_move = _reward_move(self, num_moves)
    reward_variance = _reward_variance(self)
    reward_consolidation = rewards_consolidation[consolidation_option]
    reward_total = reward_consolidation +\
        reward_move + reward_variance
    rewards = {
        "reward_move": reward_move,
        "reward_illegal": 0,
        "reward_consolidation": reward_consolidation,
        "reward_variance": reward_variance
    }
    # rewards.update({'latency_rewards' : rewards_latency})
    # rewards.update({'consolidation_rewards' : rewards_consolidation})
    return reward_total, rewards

def rescale(values, old_min = 0, old_max = 1, new_min = 0, new_max = 100):
    output = []

    for v in values:
        new_v = (new_max - new_min) / (old_max - old_min) * (v - old_min) + new_min
        output.append(new_v)

    return np.array(output)


def _reward_consolidation_2(self):
    """reward for the num_consolidated
    """
    consolidation_factor = self.num_consolidated/self.num_nodes
    reward_scaled = rescale(
        values=[consolidation_factor],
        old_min=self.consolidation_lower, 
        old_max=self.consolidation_upper,
        new_min=0, new_max=1)[0]
    reward = self.penalty_consolidated * reward_scaled
    # if reward > 10000000000000:
    #     a = 5
    return reward

# ------------- consolidatino rewards ---------------

def _reward_move(self, num_moves: int):
    """reward for the number of moves
    """
    movement_factor = num_moves/self.num_services
    reward_move = self.penalty_move * movement_factor
    return reward_move


def _reward_variance(self):
    """compute the variance reward
    """
    reward_factor = np.sum(np.var(
        self.nodes_resources_request_frac, axis=1))
    reward_variance = reward_factor * self.penalty_variance
    return reward_variance


def _reward_illegal(self, prev_num_overloaded: int):
    """reward for the number of illegal factors
    """
    nodes_overloaded_factor = prev_num_overloaded/self.num_nodes
    reward_illegal = self.penalty_illegal * nodes_overloaded_factor
    return reward_illegal
