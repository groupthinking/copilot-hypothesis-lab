# RESULTS.md — Live Experiment Results

> **Last updated:** _Pending first nightly aggregation run_  
> Auto-updated by `.github/workflows/results-aggregator.yml` every night at 00:00 UTC.

---

## Summary Dashboard

| Hypothesis | Status | PRs Collected | Current Δ | Verdict |
|------------|--------|--------------|-----------|---------|
| H1 — Memory Flywheel | 🟡 Running | 0 / 50 | — | Pending |
| H2 — MCP Swarm | 🟡 Running | 0 / 20 | — | Pending |
| H3 — Spaces Density | 🟡 Running | 0 / 30 | — | Pending |

---

## H1 — Compounding Memory Flywheel

### Acceptance Rate Over Time

| PR Milestone | Treatment (Memory ON) | Control (Memory OFF) | Δ |
|-------------|----------------------|---------------------|---|
| n=10 | — | — | — |
| n=20 | — | — | — |
| n=30 | — | — | — |
| n=40 | — | — | — |
| n=50 | — | — | — |

### Secondary Metrics

| Metric | Treatment | Control |
|--------|-----------|---------|
| Avg review comments / PR | — | — |
| Median time-to-green CI (min) | — | — |
| LESSON: blocks accumulated | 0 | N/A |

### H1 Verdict

> **Pending** — Experiment not yet started.

---

## H2 — MCP Swarm beats Monolith

### Per-Issue Results

| Issue # | Arm | Defects (72h) | Review Pass | CI Pass | Token Cost |
|---------|-----|--------------|-------------|---------|-----------|
| — | — | — | — | — | — |

### Aggregate Comparison

| Metric | Monolith | Swarm | Winner |
|--------|----------|-------|--------|
| Defect density | — | — | — |
| Review pass rate | — | — | — |
| Token cost / PR | — | — | — |
| CI pass rate | — | — | — |

### H2 Verdict

> **Pending** — Experiment not yet started.

---

## H3 — Spaces-as-Compiler: Context Density Curve

### Per-Space Results (5 trials each)

| Space | Context Tokens | Avg Tests Pass | Avg Lint Clean | Avg Review Approval | Avg Human Score | Avg Composite |
|-------|---------------|---------------|----------------|--------------------|-----------------| --------------|
| 0k | 0 | — | — | — | — | — |
| 2k | ~2,000 | — | — | — | — | — |
| 8k | ~8,000 | — | — | — | — | — |
| 32k | ~32,000 | — | — | — | — | — |
| 128k | ~128,000 | — | — | — | — | — |
| max | TBD | — | — | — | — | — |

### Curve Fit

| Statistic | Value |
|-----------|-------|
| Pearson r² | — |
| Spearman ρ | — |
| Curve type | — |
| Knee point (tokens) | — |

### H3 Verdict

> **Pending** — Experiment not yet started.

---

## Raw Data

Raw JSON data files are written to:
- `h1-memory-flywheel/metrics/raw/`
- `h2-mcp-swarm/harness/results/`
- `h3-spaces-density/analysis/raw/`

---

_This file is machine-generated. Do not edit manually._
