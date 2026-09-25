import json
from datetime import datetime, timedelta, timezone
from typing import Any

from hypothesis_lab.alerts import check_milestones, check_stagnation


def test_check_stagnation_no_file(tmp_path: Any) -> None:
    path = str(tmp_path / "non_existent.jsonl")
    assert check_stagnation(path) is True


def test_check_stagnation_recent_event(tmp_path: Any) -> None:
    history_file = tmp_path / "history.jsonl"
    recent_time = datetime.now(timezone.utc).isoformat()
    with open(history_file, "w") as f:
        f.write(json.dumps({"timestamp": recent_time}) + "\n")

    assert check_stagnation(str(history_file)) is False


def test_check_stagnation_old_event(tmp_path: Any) -> None:
    history_file = tmp_path / "history.jsonl"
    old_time = (datetime.now(timezone.utc) - timedelta(hours=80)).isoformat()
    with open(history_file, "w") as f:
        f.write(json.dumps({"timestamp": old_time}) + "\n")

    assert check_stagnation(str(history_file)) is True


def test_check_milestones(tmp_path: Any) -> None:
    history_file = tmp_path / "history.jsonl"
    with open(history_file, "w") as f:
        for i in range(10):
            f.write(json.dumps({"pr_number": i}) + "\n")

    reached = check_milestones(str(history_file))
    assert 10 in reached
