# copilot-hypothesis-lab

> A public benchmark repository exploring **gravity vs anti-gravity** in AI retrieval, while pressure-testing novel theories to maximize GitHub Copilot's surface area.

[![CI](https://github.com/groupthinking/copilot-hypothesis-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/groupthinking/copilot-hypothesis-lab/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## 🧪 Core Hypotheses & Experiments

### 1. Copilot Surface Area Experiments
| # | Name | H₁ Summary | Falsification Threshold |
|---|------|-----------|------------------------|
| H1 | Compounding Memory Flywheel | Memory-fed agents improve PR acceptance ≥30% over 50 PRs | Δ < 10% |
| H2 | MCP Swarm beats Monolith | 3 narrow MCPs produce lower defect density than 1 monolith | Swarm ≥ monolith defects OR cost > 2× with no quality gain |
| H3 | Spaces-as-Compiler | Monotonic quality vs context-density curve with locatable knee | r² < 0.3 |

*See [HYPOTHESES.md](HYPOTHESES.md) for full pre-registered specification.*

### 2. Retrieval Engine: Gravity vs Anti-gravity
In an AI retrieval system:
- **Gravity** is the force that pulls results toward your specific interests — exploitation.
- **Anti-gravity** (entropy/serendipity) pushes the system toward exploration and diversification.

This lab explores three architectural patterns:
1. **Exploration/Exploitation Trade-off** — Multi-Armed Bandits (Epsilon-Greedy & Thompson Sampling)
2. **Diversity Re-ranking** — Novelty scoring based on semantic distance from history
3. **Broadening Vectors** — Entropy injection into query vectors

---

## 🤖 Managed Agent System

This repository runs a **managed agent collaboration system** between:

| Agent | Role |
|-------|------|
| **Claude** (via GitHub Copilot) | Code review, technical analysis, hypothesis generation |
| **Jules** (Google Labs) | Async coding tasks — use `#Jules` tag in any issue or PR |

### Using Jules
Add `#Jules` anywhere in an issue or PR comment to trigger the Jules detection workflow. Jules will pick up the task and implement it asynchronously. See [jules-task-prompts](https://github.com/groupthinking/jules-task-prompts) for effective Jules prompt patterns.

---

## 🗂 Repository Layout & Architecture

```text
copilot-hypothesis-lab/
├── README.md                              # Lab overview + how to run
├── HYPOTHESES.md                          # Formal H₀/H₁, metrics, falsification criteria
├── RESULTS.md                             # Auto-updated by nightly Action
├── .github/                               # CI/CD Workflows, Agents, and Skills
├── bandit.py                              # Multi-Armed Bandit (Retrieval Engine)
├── retrieval/                             # Python Retrieval Engine Core
│   ├── gravity.py                         # Exploitation — cosine similarity 
│   ├── anti_gravity.py                    # Exploration — novelty scoring
│   └── engine.py                          # Orchestrator — bandit-driven selection
├── agents/                                # Agent SDK Integrations
├── h1-memory-flywheel/                    # Hypothesis 1 — Compounding Memory Flywheel
├── h2-mcp-swarm/                          # Hypothesis 2 — MCP Swarm beats Monolith
├── h3-spaces-density/                     # Hypothesis 3 — Spaces-as-Compiler
└── LICENSE                                # MIT

```

---

## 🚀 How to Run the Experiments

### 1. Python Retrieval Engine Setup

```bash
# Core package (no Claude SDK required)
pip install -e .

# With Claude Agent SDK support
pip install -e ".[claude]"

# Full development setup
pip install -e ".[all]"

```

*Requirements: Python 3.10+*

**Run the quick start demo:**

```bash
python examples/quick_start.py

```

**Running Tests:**

```bash
pytest tests/ -v
pytest tests/ --cov=hypothesis_lab --cov-report=term-missing

```

### 2. Copilot Hypothesis Runner Setup

*Prerequisites: Copilot Enterprise enabled, `gh` CLI authenticated, Python 3.11+, Node 20+.*

**Hypothesis 1 — Memory Flywheel**

```bash
cd h1-memory-flywheel/scripts
npx ts-node append_lesson.ts --pr <PR_NUMBER> --repo <owner/repo>

cd ../metrics
python collect.py --repo <owner/repo> --since <ISO_DATE>

```

**Hypothesis 2 — MCP Swarm A/B**

```bash
# Start the three MCP servers (each in their own terminal):
cd h2-mcp-swarm/mcp/spec-mcp && npm install && npm start
cd h2-mcp-swarm/mcp/test-mcp && npm install && npm start
cd h2-mcp-swarm/mcp/security-mcp && npm install && npm start

# Run the A/B harness:
cd h2-mcp-swarm/harness
python ab_runner.py --repo <owner/repo> --issues 20 --split 10

```

**Hypothesis 3 — Spaces Density Sweep**

```bash
gh workflow run h3-density-sweep.yml
cd h3-spaces-density/analysis
jupyter notebook density_curve.ipynb

```

---

## 🔄 CI/CD Workflows & Results

Live results are recorded in [RESULTS.md](RESULTS.md). The nightly workflow pulls metrics from the GitHub API and updates that file automatically at 00:00 UTC.

| Workflow | Trigger | Description |
| --- | --- | --- |
| `ci.yml` | Push / PR | Lint, type-check, test across Python 3.10–3.12 |
| `jules.yml` | Issue/PR with `#Jules` | Detects Jules tasks and logs them for dispatch |
| `agent_collab.yml` | Schedule / manual | Daily analysis run and agent coordination |
| `pr_merge.yml` | Manual (`workflow_dispatch`) | Validates and merges a ready PR using selected merge method |
| `h1-memory-rollup.yml` | `pull_request` merge | Fires on `cloud-agent` label, calls memory-writer skill |
| `results-aggregator.yml` | Cron (Nightly) | Aggregates Copilot lab metrics into RESULTS.md |

---

## 📖 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Run `ruff check src/ tests/` and `pytest tests/`
5. Submit a PR using the PR template — *the memory-writer skill will automatically record the outcome of your PR if it impacts the lab experiments.*

For Jules tasks, open an issue with the `#Jules` tag or use the Jules Task issue template.

---

## 🔗 References

* [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk)
* [Jules task prompts](https://github.com/groupthinking/jules-task-prompts)
* [Multi-Armed Bandit algorithms](https://en.wikipedia.org/wiki/Multi-armed_bandit)
* [Maximal Marginal Relevance (diversity re-ranking)](https://dl.acm.org/doi/10.1145/290941.291025)

---

## License

[MIT](https://www.google.com/search?q=LICENSE)

```

```
