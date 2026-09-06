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
│   │   ├── results-aggregator.yml        # Nightly RESULTS.md update
│   │   ├── project-automation.yml        # Project board sync & handoff tracking
│   │   └── bootstrap-labels.yml          # One-time label creation
│   │   ├── project-flow-automation.yml   # Project tab automation for handoffs/progress
│   │   └── results-aggregator.yml        # Nightly RESULTS.md update
│   ├── agents/
│   │   └── memory-writer.skill.md        # H1 agent skill
│   ├── skills/
│   │   ├── github-actions-failure-debugging/ # Debug failing CI workflows
│   │   ├── image-convert/                # Convert SVG charts & diagrams to PNG
│   │   ├── mcp-server-dev-testing/       # Build & test TS MCP servers
│   │   ├── context-density-evaluator/    # Evaluate context density & metrics
│   │   ├── documentation-writer/         # Keep benchmark docs updated
│   │   ├── hypothesis-test-planner/      # Minimal targeted experiment validation
│   │   ├── code-review/                  # Review experiment and workflow changes
│   │   └── experiment-issue-triage/      # Classify and hand off project issues
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

### Copilot Skills In This Repo

Project skills are located in `.github/skills/`:
- `github-actions-failure-debugging`: triage workflow failures using Actions run + job logs, then report `past performance`, `current gaps/errors`, and `next steps planned` for linked `groupthinking/.agent-orchestrator` work items.
- `image-convert`: convert SVG diagrams, context-density charts, and architecture plots to PNG using `convert-svg-to-png.sh` for this repo and `groupthinking/.agent-orchestrator`.
- `mcp-server-dev-testing`: build, verify, and property-test TS MCP servers (`spec-mcp`, `test-mcp`, `security-mcp`) in `h2-mcp-swarm/mcp/`.
- `context-density-evaluator`: evaluate context-density manifests, sweep raw output logs, and notebook curves for H3 and H1 falsification thresholds.
- `documentation-writer`: keep benchmark docs accurate and hypothesis-consistent when editing README/spec/results content.
- `hypothesis-test-planner`: run minimal targeted validation for H1/H2/H3 changes and summarize residual risk.
- `code-review`: focus Copilot code review on experiment correctness, workflow safety, MCP behavior, and linked `.agent-orchestrator` handoff quality.
- `experiment-issue-triage`: classify lab issues into H1/H2/H3/project automation work, preserve existing labels, and prepare compact orchestrator handoffs.

These skills adapt common Skills.sh patterns (workflow debugging, documentation, testing, code review, and issue triage) to this repository's experiment structure and the connected `groupthinking/.agent-orchestrator` workflow.

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

### Project Board Automation

The workflow `.github/workflows/project-automation.yml` keeps the **Project** tab in sync with repository activity automatically:

| Event | Board Action |
|-------|-------------|
| Issue opened | Added to project → **Triage** column |
| Issue assigned | Moved to **In Progress** |
| PR opened (draft) | Moved to **In Progress** |
| PR opened / ready for review | Moved to **In Review** |
| Review requested | Moved to **In Review** + handoff comment |
| Review approved | Moved to **Done** + handoff comment |
| Changes requested | Moved to **In Progress** + handoff comment |
| PR merged | Moved to **Done** + handoff comment |
| PR closed without merge | Moved to **Triage** |
| Issue / PR reopened | Moved to **In Progress** / **In Review** |

Issues and PRs are also auto-labeled by hypothesis (`H1-memory`, `H2-swarm`, `H3-spaces`) based on file paths or title keywords.

**Setup:**

1. Create a GitHub Project (Board layout) with a **Status** field containing options: `Triage`, `In Progress`, `In Review`, `Done`.
2. Set the `PROJECT_NUMBER` env var in `project-automation.yml` to match your project number (default: `1`).
3. If the project is org-owned, create a `PROJECT_TOKEN` secret with `project` scope. For user-owned projects, `GITHUB_TOKEN` is sufficient.
4. Run the label bootstrap workflow once:
   ```bash
   gh workflow run bootstrap-labels.yml
   ```

### Nightly Aggregation

Results are aggregated automatically by `.github/workflows/results-aggregator.yml` every night at 00:00 UTC and written to [RESULTS.md](RESULTS.md).

### Project Tab Flow Automation

`.github/workflows/project-flow-automation.yml` updates Project tab item status for issue/PR transitions and posts linked-issue handoff comments for PR events. Configure:
- Repository variable `PROJECT_NUMBER` (required)
- Repository variable `PROJECT_OWNER` (optional; defaults to repository owner)
- Secret `PROJECT_V2_TOKEN` (recommended for org-level projects)

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
