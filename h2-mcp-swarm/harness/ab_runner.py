#!/usr/bin/env python3
"""
ab_runner.py — H2 MCP Swarm A/B Test Harness

Assigns GitHub Issues to either the monolith arm or swarm arm,
tracks results, and writes a JSON report.

Usage:
    python ab_runner.py --repo owner/repo --issues 20 --split 10 --arm both
                        [--output results/run.json]

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
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "copilot-hypothesis-lab/ab-runner",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"GitHub API error {e.code} for {url}: {e.reason}", file=sys.stderr)
        return None


def github_post(path: str, token: str, data: dict) -> Any:
    url = f"https://api.github.com{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "copilot-hypothesis-lab/ab-runner",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"GitHub API error {e.code} for {url}: {e.reason}", file=sys.stderr)
        return None


def fetch_eligible_issues(repo: str, token: str, count: int) -> list[dict]:
    """Fetch open issues labeled 'experiment-h2'."""
    data = github_get(
        f"/repos/{repo}/issues?state=open&labels=experiment-h2&per_page={count}",
        token,
    )
    if not isinstance(data, list):
        return []
    return data[:count]


def label_issue(repo: str, issue_number: int, labels: list[str], token: str) -> None:
    """Add labels to an issue."""
    github_post(
        f"/repos/{repo}/issues/{issue_number}/labels",
        token,
        {"labels": labels},
    )


def get_pr_for_issue(repo: str, issue_number: int, token: str) -> Optional[dict]:
    """Search for a PR that closes this issue."""
    data = github_get(
        f"/repos/{repo}/pulls?state=all&per_page=100",
        token,
    )
    if not isinstance(data, list):
        return None
    for pr in data:
        body = pr.get("body") or ""
        if f"#{issue_number}" in body or f"Closes #{issue_number}" in body:
            return pr
    return None


def compute_metrics(
    repo: str,
    pr: Optional[dict],
    arm: str,
    token: str,
) -> dict:
    """Compute metrics for a single PR."""
    if pr is None:
        return {
            "arm": arm,
            "pr_number": None,
            "defects_72h": None,
            "review_pass": None,
            "token_cost": None,
            "ci_pass": None,
            "status": "no_pr_found",
        }

    pr_number = pr["number"]
    merged_at = pr.get("merged_at")

    # Check reviews
    reviews = github_get(f"/repos/{repo}/pulls/{pr_number}/reviews", token) or []
    blocking = [r for r in reviews if r.get("state") == "CHANGES_REQUESTED"]
    review_pass = len(blocking) == 0

    # Check CI
    sha = pr.get("head", {}).get("sha", "")
    check_runs = []
    if sha:
        cr_data = github_get(f"/repos/{repo}/commits/{sha}/check-runs", token)
        check_runs = cr_data.get("check_runs", []) if isinstance(cr_data, dict) else []
    failed_checks = [c for c in check_runs if c.get("conclusion") == "failure"]
    ci_pass = len(failed_checks) == 0

    # Count bugs filed within 72h of merge
    defects_72h = 0
    if merged_at:
        merged_dt = datetime.datetime.fromisoformat(merged_at.rstrip("Z"))
        cutoff = (merged_dt + datetime.timedelta(hours=72)).isoformat()
        issues_data = github_get(
            f"/repos/{repo}/issues?state=open&labels=bug&since={merged_at}&per_page=100",
            token,
        )
        if isinstance(issues_data, list):
            for issue in issues_data:
                body = issue.get("body") or ""
                if f"#{pr_number}" in body and issue.get("created_at", "") <= cutoff:
                    defects_72h += 1

    return {
        "arm": arm,
        "pr_number": pr_number,
        "defects_72h": defects_72h,
        "review_pass": review_pass,
        "token_cost": None,  # Would come from token proxy / usage API
        "ci_pass": ci_pass,
        "status": "merged" if merged_at else "open",
    }


def run_ab_test(
    repo: str,
    token: str,
    issue_count: int,
    split: int,
    arm: str,
    output_path: Optional[str],
) -> None:
    print(f"Fetching {issue_count} eligible issues from {repo}...")
    issues = fetch_eligible_issues(repo, token, issue_count)

    if not issues:
        print(
            "No issues labeled 'experiment-h2' found. "
            "Create issues and label them 'experiment-h2' to run the A/B test.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Found {len(issues)} eligible issues.")

    monolith_issues = issues[:split] if arm in ("both", "monolith") else []
    swarm_issues = issues[split:] if arm in ("both", "swarm") else (issues if arm == "swarm" else [])

    results = []
    run_id = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    for issue in monolith_issues:
        issue_number = issue["number"]
        print(f"Labeling issue #{issue_number} as monolith-arm...")
        label_issue(repo, issue_number, ["monolith-arm"], token)
        pr = get_pr_for_issue(repo, issue_number, token)
        metrics = compute_metrics(repo, pr, "monolith", token)
        metrics["issue_number"] = issue_number
        metrics["run_id"] = run_id
        results.append(metrics)
        print(f"  Issue #{issue_number}: {metrics}")

    for issue in swarm_issues:
        issue_number = issue["number"]
        print(f"Labeling issue #{issue_number} as swarm-arm...")
        label_issue(repo, issue_number, ["swarm-arm"], token)
        pr = get_pr_for_issue(repo, issue_number, token)
        metrics = compute_metrics(repo, pr, "swarm", token)
        metrics["issue_number"] = issue_number
        metrics["run_id"] = run_id
        results.append(metrics)
        print(f"  Issue #{issue_number}: {metrics}")

    output_data = {
        "run_id": run_id,
        "repo": repo,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "issue_count": issue_count,
        "split": split,
        "arm": arm,
        "results": results,
    }

    output_str = json.dumps(output_data, indent=2)

    if output_path:
        out = pathlib.Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output_str)
        print(f"Results written to {output_path}")
    else:
        print(output_str)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="H2 MCP Swarm A/B Test Harness"
    )
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--issues", type=int, default=20, help="Total issues to process")
    parser.add_argument("--split", type=int, default=10, help="Number of issues for monolith arm")
    parser.add_argument(
        "--arm",
        choices=["both", "monolith", "swarm"],
        default="both",
        help="Which arm to run",
    )
    parser.add_argument("--output", default=None, help="Output JSON file path")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("GITHUB_TOKEN environment variable is required.", file=sys.stderr)
        sys.exit(1)

    run_ab_test(
        repo=args.repo,
        token=token,
        issue_count=args.issues,
        split=args.split,
        arm=args.arm,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
