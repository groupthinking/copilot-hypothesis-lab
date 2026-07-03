"""Tests for the Multi-Armed Bandit implementations."""

import pytest

from hypothesis_lab.bandit import ArmStats, EpsilonGreedyBandit, ThompsonSamplingBandit


class TestArmStats:
    def test_initial_state(self) -> None:
        arm = ArmStats(name="test")
        assert arm.pulls == 0
        assert arm.mean_reward == 0.0
        assert arm.alpha == 1.0
        assert arm.beta == 1.0

    def test_mean_reward(self) -> None:
        arm = ArmStats(name="test", pulls=4, total_reward=8.0)
        assert arm.mean_reward == 2.0

    def test_beta_params(self) -> None:
        arm = ArmStats(name="test", successes=3, failures=1)
        assert arm.alpha == 4.0
        assert arm.beta == 2.0


class TestEpsilonGreedyBandit:
    def test_requires_arms(self) -> None:
        with pytest.raises(ValueError, match="at least one arm"):
            EpsilonGreedyBandit(arms=[])

    def test_invalid_epsilon(self) -> None:
        with pytest.raises(ValueError, match="epsilon"):
            EpsilonGreedyBandit(arms=["a"], epsilon=1.5)

    def test_invalid_epsilon_decay(self) -> None:
        with pytest.raises(ValueError, match="epsilon_decay"):
            EpsilonGreedyBandit(arms=["a"], epsilon_decay=1.5)

    def test_invalid_min_epsilon(self) -> None:
        with pytest.raises(ValueError, match="min_epsilon"):
            EpsilonGreedyBandit(arms=["a"], min_epsilon=-0.1)

    def test_min_epsilon_greater_than_epsilon_raises(self) -> None:
        with pytest.raises(ValueError, match="less than or equal to epsilon"):
            EpsilonGreedyBandit(arms=["a"], epsilon=0.1, min_epsilon=0.2)

    def test_select_returns_valid_arm(self) -> None:
        bandit = EpsilonGreedyBandit(arms=["a", "b", "c"], seed=42)
        for _ in range(20):
            arm = bandit.select()
            assert arm in ["a", "b", "c"]

    def test_update_stats(self) -> None:
        bandit = EpsilonGreedyBandit(arms=["a", "b"], seed=42)
        bandit.update("a", reward=1.0, success=True)
        assert bandit.stats["a"].pulls == 1
        assert bandit.stats["a"].mean_reward == 1.0
        assert bandit.stats["a"].successes == 1

    def test_unknown_arm_raises(self) -> None:
        bandit = EpsilonGreedyBandit(arms=["a", "b"], seed=42)
        with pytest.raises(ValueError, match="Unknown arm"):
            bandit.update("z", reward=1.0)

    def test_epsilon_decays(self) -> None:
        bandit = EpsilonGreedyBandit(arms=["a"], epsilon=0.5, epsilon_decay=0.9, seed=42)
        initial_eps = bandit.epsilon
        bandit.update("a", reward=1.0)
        assert bandit.epsilon < initial_eps

    def test_epsilon_respects_minimum(self) -> None:
        bandit = EpsilonGreedyBandit(
            arms=["a"], epsilon=0.01, epsilon_decay=0.5, min_epsilon=0.01, seed=42
        )
        for _ in range(100):
            bandit.update("a", reward=1.0)
        assert bandit.epsilon >= 0.01

    def test_exploitation_selects_best_arm(self) -> None:
        # With epsilon=0 it always exploits
        bandit = EpsilonGreedyBandit(arms=["good", "bad"], epsilon=0.0, seed=42)
        bandit.update("good", reward=10.0)
        bandit.update("bad", reward=0.0)
        for _ in range(10):
            assert bandit.select() == "good"

    def test_summary_structure(self) -> None:
        bandit = EpsilonGreedyBandit(arms=["a", "b"], seed=42)
        bandit.select()
        bandit.update("a", reward=1.0)
        summary = bandit.summary()
        assert "step" in summary
        assert "epsilon" in summary
        assert "arms" in summary
        assert "a" in summary["arms"]


class TestThompsonSamplingBandit:
    def test_requires_arms(self) -> None:
        with pytest.raises(ValueError, match="at least one arm"):
            ThompsonSamplingBandit(arms=[])

    def test_select_returns_valid_arm(self) -> None:
        bandit = ThompsonSamplingBandit(arms=["a", "b", "c"], seed=42)
        for _ in range(20):
            arm = bandit.select()
            assert arm in ["a", "b", "c"]

    def test_update_stats(self) -> None:
        bandit = ThompsonSamplingBandit(arms=["a", "b"], seed=42)
        bandit.update("a", reward=1.0, success=True)
        assert bandit.stats["a"].pulls == 1
        assert bandit.stats["a"].successes == 1

    def test_exploration_ratio_initial(self) -> None:
        bandit = ThompsonSamplingBandit(arms=["a", "b"], seed=42)
        # With no pulls, exploration ratio should be maximum (1.0)
        assert bandit.exploration_ratio == 1.0

    def test_exploration_ratio_decreases_with_pulls(self) -> None:
        bandit = ThompsonSamplingBandit(arms=["a", "b"], seed=42)
        ratio_before = bandit.exploration_ratio
        # Pull the same arm many times — decreases entropy
        for _ in range(20):
            bandit.update("a", reward=1.0)
        ratio_after = bandit.exploration_ratio
        assert ratio_after < ratio_before

    def test_step_count(self) -> None:
        bandit = ThompsonSamplingBandit(arms=["a", "b"], seed=42)
        assert bandit.step_count == 0
        bandit.select()
        assert bandit.step_count == 1

    def test_summary_structure(self) -> None:
        bandit = ThompsonSamplingBandit(arms=["a", "b"], seed=42)
        bandit.select()
        bandit.update("a", reward=1.0)
        summary = bandit.summary()
        assert "step" in summary
        assert "exploration_ratio" in summary
        assert "arms" in summary
