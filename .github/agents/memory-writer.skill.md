# memory-writer — Agent Skill

## Skill ID
`memory-writer`

## Purpose
After every cloud-agent PR is merged, this skill analyzes the PR diff, review comments, and CI outcomes to produce a structured `LESSON:` block and appends it to `h1-memory-flywheel/MEMORY.md`.

This feeds the Compounding Memory Flywheel (Hypothesis 1). Over successive PRs the Memory file accumulates project-specific conventions, failure patterns, and winning strategies that Copilot's memory system can surface proactively.

## Trigger Conditions
- Pull request merged
- PR has label: `cloud-agent`
- Author is `Copilot` or `github-actions[bot]`

## Instructions

You are the memory-writer skill. Your job is to:

1. **Read the merged PR** — title, body, diff, and all review comments.
2. **Identify key learnings** from:
   - What review comments were raised (what failed code review?)
   - What CI checks failed on first push and why
   - What patterns in the diff were flagged by Copilot code review
   - What the PR author (cloud agent) got right without being asked
3. **Write a LESSON block** in the following exact format:

```
LESSON: <one-line title>
PR: #<number>
DATE: <YYYY-MM-DD>
OUTCOME: <APPROVED | REVISED | REJECTED>
WHAT_FAILED: |
  <bullet list of what required revision — be specific, name files/functions>
WHAT_WORKED: |
  <bullet list of patterns the reviewer approved without comment>
CONVENTION: |
  <one specific rule to apply in future: e.g., "Always add integration tests when touching auth middleware">
```

4. **Append the block** to `h1-memory-flywheel/MEMORY.md` with a blank line separator.

## Constraints
- Do not remove or modify existing LESSON blocks.
- Keep each field concise — max 3 bullets per list.
- The CONVENTION field must be a single actionable rule.
- If the PR was approved without any revision requests, set `OUTCOME: APPROVED` and write `WHAT_FAILED: none`.

## Output
Append the formatted LESSON block to `h1-memory-flywheel/MEMORY.md`.
