"""
Gravity Layer — Exploitation component of the retrieval system.

The GravityLayer represents the "gravitational pull" toward known interests.
It scores documents based on cosine similarity to the user's preference vector,
implementing the exploitation side of the exploration/exploitation trade-off.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """A document in the retrieval corpus."""

    id: str
    content: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b):
        raise ValueError(f"Vector length mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class GravityLayer:
    """
    Scores and ranks documents by relevance to the user's preference vector.

    This is the "gravity" component: it tightens the focus of retrieval
    around what the user has explicitly signalled they like.

    Args:
        preference_vector: The user's current interest embedding.
        gravity_strength: Weight given to gravity scores (0.0–1.0).
    """

    def __init__(
        self,
        preference_vector: list[float],
        gravity_strength: float = 1.0,
    ) -> None:
        if not preference_vector:
            raise ValueError("preference_vector must not be empty")
        if not 0.0 <= gravity_strength <= 1.0:
            raise ValueError("gravity_strength must be between 0.0 and 1.0")
        self.preference_vector = preference_vector
        self.gravity_strength = gravity_strength

    def score(self, document: Document) -> float:
        """Return the gravity score for a document."""
        similarity = _cosine_similarity(document.vector, self.preference_vector)
        return similarity * self.gravity_strength

    def rank(self, documents: list[Document], top_k: int = 10) -> list[tuple[Document, float]]:
        """
        Rank documents by gravity score and return the top-k.

        Returns:
            List of (document, gravity_score) tuples, sorted descending.
        """
        scored = [(doc, self.score(doc)) for doc in documents]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def update_preference(self, feedback_vector: list[float], learning_rate: float = 0.1) -> None:
        """
        Update the preference vector based on user feedback.

        Implements a simple exponential moving average to shift the
        preference vector toward the feedback signal.

        Args:
            feedback_vector: Embedding of the document the user engaged with.
            learning_rate: Step size for the update (0.0–1.0).
        """
        if len(feedback_vector) != len(self.preference_vector):
            raise ValueError("feedback_vector dimension mismatch")
        self.preference_vector = [
            (1 - learning_rate) * p + learning_rate * f
            for p, f in zip(self.preference_vector, feedback_vector, strict=True)
        ]
