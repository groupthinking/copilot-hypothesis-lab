# H3 — Spaces-as-Compiler: Context Density Predicts Agent Quality

## Overview

This directory implements **Hypothesis 3**: testing whether there is a measurable monotonic relationship between Copilot Space context density and cloud-agent output quality — with a locatable inflection point (diminishing returns knee).

## Structure

```
h3-spaces-density/
├── README.md
├── spaces/                    # 6 Space context manifests
│   ├── 0k.manifest.md         # No context (~0 tokens)
│   ├── 2k.manifest.md         # Minimal context (~2,000 tokens)
│   ├── 8k.manifest.md         # Moderate context (~8,000 tokens)
│   ├── 32k.manifest.md        # Rich context (~32,000 tokens)
│   ├── 128k.manifest.md       # Very rich context (~128,000 tokens)
│   └── max.manifest.md        # Maximum supported context
├── task/
│   └── oauth2_device_flow.md  # Canonical task specification
├── rubric/
│   └── score.md               # Human scoring rubric (1–5)
└── analysis/
    ├── density_curve.ipynb    # Analysis notebook (log curve fit + knee detection)
    └── raw/                   # JSON data from each sweep run
```

## Canonical Task

All 30 trials use the same task: **"Add OAuth2 device flow to this Express app."**

See [task/oauth2_device_flow.md](task/oauth2_device_flow.md) for the full specification.

## Space Levels

| Space | Target Tokens | Content |
|-------|-------------|---------|
| `0k` | 0 | Bare task description only — no code context |
| `2k` | ~2,000 | Task + minimal README + package.json |
| `8k` | ~8,000 | + core application files |
| `32k` | ~32,000 | + full codebase without tests |
| `128k` | ~128,000 | + tests + docs + related RFCs |
| `max` | TBD | Maximum context the Space supports |

## Running the Sweep

```bash
# Trigger manually via GitHub Actions:
gh workflow run h3-density-sweep.yml

# Or with a filter (only run specific spaces):
gh workflow run h3-density-sweep.yml -f space_filter=0k,2k,8k

# After collecting results, run the analysis notebook:
cd analysis
jupyter notebook density_curve.ipynb
```

## Scoring

Each PR is scored on 4 dimensions by `density_curve.ipynb`:
1. **tests_pass** (0 or 1): All CI tests pass
2. **lint_clean** (0 or 1): Zero linter errors
3. **review_approval** (0 or 1): Copilot code-review approves with no blocking comments
4. **human_score** (1–5): Human evaluator using rubric in `rubric/score.md`

**Composite quality** = `0.3*tests_pass + 0.2*lint_clean + 0.2*review_approval + 0.3*(human_score/5)`

## Expected Outcome

A log curve fit to composite_quality vs context_tokens with r² ≥ 0.3 and a locatable knee point confirms H₁. The knee point is where marginal quality improvement per additional token approaches zero.

See [HYPOTHESES.md](../../HYPOTHESES.md) for full falsification criteria.
