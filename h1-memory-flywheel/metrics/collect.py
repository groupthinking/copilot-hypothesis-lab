#!/usr/bin/env python3
"""
collect.py — H1 Memory Flywheel PR Acceptance-Rate Analyzer

Fetches PR data from the GitHub API and computes acceptance-rate metrics
for both the treatment arm (Memory ON) and control arm (Memory OFF).

Usage:
    python collect.py --repo owner/repo [--since YYYY-MM-DD] [--output path.json]

Environment:
    GITHUB_TOKEN — required
"""

import argparse
import json
import os
import sys
import pathlib
import datetime
import urllib.request
import urllib.error
from typing import Any, Optional


def github_get(path: str, token: str) -> Any:
    """Make a GET request to the GitHub API."""
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "copilot-hypothesis-lab/metrics-collector",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"GitHub API error {e.code} for {url}: {e.reason}", file=sys.stderr)
        return None


def fetch_prs(repo: str, token: str, since: Optional[str] = None) -> list[dict]:
    """Fetch all closed PRs from the repo, optionally filtered by date."""
    prs = []
    page = 1
    while True:
        path = f"/repos/{repo}/pulls?state=closed&per_page=100&page={page}"
        data = github_get(path, token)
        if not data:
            break
        if isinstance(data, dict) and "message" in data:
            print(f"API error: {data['message']}", file=sys.stderr)
            break
        for pr in data:
            if pr.get("merged_at") is None:
                continue
            if since and pr["merged_at"] < since:
                continue
            prs.append(pr)
        if len(data) < 100:
            break
        page += 1
    return prs


def get_pr_reviews(repo: str, pr_number: int, token: str) -> list[dict]:
    """Fetch reviews for a specific PR."""
    data = github_get(f"/repos/{repo}/pulls/{pr_number}/reviews", token)
    return data if isinstance(data, list) else []


def count_lessons(memory_path: str) -> int:
    """Count LESSON: blocks in MEMORY.md."""
    p = pathlib.Path(memory_path)
    if not p.exists():
        return 0
    return p.read_text().count("\nLESSON:")


def compute_acceptance_rate(prs: list[dict], token: str, repo: str) -> dict:
    """
    For each PR, determine if it was accepted without revision requests.
    Returns a dict with overall stats and per-milestone breakdown.
    """
    results = []
    for pr in prs:
        pr_number = pr["number"]
        labels = [label["name"] for label in pr.get("labels", [])]
        is_cloud_agent = "cloud-agent" in labels
        arm = (
            "treatment" if "cloud-agent" in labels and "control-arm" not in labels
            else "control" if "control-arm" in labels
            else "unknown"
        )

        if not is_cloud_agent:
            continue

        reviews = get_pr_reviews(repo, pr_number, token)
        revision_requested = any(r["state"] == "CHANGES_REQUESTED" for r in reviews)
        accepted = not revision_requested

        results.append(
            {
                "pr_number": pr_number,
                "arm": arm,
                "merged_at": pr["merged_at"],
                "accepted": accepted,
                "review_comment_count": len(
                    [r for r in reviews if r.get("body")]
                ),
            }
        )

    treatment = [r for r in results if r["arm"] == "treatment"]
    control = [r for r in results if r["arm"] == "control"]

    def rate(items: list[dict]) -> Optional[float]:
        if not items:
            return None
        return sum(1 for i in items if i["accepted"]) / len(items)

    def milestone_rate(items: list[dict], n: int) -> Optional[float]:
        subset = items[:n]
        if len(subset) < n:
            return None
        return rate(subset)

    def avg_comments(items: list[dict]) -> Optional[float]:
        if not items:
            return None
        return sum(i["review_comment_count"] for i in items) / len(items)

    output = {
        "collected_at": datetime.datetime.utcnow().isoformat() + "Z",
        "repo": repo,
        "total_prs": len(results),
        "treatment_prs": len(treatment),
        "control_prs": len(control),
        "treatment_acceptance_rate": rate(treatment),
        "control_acceptance_rate": rate(control),
        "treatment_avg_comments": avg_comments(treatment),
        "control_avg_comments": avg_comments(control),
        "lesson_count": count_lessons("h1-memory-flywheel/MEMORY.md"),
        "raw": results,
    }

    for milestone in [10, 20, 30, 40, 50]:
        t = milestone_rate(treatment, milestone)
        c = milestone_rate(control, milestone)
        output[f"treatment_rate_at_{milestone}"] = t
        output[f"control_rate_at_{milestone}"] = c

    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="H1 Memory Flywheel — PR acceptance-rate analyzer"
    )
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--since", default=None, help="ISO date filter (YYYY-MM-DD)")
    parser.add_argument(
        "--output", default=None, help="Path to write JSON output"
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("GITHUB_TOKEN environment variable is required.", file=sys.stderr)
        sys.exit(1)

    since = args.since
    if since:
        # Ensure ISO format with time component
        if len(since) == 10:
            since = since + "T00:00:00Z"

    print(f"Fetching PRs from {args.repo}...")
    prs = fetch_prs(args.repo, token, since)
    print(f"Found {len(prs)} merged PRs.")

    metrics = compute_acceptance_rate(prs, token, args.repo)

    output_str = json.dumps(metrics, indent=2)

    if args.output:
        out_path = pathlib.Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_str)
        print(f"Metrics written to {args.output}")
    else:
        print(output_str)


if __name__ == "__main__":
    main()
