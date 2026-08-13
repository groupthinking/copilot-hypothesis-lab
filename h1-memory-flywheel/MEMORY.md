# MEMORY.md — Copilot Agent Memory Seed File

> This file is the substrate for Hypothesis 1 (Compounding Memory Flywheel).
> Seed lessons are hand-written. All subsequent LESSON: blocks are appended automatically
> by the `memory-writer` agent skill after each cloud-agent PR merge.
>
> Format: each lesson starts with `LESSON:` on its own line.
> Do not remove or reorder existing lessons.

---

LESSON: Always add integration tests when touching authentication middleware
PR: seed-001
DATE: 2026-05-09
OUTCOME: APPROVED
WHAT_FAILED: none
WHAT_WORKED: |
  - Wrote middleware unit tests covering happy path, expired token, and missing token cases
  - Used supertest for HTTP-level integration tests
CONVENTION: |
  Any PR touching auth middleware MUST include at least one integration test that exercises the full HTTP request lifecycle, not just unit tests of the middleware function.

---

LESSON: TypeScript strict mode must not be disabled for new files
PR: seed-002
DATE: 2026-05-09
OUTCOME: APPROVED
WHAT_FAILED: none
WHAT_WORKED: |
  - All new .ts files compile with `"strict": true` in tsconfig.json
  - No `as any` casts without an accompanying comment explaining why
CONVENTION: |
  Never add `// @ts-ignore` or `as any` without a comment. If strict typing is genuinely impossible, open a separate issue and link it in the comment.

---

LESSON: GitHub Actions workflows must use pinned action versions (SHA or tag)
PR: seed-003
DATE: 2026-05-09
OUTCOME: APPROVED
WHAT_FAILED: none
WHAT_WORKED: |
  - Used `actions/checkout@v4` with explicit version tag
  - Did not use `actions/checkout@main` or floating refs
CONVENTION: |
  All `uses:` entries in .github/workflows/*.yml must reference a specific version tag (e.g., `@v4`) not a branch. Floating refs like `@main` are rejected in code review.

---
