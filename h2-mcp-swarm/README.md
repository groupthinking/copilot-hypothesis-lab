# H2 — MCP Swarm beats Monolith Agent

## Overview

This directory implements **Hypothesis 2**: testing whether decomposing a cloud-agent task into 3 narrow MCP servers produces lower defect density and higher code-review pass rate than a monolithic agent with no MCP.

## Structure

```
h2-mcp-swarm/
├── README.md
├── mcp/
│   ├── spec-mcp/           # TS MCP server — returns PRD slice for a feature
│   ├── test-mcp/           # TS MCP server — generates + runs property-based tests
│   └── security-mcp/       # TS MCP server — runs CodeQL/semgrep, returns findings
├── .vscode/
│   └── mcp.json            # Registers all 3 MCP servers for Copilot
└── harness/
    ├── ab_runner.py         # A/B test harness
    └── results/             # JSON output from each run
```

## The Three MCP Servers

### spec-mcp (port 3001)
Returns a PRD (Product Requirements Document) slice for a given GitHub Issue.
- Input: issue number
- Output: structured spec with acceptance criteria, API contract, and data model

### test-mcp (port 3002)
Generates property-based tests for a given implementation and runs them.
- Input: list of modified files
- Output: generated test code + pass/fail result + coverage %

### security-mcp (port 3003)
Runs CodeQL and semgrep static analysis on modified files.
- Input: list of modified files + tool selection
- Output: structured list of findings (severity, rule, location, recommendation)

## Running Locally

```bash
# Terminal 1 — Spec MCP
cd mcp/spec-mcp && npm install && npm start

# Terminal 2 — Test MCP
cd mcp/test-mcp && npm install && npm start

# Terminal 3 — Security MCP
cd mcp/security-mcp && npm install && npm start

# Terminal 4 — Run A/B harness
cd harness
python ab_runner.py --repo owner/repo --issues 20 --split 10 --arm both
```

## A/B Design

- **Monolith arm**: 10 issues assigned to default cloud agent (no MCP)
- **Swarm arm**: 10 issues assigned to `swarm-orchestrator.agent.md` (uses all 3 MCPs)
- Issues labeled `experiment-h2` are eligible
- Monolith issues get label `monolith-arm`; swarm issues get label `swarm-arm`

## Success Criteria

H₁ confirmed if (at n=20):
- Swarm `defect_density` < Monolith `defect_density`
- Swarm `review_pass_rate` > Monolith `review_pass_rate`
- Swarm token cost ≤ 2× Monolith token cost

See [HYPOTHESES.md](../../HYPOTHESES.md) for full falsification criteria.
