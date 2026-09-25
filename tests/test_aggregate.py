import json
from typing import Any

from hypothesis_lab.aggregate import calculate_stats, update_results_md


def test_calculate_stats_no_file(tmp_path: Any) -> None:
    non_existent = str(tmp_path / "missing.jsonl")
    stats = calculate_stats(non_existent)
    assert stats["h1"]["total_prs"] == 0
    assert stats["h1"]["status"] == "Pending"
    assert stats["h1"]["delta"] == 0.0


def test_calculate_stats_running(tmp_path: Any) -> None:
    history_file = tmp_path / "history.jsonl"
    events = [
        {"hypothesis": "h1", "arm": "treatment", "accepted": True},
        {"hypothesis": "h1", "arm": "control", "accepted": False},
    ]
    with open(history_file, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    stats = calculate_stats(str(history_file))
    assert stats["h1"]["total_prs"] == 2
    assert stats["h1"]["treatment_count"] == 1
    assert stats["h1"]["control_count"] == 1
    assert stats["h1"]["treatment_rate"] == 1.0
    assert stats["h1"]["control_rate"] == 0.0
    assert stats["h1"]["delta"] == 1.0
    assert stats["h1"]["status"] == "Running"


def test_calculate_stats_falsified(tmp_path: Any) -> None:
    history_file = tmp_path / "history.jsonl"
    # 20 PRs total, delta < 0.10
    events = []
    for _ in range(10):
        events.append({"hypothesis": "h1", "arm": "treatment", "accepted": False})
        events.append({"hypothesis": "h1", "arm": "control", "accepted": False})

    with open(history_file, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    stats = calculate_stats(str(history_file))
    assert stats["h1"]["total_prs"] == 20
    assert stats["h1"]["delta"] == 0.0
    assert stats["h1"]["status"] == "Falsified (Early Boundary)"


def test_calculate_stats_validated(tmp_path: Any) -> None:
    history_file = tmp_path / "history.jsonl"
    # 50 PRs total, delta >= 0.30
    events = []
    for _ in range(25):
        events.append({"hypothesis": "h1", "arm": "treatment", "accepted": True})
        events.append({"hypothesis": "h1", "arm": "control", "accepted": False})

    with open(history_file, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    stats = calculate_stats(str(history_file))
    assert stats["h1"]["total_prs"] == 50
    assert stats["h1"]["delta"] == 1.0
    assert stats["h1"]["status"] == "Validated"


def test_update_results_md(tmp_path: Any) -> None:
    results_file = tmp_path / "RESULTS.md"
    stats = {
        "h1": {
            "total_prs": 10,
            "treatment_count": 5,
            "control_count": 5,
            "treatment_rate": 0.8,
            "control_rate": 0.4,
            "delta": 0.4,
            "status": "Running",
        }
    }
    update_results_md(stats, results_path=str(results_file))
    content = results_file.read_text()
    assert "H1 — Memory Flywheel" in content
    assert "10 / 50" in content
    assert "40.0%" in content
