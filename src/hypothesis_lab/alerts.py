import json
import os
from datetime import datetime, timedelta, timezone


def check_stagnation(history_path: str = "metrics/history.jsonl") -> bool:
    """Check if no telemetry events have been recorded in the last 72 hours."""
    if not os.path.exists(history_path):
        print("STAGNATION ALERT: No metrics history file found (0 PRs recorded).")
        return True

    latest_time = None
    count = 0
    with open(history_path, encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            count += 1
            data = json.loads(line_str)
            ts_str = data.get("timestamp")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str)
                    if latest_time is None or ts > latest_time:
                        latest_time = ts
                except ValueError:
                    pass

    if count == 0 or latest_time is None:
        print("STAGNATION ALERT: History file is empty (0 PRs recorded).")
        return True

    now = datetime.now(timezone.utc)
    if latest_time.tzinfo is None:
        latest_time = latest_time.replace(tzinfo=timezone.utc)

    diff = now - latest_time
    if diff > timedelta(hours=72):
        print(
            f"STAGNATION ALERT: No PR telemetry recorded in the last 72 hours "
            f"(last event was {latest_time.isoformat()})."
        )
        return True

    print(
        f"Activity OK: Last PR recorded at {latest_time.isoformat()} "
        f"({diff.total_seconds() / 3600:.1f} hours ago)."
    )
    return False


def check_milestones(history_path: str = "metrics/history.jsonl") -> list[int]:
    """Check if total PR count has reached milestones (10, 20, 30, 40, 50)."""
    if not os.path.exists(history_path):
        return []

    count = 0
    with open(history_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1

    milestones = [10, 20, 30, 40, 50]
    reached = [m for m in milestones if count >= m]
    if count in milestones:
        print(f"MILESTONE ALERT: Reached {count} total PRs recorded!")
    else:
        print(f"Milestone status: {count} total PRs recorded.")

    return reached


def main() -> None:
    history_path = os.getenv("HISTORY_PATH", "metrics/history.jsonl")
    check_stagnation(history_path)
    check_milestones(history_path)


if __name__ == "__main__":
    main()
