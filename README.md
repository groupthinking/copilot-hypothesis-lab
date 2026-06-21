# copilot-hypothesis-lab

> **Public benchmark repo** pressure-testing 3 novel theories that maximize GitHub Copilot's surface area: Spaces, MCP, cloud agent, code review, Memory, agent skills, and custom agents.

---

## 🗂 Repository Layout

```
copilot-hypothesis-lab/
├── README.md                              # This file — lab overview + how to run
├── HYPOTHESES.md                          # Formal H₀/H₁, metrics, falsification criteria
├── RESULTS.md                             # Auto-updated by nightly Action
├── .github/
│   ├── workflows/
│   │   ├── h1-memory-rollup.yml          # Appends LESSON: blocks post-merge
│   │   ├── h2-swarm-ab.yml               # A/B harness: monolith vs MCP swarm
│   │   ├── h3-density-sweep.yml          # Runs 6 Spaces × 5 trials
│   │   └── results-aggregator.yml        # Nightly RESULTS.md update
│   ├── agents/
│   │   └── memory-writer.skill.md        # H1 agent skill
│   └── copilot/
│       └── custom-agents/
│           ├── memory-reader.agent.md    # H1 custom agent
│           └── swarm-orchestrator.agent.md # H2 custom agent
├── h1-memory-flywheel/                   # Hypothesis 1 — Compounding Memory Flywheel
│   ├── README.md
│   ├── MEMORY.md                         # Seed memory file
│   ├── scripts/append_lesson.ts
│   └── metrics/collect.py
├── h2-mcp-swarm/                         # Hypothesis 2 — MCP Swarm beats Monolith
│   ├── README.md
│   ├── mcp/
│   │   ├── spec-mcp/                     # TS MCP server — returns PRD slice
│   │   ├── test-mcp/                     # TS MCP server — property-based tests
│   │   └── security-mcp/                 # TS MCP server — CodeQL/semgrep wrapper
│   ├── .vscode/mcp.json
│   └── harness/ab_runner.py
├── h3-spaces-density/                    # Hypothesis 3 — Spaces-as-Compiler
│   ├── README.md
│   ├── spaces/                           # 6 context-density manifests
│   ├── task/oauth2_device_flow.md        # Canonical task spec
│   ├── rubric/score.md
│   └── analysis/density_curve.ipynb
└── LICENSE                               # MIT
```

---

## 🧪 The Three Hypotheses

| # | Name | H₁ Summary | Falsification Threshold |
|---|------|-----------|------------------------|
| H1 | Compounding Memory Flywheel | Memory-fed agents improve PR acceptance ≥30% over 50 PRs | Δ < 10% |
| H2 | MCP Swarm beats Monolith | 3 narrow MCPs produce lower defect density than 1 monolith | Swarm ≥ monolith defects OR cost > 2× with no quality gain |
| H3 | Spaces-as-Compiler | Monotonic quality vs context-density curve with locatable knee | r² < 0.3 |

See [HYPOTHESES.md](HYPOTHESES.md) for full pre-registered specification.

---

## 🚀 How to Run Each Experiment

### Prerequisites
- GitHub repository with Copilot Enterprise / Copilot for Business enabled
- `GITHUB_TOKEN` with `repo`, `pull_requests: write`, `issues: write` scopes
- Python 3.11+ and Node.js 20+ installed locally
- `gh` CLI authenticated

### Hypothesis 1 — Memory Flywheel

```bash
# 1. Ensure MEMORY.md seed file is present
cat h1-memory-flywheel/MEMORY.md

# 2. The workflow triggers automatically after every cloud-agent PR merge.
#    To run the lesson-append script manually:
cd h1-memory-flywheel/scripts
npx ts-node append_lesson.ts --pr <PR_NUMBER> --repo <owner/repo>

# 3. Collect metrics after n PRs:
cd h1-memory-flywheel/metrics
python collect.py --repo <owner/repo> --since <ISO_DATE>
```

The workflow `.github/workflows/h1-memory-rollup.yml` fires on every `pull_request` merge event with label `cloud-agent` and calls the memory-writer agent skill.

### Hypothesis 2 — MCP Swarm A/B

```bash
# 1. Start the three MCP servers (each in their own terminal):
cd h2-mcp-swarm/mcp/spec-mcp && npm install && npm start
cd h2-mcp-swarm/mcp/test-mcp && npm install && npm start
cd h2-mcp-swarm/mcp/security-mcp && npm install && npm start

# 2. Run the A/B harness against 20 issues:
cd h2-mcp-swarm/harness
python ab_runner.py --repo <owner/repo> --issues 20 --split 10

# 3. The workflow h2-swarm-ab.yml can be triggered manually:
gh workflow run h2-swarm-ab.yml -f issue_count=20
```

### Hypothesis 3 — Spaces Density Sweep

```bash
# 1. Review the canonical task spec:
cat h3-spaces-density/task/oauth2_device_flow.md

# 2. Review each space manifest:
ls h3-spaces-density/spaces/

# 3. Run the density sweep workflow manually:
gh workflow run h3-density-sweep.yml

# 4. After 30 PRs are collected, open the analysis notebook:
cd h3-spaces-density/analysis
jupyter notebook density_curve.ipynb
```

### Nightly Aggregation

Results are aggregated automatically by `.github/workflows/results-aggregator.yml` every night at 00:00 UTC and written to [RESULTS.md](RESULTS.md).

---

## 📊 Results

Live results are in [RESULTS.md](RESULTS.md). The nightly workflow pulls metrics from GitHub API and updates that file automatically.

---

## 📖 Contributing

1. Fork the repo
2. Create a branch for your experiment variant
3. Submit a PR — the memory-writer skill will record the outcome

---

## License

[MIT](LICENSE)
