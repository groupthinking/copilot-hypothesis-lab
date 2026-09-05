---
name: context-density-evaluator
description: Evaluate context-density manifests, sweep metrics, and notebook curves for H3 (Spaces Density) and H1 (Memory Flywheel). Use when evaluating context bounds, scoring rubrics, or falsification thresholds.
license: MIT
---

Use this skill when evaluating context density levels (0k, 2k, 8k, 32k, 128k, max) for Hypothesis 3 or compounding memory metrics for Hypothesis 1 in `groupthinking/copilot-hypothesis-lab` and linked items in `groupthinking/.agent-orchestrator`.

## Key Resources & Paths

- Manifests: `h3-spaces-density/spaces/*.manifest.md`
- Task spec: `h3-spaces-density/task/oauth2_device_flow.md`
- Rubric: `h3-spaces-density/rubric/score.md`
- Raw evaluation runs: `h3-spaces-density/analysis/raw/*.json`
- Analysis notebook: `h3-spaces-density/analysis/density_curve.ipynb`
- Memory metrics script: `h1-memory-flywheel/metrics/collect.py`

## Workflow

1. Manifest Verification:
   - Check context density boundary limits against manifest specifications in `h3-spaces-density/spaces/`.
2. Metric Data Collection & Analysis:
   - Verify structure of raw experiment output files (`h3-spaces-density/analysis/raw/*.json` and `h1-memory-flywheel/metrics/raw/*.json`).
   - Run metric collector script:
     ```bash
     cd h1-memory-flywheel/metrics && python collect.py --help
     ```
3. Falsification Criteria Check:
   - H1 Threshold: Memory-fed agents improve PR acceptance ≥ 30% over 50 PRs (falsified if Δ < 10%).
   - H3 Threshold: Monotonic quality vs context-density curve with locatable knee (falsified if r² < 0.3).
4. Report results and residual risks to `RESULTS.md` and linked `.agent-orchestrator` work items.
