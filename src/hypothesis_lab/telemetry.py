import json
import os
import sys
from datetime import datetime, timezone
from typing import Any


def parse_labels(labels_raw: str | None) -> tuple[str | None, str | None]:
    """Parse PR labels to extract hypothesis and arm tags."""
    if not labels_raw:
        return None, None

    try:
        data: Any = json.loads(labels_raw)
    except json.JSONDecodeError:
        return None, None

    if not isinstance(data, list):
        return None, None

    labels: list[str] = []
    for item in data:
        if isinstance(item, dict) and "name" in item:
            labels.append(str(item["name"]))
        elif isinstance(item, str):
            labels.append(item)

    hypothesis = next(
        (label.split(":", 1)[1] for label in labels if label.startswith("hyp:")), None
    )
    arm = next(
        (label.split(":", 1)[1] for label in labels if label.startswith("arm:")), None
    )
    return hypothesis, arm


def log_telemetry(
    labels_raw: str | None,
    pr_number_str: str | None,
    pr_merged_str: str | None,
    pr_author: str | None,
    history_path: str = "metrics/history.jsonl",
) -> dict[str, Any] | None:
    """Extract PR metadata and append event to the history log."""
    hypothesis, arm = parse_labels(labels_raw)

    if not hypothesis or not arm:
        print("PR not tagged with experiment labels (hyp:, arm:<treatment|control>). Skipping.")
        return None

    pr_number = int(pr_number_str) if pr_number_str and pr_number_str.isdigit() else 0

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pr_number": pr_number,
        "hypothesis": hypothesis,
        "arm": arm,  # "treatment" or "control"
        "accepted": pr_merged_str == "true",
        "author": pr_author or "",
    }

    dir_name = os.path.dirname(history_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    print(f"Logged event: {event}")
    return event


def main() -> None:
    event = log_telemetry(
        labels_raw=os.getenv("PR_LABELS"),
        pr_number_str=os.getenv("PR_NUMBER"),
        pr_merged_str=os.getenv("PR_MERGED"),
        pr_author=os.getenv("PR_AUTHOR"),
        history_path=os.getenv("HISTORY_PATH", "metrics/history.jsonl"),
    )
    if event is None:
        sys.exit(0)


if __name__ == "__main__":
    main()
