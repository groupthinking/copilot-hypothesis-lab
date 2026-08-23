# RESULTS.md — Live Experiment Results

> **Last updated:** 2026-08-23 00:02 UTC  
> Auto-updated by `.github/workflows/results-aggregator.yml` every night at 00:00 UTC.

---

## Summary Dashboard

| Hypothesis | Status | PRs Collected | Current Δ | Verdict |
|------------|--------|--------------|-----------|---------|
| H1 — Memory Flywheel | 🟡 Running | 0 / 50 | — | Pending |
| H2 — MCP Swarm | 🟡 Running | 0 / 20 | — | Pending |
| H3 — Spaces Density | 🟡 Running | 75 / 30 | — | Pending |

---

## H1 — Compounding Memory Flywheel

### Acceptance Rate Over Time

| PR Milestone | Treatment (Memory ON) | Control (Memory OFF) | Δ |
|-------------|----------------------|---------------------|---|
| n=10 | None | None | — |
| n=20 | None | None | — |
| n=30 | None | None | — |
| n=40 | None | None | — |
| n=50 | None | None | — |

### Secondary Metrics

| Metric | Treatment | Control |
|--------|-----------|---------|
| Avg review comments / PR | None | None |
| Median time-to-green CI (min) | — | — |
| LESSON: blocks accumulated | 3 | N/A |

### H1 Verdict

> **Pending**

---

## H2 — MCP Swarm beats Monolith

### Aggregate Comparison

| Metric | Monolith | Swarm | Winner |
|--------|----------|-------|--------|
| Defect density | — | — | — |
| Review pass rate | — | — | — |
| Token cost / PR | — | — | — |
| CI pass rate | — | — | — |

### H2 Verdict

> **Pending**

---

## H3 — Spaces-as-Compiler: Context Density Curve

### Per-Space Results (5 trials each)

| Space | Context Tokens | Avg Tests Pass | Avg Lint Clean | Avg Review Approval | Avg Human Score | Avg Composite |
|-------|---------------|---------------|----------------|--------------------|-----------------| --------------|
| 0k | 0 | — | — | — | — | — |
| 2k | 2000 | — | — | — | — | — |
| 8k | 8000 | — | — | — | — | — |
| 32k | 32000 | — | — | — | — | — |
| 128k | 128000 | — | — | — | — | — |
| max | TBD | — | — | — | — | — |

### H3 Verdict

> **Pending**

---

## Raw Data

Raw JSON data files are written to:
- `h1-memory-flywheel/metrics/raw/`
- `h2-mcp-swarm/harness/results/`
- `h3-spaces-density/analysis/raw/`

---

_This file is machine-generated. Do not edit manually._
