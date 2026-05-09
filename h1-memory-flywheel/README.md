# H1 — Compounding Memory Flywheel

## Overview

This directory implements **Hypothesis 1**: testing whether writing structured post-mortems back into Copilot Memory after every cloud-agent PR creates a compounding improvement in PR acceptance rate.

## Structure

```
h1-memory-flywheel/
├── README.md              # This file
├── MEMORY.md              # Accumulated LESSON: blocks (seed + agent-appended)
├── scripts/
│   └── append_lesson.ts   # Script invoked by h1-memory-rollup.yml
└── metrics/
    ├── collect.py         # PR acceptance-rate analyzer
    └── raw/               # JSON snapshots from each run
```

## How It Works

1. **Seed**: `MEMORY.md` starts with 3 hand-written lessons establishing baseline conventions.
2. **Trigger**: When a PR labeled `cloud-agent` is merged to `main`, the workflow `.github/workflows/h1-memory-rollup.yml` fires.
3. **Lesson append**: The workflow calls `append_lesson.ts` which uses the GitHub API to fetch PR reviews, comments, and CI results, then asks the `memory-writer` skill to synthesize a `LESSON:` block.
4. **Memory reads**: The `memory-reader.agent.md` custom agent reads `MEMORY.md` at the start of every task, applying relevant conventions.
5. **Metric collection**: `collect.py` tracks PR acceptance rate over time across both arms.

## Running Locally

```bash
# Append a lesson for a specific PR (dry-run):
cd scripts
npx ts-node append_lesson.ts --pr 42 --repo owner/repo --dry-run

# Collect current metrics:
cd metrics
python collect.py --repo owner/repo --since 2026-01-01
```

## Expected Outcome

After 50 PRs in the treatment arm (Memory ON), PR acceptance rate (PRs merged without revision) should be ≥ 30% higher than the control arm (Memory OFF).

See [HYPOTHESES.md](../../HYPOTHESES.md) for full falsification criteria.
