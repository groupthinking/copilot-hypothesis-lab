import json
from typing import Any
from unittest.mock import patch

from hypothesis_lab.telemetry import log_telemetry, main, parse_labels


def test_parse_labels_valid_dict_list() -> None:
    labels_raw = json.dumps([{"name": "hyp:h1"}, {"name": "arm:treatment"}, {"name": "bug"}])
    hyp, arm = parse_labels(labels_raw)
    assert hyp == "h1"
    assert arm == "treatment"


def test_parse_labels_valid_str_list() -> None:
    labels_raw = json.dumps(["hyp:h2", "arm:control"])
    hyp, arm = parse_labels(labels_raw)
    assert hyp == "h2"
    assert arm == "control"


def test_parse_labels_missing_tags() -> None:
    labels_raw = json.dumps(["bug", "enhancement"])
    hyp, arm = parse_labels(labels_raw)
    assert hyp is None
    assert arm is None


def test_parse_labels_invalid_json() -> None:
    hyp, arm = parse_labels("invalid json")
    assert hyp is None
    assert arm is None


def test_telemetry_main_missing_labels(capsys: Any) -> None:
    with patch.dict("os.environ", {}, clear=True):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0
    captured = capsys.readouterr()
    assert "Skipping" in captured.out


def test_telemetry_log_telemetry(tmp_path: Any) -> None:
    history_file = tmp_path / "metrics" / "history.jsonl"
    labels_raw = json.dumps([{"name": "hyp:h1"}, {"name": "arm:treatment"}])

    event = log_telemetry(
        labels_raw=labels_raw,
        pr_number_str="123",
        pr_merged_str="true",
        pr_author="alice",
        history_path=str(history_file),
    )

    assert event is not None
    assert event["pr_number"] == 123
    assert event["hypothesis"] == "h1"
    assert event["arm"] == "treatment"
    assert event["accepted"] is True
    assert event["author"] == "alice"

    content = history_file.read_text(encoding="utf-8")
    assert "123" in content
    assert "h1" in content
