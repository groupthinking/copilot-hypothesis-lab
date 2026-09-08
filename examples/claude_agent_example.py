"""
Claude Agent example — Hypothesis generation from retrieval results.

Requires the optional claude-agent-sdk dependency:
    pip install hypothesis-lab[claude]

Usage:
    python examples/claude_agent_example.py
"""

from __future__ import annotations

import asyncio
import math
import random

from hypothesis_lab import RetrievalEngine
from hypothesis_lab.retrieval.gravity import Document

# Check SDK availability
try:
    from hypothesis_lab.agents import ClaudeHypothesisAgent

    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False


def random_unit_vector(dim: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    v = [rng.gauss(0, 1) for _ in range(dim)]
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v]


async def main() -> None:
    if not _SDK_AVAILABLE:
        print("⚠️  claude-agent-sdk is not installed.")
        print("   Install it with: pip install hypothesis-lab[claude]")
        return

    dim = 8
    corpus = [
        Document(
            id=f"doc_{i:03d}",
            content=f"Sample document {i}",
            vector=random_unit_vector(dim, seed=i),
        )
        for i in range(10)
    ]

    engine = RetrievalEngine(
        preference_vector=corpus[0].vector,
        gravity_strength=0.8,
        anti_gravity_strength=0.4,
        epsilon=0.2,
        seed=42,
    )

    agent = ClaudeHypothesisAgent(max_turns=2)

    print("🔍 Running retrieval...")
    results = engine.retrieve(corpus, top_k=5)

    print("🤖 Asking Claude to analyse results...")
    analysis = await agent.analyse_results(results)
    print("\n--- Claude Analysis ---")
    print(analysis)

    print("\n💡 Generating hypothesis about exploration/exploitation balance...")
    hypothesis = await agent.generate_hypothesis(engine.bandit.summary())
    print("\n--- Claude Hypothesis ---")
    print(hypothesis)


if __name__ == "__main__":
    asyncio.run(main())
