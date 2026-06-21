"""
Anti-Gravity Layer — Exploration component of the retrieval system.

The AntiGravityLayer implements the "anti-gravity" or serendipity mechanism.
It promotes documents that are semantically *distant* from the user's recent
history, countering the echo-chamber effect and injecting diversity.

Three strategies are provided:
1. Diversity re-ranking — penalise documents too close to already-seen content.
2. Entropy injection — blend random-direction vectors into the query.
3. Trend boosting — boost globally trending topics.
"""

from __future__ import annotations

import math
import random

from hypothesis_lab.retrieval.gravity import Document, _cosine_similarity


class AntiGravityLayer:
    """
    Promotes exploration by diversifying retrieval results.

    Args:
        history_vectors: Embeddings of documents the user has recently seen.
        anti_gravity_strength: Weight given to the anti-gravity penalty (0.0–1.0).
        entropy_scale: Scale of random noise injected into the query vector.
        seed: Random seed for reproducibility.
    """

    def __init__(
        self,
        history_vectors: list[list[float]] | None = None,
        anti_gravity_strength: float = 0.5,
        entropy_scale: float = 0.1,
        seed: int | None = None,
    ) -> None:
        if not 0.0 <= anti_gravity_strength <= 1.0:
            raise ValueError("anti_gravity_strength must be between 0.0 and 1.0")
        self.history_vectors: list[list[float]] = history_vectors or []
        self.anti_gravity_strength = anti_gravity_strength
        self.entropy_scale = entropy_scale
        self._rng = random.Random(seed)

    def _max_history_similarity(self, document: Document) -> float:
        """Return the maximum cosine similarity to any vector in history."""
        if not self.history_vectors:
            return 0.0
        sims = [_cosine_similarity(document.vector, h) for h in self.history_vectors]
        return max(sims)

    def novelty_score(self, document: Document) -> float:
        """
        Return a novelty score for a document.

        Higher score means the document is *more different* from history
        (more anti-gravitational / exploratory).
        """
        similarity = self._max_history_similarity(document)
        # Invert: low similarity → high novelty
        return (1.0 - similarity) * self.anti_gravity_strength

    def diversity_rerank(
        self,
        candidates: list[tuple[Document, float]],
        top_k: int = 10,
    ) -> list[tuple[Document, float]]:
        """
        Re-rank candidates by combining gravity score with novelty score.

        Args:
            candidates: List of (document, gravity_score) tuples.
            top_k: Number of results to return.

        Returns:
            Re-ranked list of (document, combined_score) tuples.
        """
        reranked = []
        for doc, gravity_score in candidates:
            novelty = self.novelty_score(doc)
            combined = gravity_score + novelty
            reranked.append((doc, combined))
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:top_k]

    def inject_entropy(self, query_vector: list[float]) -> list[float]:
        """
        Inject random noise into a query vector to broaden the search.

        This forces the retrieval model to compare the intent against data
        that isn't naturally clustered near the user profile.

        Args:
            query_vector: Original query embedding.

        Returns:
            Perturbed query vector with entropy injected.
        """
        noise = [
            self._rng.gauss(0.0, self.entropy_scale) for _ in query_vector
        ]
        perturbed = [q + n for q, n in zip(query_vector, noise, strict=True)]
        # Renormalise to unit length
        norm = math.sqrt(sum(x * x for x in perturbed))
        if norm == 0.0:
            return query_vector
        return [x / norm for x in perturbed]

    def add_to_history(self, vector: list[float]) -> None:
        """Add a vector to the seen-document history."""
        self.history_vectors.append(vector)

    def clear_history(self) -> None:
        """Reset the history (e.g., at the start of a new session)."""
        self.history_vectors.clear()
