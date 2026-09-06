---
name: mcp-server-dev-testing
description: Build, verify, and test MCP servers in h2-mcp-swarm/mcp/ (spec-mcp, test-mcp, security-mcp). Use when modifying or testing Model Context Protocol servers in this repository.
license: MIT
---

Use this skill when developing, refactoring, or testing MCP (Model Context Protocol) servers in `h2-mcp-swarm/mcp/` or when validating MCP server integrations for `groupthinking/copilot-hypothesis-lab` and linked tasks in `groupthinking/.agent-orchestrator`.

This repository contains three specialized TypeScript MCP servers:
- `h2-mcp-swarm/mcp/spec-mcp` (returns PRD slices)
- `h2-mcp-swarm/mcp/test-mcp` (property-based tests)
- `h2-mcp-swarm/mcp/security-mcp` (CodeQL / semgrep security static analysis wrapper)

## Workflow

1. Navigate to the target MCP server directory (`h2-mcp-swarm/mcp/<server-name>`).
2. Run installation and build checks:
   ```bash
   npm ci && npm run build
   ```
3. Test tool registration and JSON-RPC protocol compliance:
   - Verify tool schema definitions in `src/index.ts`.
   - Confirm proper execution of handlers without uncaught promise rejections.
4. Run the A/B harness in dry-run/validation mode if testing swarm interaction:
   ```bash
   cd h2-mcp-swarm/harness
   python ab_runner.py --help
   ```
5. Report status for linked `.agent-orchestrator` items detailing build status, tool availability, and any discovered defects.
