---
name: github-actions-failure-debugging
description: Debug failing GitHub Actions workflows for copilot-hypothesis-lab and report status to linked .agent-orchestrator work items.
license: MIT
---

Use this skill when asked to investigate CI, workflow, build, or test failures.

This repository has multiple experiment workflows. Prioritize these when triaging:
- `.github/workflows/project-flow-automation.yml`
- `.github/workflows/project-automation.yml`
- `.github/workflows/h1-memory-rollup.yml`
- `.github/workflows/h2-swarm-ab.yml`
- `.github/workflows/h3-density-sweep.yml`
- `.github/workflows/results-aggregator.yml`

## Workflow

1. List recent runs with `actions_list` (`list_workflow_runs`) for `groupthinking/copilot-hypothesis-lab`.
2. Filter to the relevant branch, pull request, or workflow file.
3. Pull failure details with `get_job_logs`:
   - First use `run_id` + `failed_only=true`
   - If no failed jobs are returned, inspect workflow jobs and retry with explicit `job_id`
4. Reproduce locally with the smallest matching command:
   - Node/TS MCP servers: `npm run build` and any existing tests in touched `h2-mcp-swarm/mcp/*` package
   - Python harness/scripts: run targeted script invocation only
5. Fix the root cause and re-run targeted validation commands before finalizing.

## Required Status Report Format

If the work item is linked to `.agent-orchestrator` (for example `groupthinking/.agent-orchestrator#14`), include:
- `Past performance`: what has been passing/failing recently
- `Current gaps/errors`: exact failing workflow/job and failure reason
- `Next steps planned`: concrete follow-up actions

Use this short template:

```markdown
### CI Status
- Past performance: <summary>
- Current gaps/errors: <summary>
- Next steps planned: <summary>
```

