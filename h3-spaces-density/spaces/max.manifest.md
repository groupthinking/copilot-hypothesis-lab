# Space Manifest — max (Maximum Context)

## Metadata
- **Space ID**: `h3-max`
- **Target Context Tokens**: Maximum supported by Copilot Spaces
- **Actual Context**: Everything + extended reference material

## Purpose
Maximum context. Includes everything from 128k plus extended reference material that may or may not be useful. Tests whether maximum context degrades, matches, or marginally improves upon 128k quality — confirming or locating the diminishing returns plateau.

## Context Included

All of 128k, plus:

1. **Full dependency source** — key library source files (Express, passport, etc.) — ~30,000 tokens
2. **All GitHub Actions workflow files** — CI/CD configuration — ~5,000 tokens
3. **Docker and infrastructure configs** — Dockerfile, docker-compose — ~2,000 tokens
4. **Extended test fixtures** — additional mock data, ~8,000 tokens
5. **External API documentation** — full OAuth provider API references — ~15,000 tokens
6. **Community forum Q&As** — Stack Overflow-style solutions for device flow — ~10,000 tokens
7. **Competing implementation references** — open-source OAuth2 device flow libraries — ~20,000 tokens

**Total**: Maximum supported (TBD — depends on model and Space configuration)

## What the Agent Knows

Everything from 128k, plus:
- Library internals for deeper integration
- Community-validated patterns and pitfalls
- Reference implementations for comparison

## Expected Behavior

At maximum context, we expect to see one of:
1. **Plateau**: Quality matches 128k → inflection already passed
2. **Slight degradation**: More noise than signal at this density → context overload
3. **Marginal improvement**: More information still helps → inflection not yet reached

All three outcomes are scientifically valid results for H3.

## Hypothesis Role

Terminal data point. Combined with 128k results, this determines:
- Whether the inflection point is before 128k (plateau here)
- Or after 128k (still improving)
- Or whether context is uniformly beneficial up to max (no knee found)

## Notes

- Actual token count will vary based on the specific application being tested
- Token count should be measured and recorded before each trial run
- The `density_curve.ipynb` notebook expects token count in metadata
