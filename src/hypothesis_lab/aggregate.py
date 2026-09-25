import json
import os
import pathlib
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any


def calculate_stats(history_path: str = "metrics/history.jsonl") -> dict[str, Any]:
    """Calculate statistical aggregates from the append-only PR history log."""
    if not os.path.exists(history_path):
        return {
            "h1": {
                "total_prs": 0,
                "treatment_count": 0,
                "control_count": 0,
                "treatment_rate": 0.0,
                "control_rate": 0.0,
                "delta": 0.0,
                "status": "Pending",
            }
        }

    runs: dict[str, dict[str, list[bool]]] = defaultdict(lambda: {"treatment": [], "control": []})

    with open(history_path, encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            item = json.loads(line_str)
            hyp = str(item.get("hypothesis", "")).lower()
            arm = str(item.get("arm", "")).lower()
            if arm in ("treatment", "control"):
                runs[hyp][arm].append(bool(item.get("accepted", False)))

    h1 = runs.get("h1", {"treatment": [], "control": []})
    t_acc = sum(h1["treatment"]) / len(h1["treatment"]) if h1["treatment"] else 0.0
    c_acc = sum(h1["control"]) / len(h1["control"]) if h1["control"] else 0.0
    delta = t_acc - c_acc
    total = len(h1["treatment"]) + len(h1["control"])

    # Falsification check: Delta < 10% after 20+ PRs
    status = "Running"
    if total == 0:
        status = "Pending"
    elif total >= 20 and delta < 0.10:
        status = "Falsified (Early Boundary)"
    elif total >= 50 and delta >= 0.30:
        status = "Validated"

    return {
        "h1": {
            "total_prs": total,
            "treatment_count": len(h1["treatment"]),
            "control_count": len(h1["control"]),
            "treatment_rate": round(t_acc, 3),
            "control_rate": round(c_acc, 3),
            "delta": round(delta, 3),
            "status": status,
        }
    }


def update_results_md(stats: dict[str, Any], results_path: str = "RESULTS.md") -> None:
    """Update RESULTS.md with latest hypothesis benchmarks."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    h1 = stats.get("h1", {})

    total_prs = h1.get("total_prs", 0)
    delta_val = h1.get("delta", 0.0)
    delta_str = f"{delta_val * 100:.1f}%" if total_prs > 0 else "—"
    status = h1.get("status", "Pending")

    status_icon = "🟡"
    if "Falsified" in status:
        status_icon = "🔴"
    elif "Validated" in status:
        status_icon = "🟢"

    t_rate_pct = round(h1.get("treatment_rate", 0.0) * 100, 1)
    c_rate_pct = round(h1.get("control_rate", 0.0) * 100, 1)

    h1_summary_line = (
        f"| H1 — Memory Flywheel | {status_icon} {status} | "
        f"{total_prs} / 50 | {delta_str} | {status} |"
    )

    lines = [
        "# RESULTS.md — Live Experiment Results",
        "",
        f"> **Last updated:** {now}  ",
        "> Auto-updated by `.github/workflows/results-aggregator.yml`.",
        "",
        "---",
        "",
        "## Summary Dashboard",
        "",
        "| Hypothesis | Status | PRs Collected | Current Δ | Verdict |",
        "|------------|--------|--------------|-----------|---------|",
        h1_summary_line,
        "| H2 — MCP Swarm | 🟡 Running | 0 / 20 | — | Pending |",
        "| H3 — Spaces Density | 🟡 Running | 0 / 30 | — | Pending |",
        "",
        "---",
        "",
        "## H1 — Compounding Memory Flywheel",
        "",
        "### Acceptance Rate Over Time",
        "",
        "| Arm | PR Count | Acceptance Rate |",
        "|-----|----------|-----------------|",
        f"| Treatment (Memory ON) | {h1.get('treatment_count', 0)} | {t_rate_pct}% |",
        f"| Control (Memory OFF) | {h1.get('control_count', 0)} | {c_rate_pct}% |",
        "",
        "### H1 Verdict",
        "",
        f"> **{status}**",
        "",
        "---",
        "",
        "_This file is machine-generated. Do not edit manually._",
    ]

    pathlib.Path(results_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    stats = calculate_stats()
    os.makedirs("metrics/raw", exist_ok=True)
    with open("metrics/raw/latest.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    update_results_md(stats)
    print("Computed stats and updated metrics/raw/latest.json and RESULTS.md")


if __name__ == "__main__":
    main()
