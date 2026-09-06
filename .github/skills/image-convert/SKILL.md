---
name: image-convert
description: Converts SVG diagrams, context-density charts, and experiment architecture plots to PNG images for copilot-hypothesis-lab and linked groupthinking/.agent-orchestrator work. Use when asked to convert SVG files or export visual artifacts.
allowed-tools: shell
license: MIT
---

Use this skill when asked to convert SVG images or export visual diagram artifacts (such as context density curves, MCP swarm architecture diagrams, or experiment results charts) to PNG format.

This skill is configured specifically for `groupthinking/copilot-hypothesis-lab` and its connected task orchestrator `groupthinking/.agent-orchestrator`.

## Workflow

1. Locate the target SVG file (e.g. density curve outputs, experiment flow diagrams, or architecture charts).
2. Run the `convert-svg-to-png.sh` script from this skill directory:
   ```bash
   .github/skills/image-convert/convert-svg-to-png.sh <path-to-svg> [optional-output-png-path]
   ```
3. Verify that the output PNG file exists and has non-zero size.
4. If reporting status for a linked `.agent-orchestrator` task, include the path of the rendered PNG artifact in the summary.

## Examples

Convert a single SVG file:
```bash
.github/skills/image-convert/convert-svg-to-png.sh path/to/generated-density-curve.svg
```

Convert an SVG file specifying custom PNG path:
```bash
.github/skills/image-convert/convert-svg-to-png.sh path/to/generated-architecture.svg path/to/output/architecture.png
```
