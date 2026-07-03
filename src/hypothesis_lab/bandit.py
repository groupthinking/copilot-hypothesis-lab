"""
Multi-Armed Bandit implementations for exploration/exploitation trade-off.

These algorithms balance between:
- Exploitation (gravity): choosing the option known to give good results
- Exploration (anti-gravity): trying new options to discover better ones
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any


@dataclass
class ArmStats:
    """Statistics for a single bandit arm."""

    name: str
    successes: int = 0
    failures: int = 0
    total_reward: float = 0.0
    pulls: int = 0

    @property
    def mean_reward(self) -> float:
        """Average reward for this arm."""
        return self.total_reward / self.pulls if self.pulls > 0 else 0.0

    @property
    def alpha(self) -> float:
        """Beta distribution alpha parameter (successes + 1)."""
        return self.successes + 1.0

    @property
    def beta(self) -> float:
        """Beta distribution beta parameter (failures + 1)."""
        return self.failures + 1.0


class EpsilonGreedyBandit:
    """
    Epsilon-Greedy Multi-Armed Bandit.

    With probability epsilon, explore a random arm (anti-gravity).
    With probability 1-epsilon, exploit the best known arm (gravity).

    Args:
        arms: List of arm names to choose from.
        epsilon: Exploration probability (0.0 = pure exploitation, 1.0 = pure exploration).
        epsilon_decay: Factor to reduce epsilon over time (simulated annealing).
        min_epsilon: Minimum epsilon after decay.
        seed: Random seed for reproducibility.
    """

    def __init__(
        self,
        arms: list[str],
        epsilon: float = 0.15,
        epsilon_decay: float = 0.995,
        min_epsilon: float = 0.01,
        seed: int | None = None,
    ) -> None:
        if not arms:
            raise ValueError("Must provide at least one arm")
        if not 0.0 <= epsilon <= 1.0:
            raise ValueError("epsilon must be between 0.0 and 1.0")
        if not 0.0 <= epsilon_decay <= 1.0:
            raise ValueError("epsilon_decay must be between 0.0 and 1.0")
        if not 0.0 <= min_epsilon <= 1.0:
            raise ValueError("min_epsilon must be between 0.0 and 1.0")
        if min_epsilon > epsilon:
            raise ValueError("min_epsilon must be less than or equal to epsilon")

        self._rng = random.Random(seed)
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.stats: dict[str, ArmStats] = {name: ArmStats(name=name) for name in arms}
        self.step_count = 0

    def select(self) -> str:
        """Select an arm using epsilon-greedy strategy."""
        self.step_count += 1
        if self._rng.random() < self.epsilon:
            # Exploration: pick any arm randomly (anti-gravity)
            return self._rng.choice(list(self.stats.keys()))
        # Exploitation: pick the arm with highest mean reward (gravity)
        return max(self.stats, key=lambda arm: self.stats[arm].mean_reward)

    def update(self, arm: str, reward: float, success: bool = True) -> None:
        """Update the arm statistics after receiving a reward."""
        if arm not in self.stats:
            raise ValueError(f"Unknown arm: {arm!r}")
        stats = self.stats[arm]
        stats.pulls += 1
        stats.total_reward += reward
        if success:
            stats.successes += 1
        else:
            stats.failures += 1
        # Decay epsilon toward minimum
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    @property
    def exploration_ratio(self) -> float:
        """Current probability of exploration (anti-gravity strength)."""
        return self.epsilon

    def summary(self) -> dict[str, Any]:
        """Return a summary of bandit statistics."""
        return {
            "step": self.step_count,
            "epsilon": round(self.epsilon, 4),
            "arms": {
                name: {
                    "pulls": s.pulls,
                    "mean_reward": round(s.mean_reward, 4),
                    "successes": s.successes,
                    "failures": s.failures,
                }
                for name, s in self.stats.items()
            },
        }


class ThompsonSamplingBandit:
    """
    Thompson Sampling Multi-Armed Bandit using Beta distributions.

    More principled Bayesian approach to the exploration/exploitation trade-off.
    Each arm's reward probability is modelled with a Beta(alpha, beta) prior.
    At each step, a sample is drawn from each arm's posterior and the arm
    with the highest sample is chosen.

    Args:
        arms: List of arm names to choose from.
        seed: Random seed for reproducibility.
    """

    def __init__(self, arms: list[str], seed: int | None = None) -> None:
        if not arms:
            raise ValueError("Must provide at least one arm")
        self._rng = random.Random(seed)
        self.stats: dict[str, ArmStats] = {name: ArmStats(name=name) for name in arms}
        self.step_count = 0

    def _beta_sample(self, alpha: float, beta: float) -> float:
        """Sample from Beta(alpha, beta) distribution."""
        # Use the relation between Beta and Gamma distributions
        x = self._rng.gammavariate(alpha, 1.0)
        y = self._rng.gammavariate(beta, 1.0)
        return x / (x + y)

    def select(self) -> str:
        """Select an arm by Thompson Sampling."""
        self.step_count += 1
        samples = {
            name: self._beta_sample(s.alpha, s.beta)
            for name, s in self.stats.items()
        }
        return max(samples, key=lambda arm: samples[arm])

    def update(self, arm: str, reward: float, success: bool = True) -> None:
        """Update the arm statistics after receiving a reward."""
        if arm not in self.stats:
            raise ValueError(f"Unknown arm: {arm!r}")
        stats = self.stats[arm]
        stats.pulls += 1
        stats.total_reward += reward
        if success:
            stats.successes += 1
        else:
            stats.failures += 1

    @property
    def exploration_ratio(self) -> float:
        """
        Estimated exploration ratio based on arm uncertainty.

        Arms with fewer pulls have higher uncertainty (more exploration).
        """
        total_pulls = sum(s.pulls for s in self.stats.values())
        if total_pulls == 0:
            return 1.0
        # Entropy-based exploration measure
        arm_count = len(self.stats)
        if arm_count < 2:
            return 0.0
        entropy = 0.0
        for s in self.stats.values():
            p = s.pulls / total_pulls if total_pulls > 0 else 1.0 / arm_count
            if p > 0:
                entropy -= p * math.log(p)
        max_entropy = math.log(arm_count)
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def summary(self) -> dict[str, Any]:
        """Return a summary of bandit statistics."""
        return {
            "step": self.step_count,
            "exploration_ratio": round(self.exploration_ratio, 4),
            "arms": {
                name: {
                    "pulls": s.pulls,
                    "mean_reward": round(s.mean_reward, 4),
                    "alpha": round(s.alpha, 2),
                    "beta": round(s.beta, 2),
                }
                for name, s in self.stats.items()
            },
        }
