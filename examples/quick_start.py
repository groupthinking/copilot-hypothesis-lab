"""
Quick start example — Gravity vs Anti-Gravity retrieval.

Demonstrates the exploration/exploitation trade-off in a simple corpus.

Usage:
    python examples/quick_start.py
"""

from __future__ import annotations

import math
import random

from hypothesis_lab import RetrievalEngine
from hypothesis_lab.retrieval.gravity import Document


def random_unit_vector(dim: int, seed: int | None = None) -> list[float]:
    """Generate a random unit vector of dimension `dim`."""
    rng = random.Random(seed)
    v = [rng.gauss(0, 1) for _ in range(dim)]
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v]


def make_corpus(size: int = 20, dim: int = 8, seed: int = 0) -> list[Document]:
    """Generate a synthetic document corpus."""
    rng = random.Random(seed)
    docs = []
    categories = ["technology", "science", "art", "history", "sports"]
    for i in range(size):
        category = categories[i % len(categories)]
        doc = Document(
            id=f"doc_{i:03d}",
            content=f"Document {i} about {category}",
            vector=random_unit_vector(dim, seed=rng.randint(0, 10_000)),
            metadata={"category": category},
        )
        docs.append(doc)
    return docs


def main() -> None:
    print("=" * 60)
    print("Hypothesis Lab — Gravity vs Anti-Gravity Demo")
    print("=" * 60)

    dim = 8
    corpus = make_corpus(size=20, dim=dim, seed=42)

    # User's initial preference: first document's direction
    pref = corpus[0].vector

    engine = RetrievalEngine(
        preference_vector=pref,
        gravity_strength=0.8,
        anti_gravity_strength=0.4,
        epsilon=0.3,
        seed=42,
    )

    print("\n🔁 Running 5 retrieval rounds with user feedback...\n")

    for round_num in range(1, 6):
        results = engine.retrieve(corpus, top_k=3)
        status = engine.status()

        print(f"Round {round_num} — Strategy: {status['last_strategy']}")
        print(f"  Epsilon (exploration): {status['bandit']['epsilon']:.3f}")
        print(f"  History size: {status['history_size']}")
        print("  Top results:")
        for r in results:
            print(
                f"    [{r.id}] {r.document.content}"
                f"  gravity={r.gravity_score:.3f}  novelty={r.novelty_score:.3f}"
            )

        # Simulate user engagement with the first result
        engine.feedback(results[0], reward=1.0, engaged=True)
        print()

    print("=" * 60)
    print("Final bandit summary:")
    for arm, stats in engine.bandit.summary()["arms"].items():
        print(f"  {arm}: pulls={stats['pulls']} mean_reward={stats['mean_reward']:.3f}")


if __name__ == "__main__":
    main()
