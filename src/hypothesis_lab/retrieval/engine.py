"""
RetrievalEngine — Orchestrates gravity and anti-gravity layers.

This engine implements the balanced retrieval system described in the
hypothesis lab. It uses a Multi-Armed Bandit to dynamically tune the
gravity/anti-gravity balance based on user feedback signals.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hypothesis_lab.bandit import EpsilonGreedyBandit
from hypothesis_lab.retrieval.anti_gravity import AntiGravityLayer
from hypothesis_lab.retrieval.gravity import Document, GravityLayer


@dataclass
class RetrievalResult:
    """A single result returned by the retrieval engine."""

    document: Document
    gravity_score: float
    novelty_score: float
    combined_score: float
    strategy: str  # "gravity" | "anti_gravity" | "balanced"

    @property
    def id(self) -> str:
        return self.document.id

    @property
    def content(self) -> str:
        return self.document.content


class RetrievalEngine:
    """
    Orchestrates gravity (exploitation) and anti-gravity (exploration)
    to deliver balanced, personalised yet diverse retrieval results.

    The engine uses an Epsilon-Greedy Multi-Armed Bandit to adapt the
    gravity/anti-gravity balance over time based on user engagement.

    Args:
        preference_vector: Initial user preference embedding.
        gravity_strength: Initial strength of the gravity layer (0.0–1.0).
        anti_gravity_strength: Initial strength of the anti-gravity layer (0.0–1.0).
        epsilon: Initial exploration probability for the bandit.
        seed: Random seed for reproducibility.
    """

    STRATEGIES = ["gravity", "anti_gravity", "balanced"]

    def __init__(
        self,
        preference_vector: list[float],
        gravity_strength: float = 0.8,
        anti_gravity_strength: float = 0.4,
        epsilon: float = 0.15,
        seed: int | None = None,
    ) -> None:
        self.gravity = GravityLayer(preference_vector, gravity_strength)
        self.anti_gravity = AntiGravityLayer(
            anti_gravity_strength=anti_gravity_strength, seed=seed
        )
        self.bandit = EpsilonGreedyBandit(
            arms=self.STRATEGIES, epsilon=epsilon, seed=seed
        )
        self._last_strategy: str | None = None

    def retrieve(
        self,
        documents: list[Document],
        query_vector: list[float] | None = None,
        top_k: int = 10,
    ) -> list[RetrievalResult]:
        """
        Retrieve and rank documents using the current strategy.

        The bandit selects the strategy for this round:
        - "gravity": pure exploitation (relevant to your preferences)
        - "anti_gravity": pure exploration (semantically distant, diverse)
        - "balanced": combines gravity + novelty scores

        Args:
            documents: Corpus to search.
            query_vector: Optional query vector; if None, preference vector is used.
            top_k: Number of results to return.

        Returns:
            List of RetrievalResult objects sorted by combined score.
        """
        strategy = self.bandit.select()
        self._last_strategy = strategy

        effective_query = query_vector or self.gravity.preference_vector

        if strategy == "anti_gravity":
            effective_query = self.anti_gravity.inject_entropy(effective_query)

        # Score with gravity
        gravity_layer = GravityLayer(effective_query, self.gravity.gravity_strength)
        gravity_ranked = gravity_layer.rank(documents, top_k=len(documents))

        if strategy == "gravity":
            results = gravity_ranked[:top_k]
            return [
                RetrievalResult(
                    document=doc,
                    gravity_score=score,
                    novelty_score=0.0,
                    combined_score=score,
                    strategy=strategy,
                )
                for doc, score in results
            ]

        # Apply anti-gravity re-ranking for "anti_gravity" and "balanced"
        reranked = self.anti_gravity.diversity_rerank(gravity_ranked, top_k=top_k)
        results_out = []
        for doc, combined_score in reranked:
            novelty = self.anti_gravity.novelty_score(doc)
            results_out.append(
                RetrievalResult(
                    document=doc,
                    gravity_score=combined_score - novelty,
                    novelty_score=novelty,
                    combined_score=combined_score,
                    strategy=strategy,
                )
            )
        return results_out

    def feedback(self, result: RetrievalResult, reward: float, engaged: bool = True) -> None:
        """
        Provide feedback on a result to update the bandit and preference vector.

        Args:
            result: The result the user interacted with.
            reward: Reward signal (e.g., 1.0 for positive engagement).
            engaged: Whether the user engaged positively with the result.
        """
        if self._last_strategy is not None:
            self.bandit.update(self._last_strategy, reward, success=engaged)
        if engaged:
            self.gravity.update_preference(result.document.vector)
            self.anti_gravity.add_to_history(result.document.vector)

    def status(self) -> dict[str, Any]:
        """Return the current status of the retrieval engine."""
        return {
            "gravity_strength": self.gravity.gravity_strength,
            "anti_gravity_strength": self.anti_gravity.anti_gravity_strength,
            "history_size": len(self.anti_gravity.history_vectors),
            "bandit": self.bandit.summary(),
            "last_strategy": self._last_strategy,
        }
