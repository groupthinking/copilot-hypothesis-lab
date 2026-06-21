# Scoring Rubric — H3 Spaces Density Experiment

## Overview

Each PR produced by the density sweep is scored on 4 dimensions. Three are automated (recorded by CI); one requires a human evaluator using this rubric.

## Automated Metrics (0 or 1)

These are recorded automatically by the `h3-density-sweep.yml` workflow:

| Metric | Pass Condition |
|--------|---------------|
| `tests_pass` | All CI test checks have conclusion `success` |
| `lint_clean` | Linter check has conclusion `success` with 0 errors |
| `review_approval` | Copilot code-review posts 0 blocking comments |

## Human Score (1–5)

The human evaluator reads the PR diff and scores on the following scale:

### Score 5 — Exemplary
- All acceptance criteria from `task/oauth2_device_flow.md` fully met
- RFC 8628 compliance: all 5 poll states correctly implemented
- Security: crypto.randomBytes used, constant-time comparison, rate limit enforced
- Code is idiomatic, well-typed, and follows existing project conventions
- Tests are meaningful property-based or integration tests, not just smoke tests
- Documentation is complete and accurate

### Score 4 — Good
- All mandatory acceptance criteria met
- Minor issues: one acceptance criterion partially met, or minor style inconsistency
- Security requirements met
- Tests pass but coverage is shallow
- Documentation present but incomplete

### Score 3 — Acceptable
- Core flow works (device code issuance and happy-path polling)
- 1–2 acceptance criteria not met (e.g., missing `slow_down` state, or `verification_uri_complete` missing)
- No critical security issues, but minor weaknesses (e.g., non-constant-time comparison)
- Tests present but limited to happy path only
- Documentation minimal

### Score 2 — Marginal
- Core flow partially works (device code issued but polling logic incomplete or broken)
- Multiple acceptance criteria not met
- Security issues present (e.g., predictable codes, no rate limiting)
- Tests insufficient or failing
- Little to no documentation

### Score 1 — Failing
- Core flow does not work or produces incorrect RFC responses
- Most acceptance criteria not met
- Serious security vulnerabilities (e.g., codes guessable, no TTL enforcement)
- No meaningful tests
- No documentation

## Composite Quality Score

After collecting all 4 metrics, compute composite quality:

```
composite = 0.3 * tests_pass
          + 0.2 * lint_clean
          + 0.2 * review_approval
          + 0.3 * (human_score / 5)
```

Range: 0.0 (all failed, score=1) to 1.0 (all passed, score=5).

## Evaluation Protocol

1. Human evaluator reads the PR diff without knowledge of which Space level was used (blind evaluation).
2. Evaluator checks each acceptance criterion in `task/oauth2_device_flow.md`.
3. Scores are entered into the raw JSON file for that trial.
4. `density_curve.ipynb` computes composite scores and plots the curve.

## Inter-Rater Reliability

When multiple evaluators are used:
- Each PR is scored independently by 2 evaluators
- If scores differ by > 1 point, a third evaluator resolves
- Report Cohen's κ in the notebook if multiple evaluators used

## Example Score Entry (JSON)

```json
{
  "space": "8k",
  "trial": 3,
  "pr_number": 42,
  "metrics": {
    "tests_pass": 1,
    "lint_clean": 1,
    "review_approval": 0,
    "human_score": 4,
    "composite_quality": 0.74
  },
  "evaluator_notes": "Missing slow_down polling state. Rate limiting present but uses wall-clock instead of per-client tracking."
}
```
