"""Tests for the retrieval engine components."""

import math

import pytest

from hypothesis_lab.retrieval.anti_gravity import AntiGravityLayer
from hypothesis_lab.retrieval.engine import RetrievalEngine, RetrievalResult
from hypothesis_lab.retrieval.gravity import Document, GravityLayer, _cosine_similarity

# ── Helpers ────────────────────────────────────────────────────────────────


def make_doc(doc_id: str, vector: list[float], content: str = "") -> Document:
    return Document(id=doc_id, content=content or doc_id, vector=vector)


# ── Cosine similarity ──────────────────────────────────────────────────────


class TestCosineSimilarity:
    def test_identical_vectors(self) -> None:
        v = [1.0, 0.0, 0.0]
        assert _cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self) -> None:
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert _cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self) -> None:
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert _cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_length_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="length mismatch"):
            _cosine_similarity([1.0], [1.0, 2.0])

    def test_zero_vector(self) -> None:
        assert _cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0


# ── GravityLayer ───────────────────────────────────────────────────────────


class TestGravityLayer:
    def test_empty_preference_raises(self) -> None:
        with pytest.raises(ValueError, match="preference_vector must not be empty"):
            GravityLayer([])

    def test_invalid_gravity_strength_raises(self) -> None:
        with pytest.raises(ValueError, match="gravity_strength"):
            GravityLayer([1.0], gravity_strength=1.5)

    def test_score_identical(self) -> None:
        layer = GravityLayer([1.0, 0.0])
        doc = make_doc("d1", [1.0, 0.0])
        assert layer.score(doc) == pytest.approx(1.0)

    def test_score_orthogonal(self) -> None:
        layer = GravityLayer([1.0, 0.0])
        doc = make_doc("d1", [0.0, 1.0])
        assert layer.score(doc) == pytest.approx(0.0)

    def test_gravity_strength_scales_score(self) -> None:
        layer = GravityLayer([1.0, 0.0], gravity_strength=0.5)
        doc = make_doc("d1", [1.0, 0.0])
        assert layer.score(doc) == pytest.approx(0.5)

    def test_rank_returns_top_k(self) -> None:
        layer = GravityLayer([1.0, 0.0])
        docs = [make_doc(f"d{i}", [float(i % 2), float((i + 1) % 2)]) for i in range(10)]
        results = layer.rank(docs, top_k=3)
        assert len(results) == 3

    def test_rank_is_sorted_descending(self) -> None:
        layer = GravityLayer([1.0, 0.0])
        docs = [
            make_doc("high", [1.0, 0.0]),
            make_doc("low", [0.0, 1.0]),
        ]
        results = layer.rank(docs)
        assert results[0][0].id == "high"
        assert results[1][0].id == "low"

    def test_update_preference(self) -> None:
        layer = GravityLayer([1.0, 0.0])
        layer.update_preference([0.0, 1.0], learning_rate=0.5)
        assert layer.preference_vector[0] == pytest.approx(0.5)
        assert layer.preference_vector[1] == pytest.approx(0.5)

    def test_update_preference_dimension_mismatch(self) -> None:
        layer = GravityLayer([1.0, 0.0])
        with pytest.raises(ValueError, match="dimension mismatch"):
            layer.update_preference([1.0])


# ── AntiGravityLayer ───────────────────────────────────────────────────────


class TestAntiGravityLayer:
    def test_invalid_anti_gravity_strength_raises(self) -> None:
        with pytest.raises(ValueError, match="anti_gravity_strength"):
            AntiGravityLayer(anti_gravity_strength=2.0)

    def test_novelty_no_history(self) -> None:
        layer = AntiGravityLayer()
        doc = make_doc("d1", [1.0, 0.0])
        # No history → max novelty (similarity=0, novelty=strength)
        assert layer.novelty_score(doc) == pytest.approx(layer.anti_gravity_strength)

    def test_novelty_identical_to_history(self) -> None:
        layer = AntiGravityLayer(history_vectors=[[1.0, 0.0]])
        doc = make_doc("d1", [1.0, 0.0])
        # Identical to history → zero novelty
        assert layer.novelty_score(doc) == pytest.approx(0.0)

    def test_diversity_rerank_returns_top_k(self) -> None:
        layer = AntiGravityLayer()
        candidates = [(make_doc(f"d{i}", [float(i), 0.0]), float(i)) for i in range(10)]
        results = layer.diversity_rerank(candidates, top_k=5)
        assert len(results) == 5

    def test_inject_entropy_changes_vector(self) -> None:
        layer = AntiGravityLayer(entropy_scale=0.5, seed=42)
        original = [1.0, 0.0, 0.0]
        perturbed = layer.inject_entropy(original)
        assert perturbed != original

    def test_inject_entropy_returns_unit_vector(self) -> None:
        layer = AntiGravityLayer(entropy_scale=0.5, seed=42)
        perturbed = layer.inject_entropy([1.0, 0.0, 0.0])
        norm = math.sqrt(sum(x * x for x in perturbed))
        assert norm == pytest.approx(1.0, abs=1e-6)

    def test_add_and_clear_history(self) -> None:
        layer = AntiGravityLayer()
        layer.add_to_history([1.0, 0.0])
        assert len(layer.history_vectors) == 1
        layer.clear_history()
        assert len(layer.history_vectors) == 0


# ── RetrievalEngine ────────────────────────────────────────────────────────


class TestRetrievalEngine:
    def _make_corpus(self) -> list[Document]:
        return [
            make_doc("d1", [1.0, 0.0], "Highly relevant document"),
            make_doc("d2", [0.0, 1.0], "Orthogonal document"),
            make_doc("d3", [0.7, 0.7], "Diagonal document"),
        ]

    def test_retrieve_returns_results(self) -> None:
        engine = RetrievalEngine([1.0, 0.0], seed=42)
        docs = self._make_corpus()
        results = engine.retrieve(docs, top_k=3)
        assert len(results) <= 3
        assert all(isinstance(r, RetrievalResult) for r in results)

    def test_retrieve_gravity_strategy(self) -> None:
        # Force gravity strategy by setting epsilon=0 after init
        engine = RetrievalEngine([1.0, 0.0], epsilon=0.0, seed=42)
        # Give "gravity" arm a high reward so it's selected
        engine.bandit.update("gravity", reward=10.0)
        engine.bandit.update("anti_gravity", reward=0.0)
        engine.bandit.update("balanced", reward=0.0)
        docs = self._make_corpus()
        results = engine.retrieve(docs)
        # With gravity strategy all novelty scores should be 0
        for r in results:
            if r.strategy == "gravity":
                assert r.novelty_score == 0.0

    def test_feedback_updates_state(self) -> None:
        engine = RetrievalEngine([1.0, 0.0], seed=42)
        docs = self._make_corpus()
        results = engine.retrieve(docs, top_k=1)
        history_before = len(engine.anti_gravity.history_vectors)
        engine.feedback(results[0], reward=1.0, engaged=True)
        assert len(engine.anti_gravity.history_vectors) > history_before

    def test_status_structure(self) -> None:
        engine = RetrievalEngine([1.0, 0.0], seed=42)
        status = engine.status()
        assert "gravity_strength" in status
        assert "anti_gravity_strength" in status
        assert "history_size" in status
        assert "bandit" in status

    def test_result_properties(self) -> None:
        engine = RetrievalEngine([1.0, 0.0], seed=42)
        docs = self._make_corpus()
        results = engine.retrieve(docs, top_k=1)
        r = results[0]
        assert r.id == r.document.id
        assert r.content == r.document.content
