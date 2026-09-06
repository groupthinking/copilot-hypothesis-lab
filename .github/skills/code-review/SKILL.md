---
name: code-review
description: Review copilot-hypothesis-lab PRs for experiment correctness, workflow safety, MCP behavior, and linked .agent-orchestrator handoff quality.
license: MIT
---

Use this skill when reviewing pull requests in `groupthinking/copilot-hypothesis-lab`, especially with Copilot code review.

This skill is adapted for `copilot-hypothesis-lab` from code-review-oriented entries on Skills.sh.

## Review Focus

1. Check whether the change preserves the registered hypothesis boundaries in `HYPOTHESES.md`:
   - H1: Memory Flywheel changes should not alter the control/treatment comparison after data collection starts.
   - H2: MCP Swarm changes should keep monolith and swarm arms comparable and should not hide token or defect costs.
   - H3: Spaces Density changes should preserve the canonical task, six context-density manifests, and scoring rubric.
2. For workflow changes, verify the touched workflow path exists under `.github/workflows/` and that project automation keeps these operational inputs intact:
   - `PROJECT_NUMBER`
   - `PROJECT_OWNER`
   - `PROJECT_V2_TOKEN`
3. For H2 MCP changes, review the touched server or harness in `h2-mcp-swarm/` for:
   - consistent request/response assumptions across Spec-MCP, Test-MCP, and Security-MCP
   - no shell command construction from untrusted issue text
   - targeted validation using the package's existing `npm run build` command when source changes
4. For H3 Space changes, compare edits against `h3-spaces-density/task/oauth2_device_flow.md`, `h3-spaces-density/rubric/score.md`, and the relevant `h3-spaces-density/spaces/*.manifest.md` file.
5. If the PR references `groupthinking/.agent-orchestrator`, ensure the final review or handoff clearly states:
   - past performance
   - current gaps/errors
   - next steps planned

## Output Guidance

- Report only high-confidence correctness, security, or experiment-validity issues.
- Avoid style-only feedback unless it blocks an experiment workflow or makes a benchmark result ambiguous.
- Include exact file paths and the smallest suggested fix.
