"""
Hypothesis Lab — A managed AI agent system exploring gravity vs anti-gravity
in retrieval systems.

This package implements a balance between:
- Gravity (exploitation): pulling results toward your specific interests
- Anti-gravity (exploration): pushing toward serendipity and diversity

The system orchestrates Claude and Jules agents to implement Multi-Armed
Bandit exploration/exploitation trade-offs and diversity re-ranking.
"""

from hypothesis_lab.bandit import EpsilonGreedyBandit, ThompsonSamplingBandit
from hypothesis_lab.retrieval.anti_gravity import AntiGravityLayer
from hypothesis_lab.retrieval.engine import RetrievalEngine
from hypothesis_lab.retrieval.gravity import GravityLayer

__version__ = "0.1.0"
__all__ = [
    "RetrievalEngine",
    "GravityLayer",
    "AntiGravityLayer",
    "EpsilonGreedyBandit",
    "ThompsonSamplingBandit",
]
