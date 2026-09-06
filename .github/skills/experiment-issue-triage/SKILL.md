---
name: experiment-issue-triage
description: Triage copilot-hypothesis-lab experiment issues and linked groupthinking/.agent-orchestrator work into H1/H2/H3 paths, labels, and next actions.
license: MIT
---

Use this skill when asked to triage issues, plan experiment work, or update linked `groupthinking/.agent-orchestrator` handoffs for `groupthinking/copilot-hypothesis-lab`.

This skill is adapted for `copilot-hypothesis-lab` from issue-triage-oriented entries on Skills.sh.

## Triage Steps

1. Classify the issue by experiment surface:
   - H1 Memory Flywheel: `h1-memory-flywheel/`, memory collection, or lesson rollups
   - H2 MCP Swarm vs Monolith: `h2-mcp-swarm/`, MCP servers, A/B harness, or `experiment-h2` issues
   - H3 Spaces Density: `h3-spaces-density/`, space manifests, canonical task, rubric, or density analysis
   - Project automation: `.github/workflows/project-automation.yml`, `.github/workflows/project-flow-automation.yml`, project variables, or `.agent-orchestrator` handoffs
2. Identify the smallest repository artifact that can validate the issue:
   - H1 metrics: `h1-memory-flywheel/metrics/collect.py`
   - H2 issue selection and defect tracking: `h2-mcp-swarm/harness/ab_runner.py`
   - H3 scoring and context-density inputs: `h3-spaces-density/rubric/score.md` and `h3-spaces-density/spaces/`
   - Results rollups: `RESULTS.md` and `.github/workflows/results-aggregator.yml`
3. Recommend labels only when supported by existing repo conventions:
   - `experiment-h2` for H2 A/B candidates
   - `bug` for defects that should count toward H2 defect density
4. When an issue is connected to `groupthinking/.agent-orchestrator`, include a compact handoff:
   - past performance
   - current gaps/errors
   - next steps planned
5. Avoid inventing benchmark results. If metrics are missing, state the gap and point to the collection artifact that should produce them.

## Triage Output Template

```markdown
### Experiment Triage
- Surface: <H1 | H2 | H3 | Project automation>
- Evidence: <paths, workflow names, or labels checked>
- Recommended next action: <smallest concrete step>
- Orchestrator handoff: <past performance / current gaps / next steps, if linked>
```
