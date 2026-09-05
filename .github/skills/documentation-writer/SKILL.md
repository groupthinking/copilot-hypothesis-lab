---
name: documentation-writer
description: Write and update experiment documentation in this repository with path-accurate commands and hypothesis-consistent language.
license: MIT
---

Use this skill when editing `README.md`, `HYPOTHESES.md`, `RESULTS.md`, or any hypothesis subdirectory README.

This skill is adapted for `copilot-hypothesis-lab` from documentation-focused entries on Skills.sh.

## Documentation Rules

1. Keep hypothesis framing consistent:
   - H1: Memory Flywheel
   - H2: MCP Swarm vs Monolith
   - H3: Spaces Density
2. Verify every command/path before writing it:
   - Confirm paths exist with `rg --files` or `ls`
   - Confirm workflow names under `.github/workflows/`
3. Keep benchmark claims grounded in repository artifacts (`HYPOTHESES.md`, `RESULTS.md`, workflow outputs). Do not invent metrics.
4. Preserve operational setup details for project automation variables/secrets:
   - `PROJECT_NUMBER`
   - `PROJECT_OWNER` (optional)
   - `PROJECT_V2_TOKEN` (recommended for org projects)
5. When a task links to `.agent-orchestrator`, include a compact status handoff:
   - past performance
   - current gaps/errors
   - next steps planned

## Repo-Specific Checklist

- Update only docs tied to the requested change
- Keep markdown concise and executable
- Re-check cross-references to the three hypothesis directories

