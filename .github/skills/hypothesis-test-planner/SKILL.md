---
name: hypothesis-test-planner
description: Plan and run minimal targeted validation for H1/H2/H3 changes, with explicit regression checks and experiment status reporting.
license: MIT
---

Use this skill when changes touch experiment code, workflows, harnesses, or custom agents.

This skill is adapted for `copilot-hypothesis-lab` from testing/TDD-oriented entries on Skills.sh.

## Validation Strategy

1. Identify touched hypothesis surface:
   - `h1-memory-flywheel/`
   - `h2-mcp-swarm/`
   - `h3-spaces-density/`
   - `.github/workflows/`
2. Run the smallest existing validation commands that cover the touched area:
   - Node packages: `npm run build`, `npm test` (if defined)
   - Python scripts: targeted invocation with real args where feasible
   - Workflow changes: YAML sanity check plus workflow-specific assumptions review
3. Avoid unrelated full-suite runs unless targeted checks are insufficient.
4. Confirm no security regressions in changed logic and no secret material in modified files.
5. Report validation outcomes as:
   - what was run
   - what passed/failed
   - residual risk

## Linked Repo Handoff

If the task closes or updates `.agent-orchestrator` work:
- Summarize past performance signals from `RESULTS.md` and recent workflow runs
- Call out unresolved gaps/errors
- List next planned experiment or maintenance steps

