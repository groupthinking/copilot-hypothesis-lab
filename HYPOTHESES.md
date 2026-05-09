# HYPOTHESES.md — Pre-Registered Experiment Specifications

> **Pre-registration date:** 2026-05-09  
> All thresholds below are locked before data collection begins. Changing them post-hoc invalidates the experiment.

---

## Hypothesis 1 — "Compounding Memory Flywheel"

### Formal Statement

| | Statement |
|---|---|
| **H₀** | A repo with Copilot Memory enabled and agent-authored LESSON: blocks shows **no statistically significant improvement** in cloud-agent PR first-pass acceptance rate compared to a control repo with Memory disabled (Δ < 10% after n=50 PRs). |
| **H₁** | The Memory-enabled repo shows cloud-agent first-pass acceptance rate improve **≥ 30%** within 50 PRs vs. the control repo with Memory disabled. |

### Metrics

| Metric | Description | Collection Method |
|--------|-------------|-------------------|
| `pr_acceptance_rate` | % of cloud-agent PRs merged without any revision requests | `h1-memory-flywheel/metrics/collect.py` |
| `review_comments_per_pr` | Average number of review comments left on cloud-agent PRs | GitHub API: `pulls/{pr}/reviews` |
| `time_to_green_ci` | Median minutes from PR open to all CI checks green | GitHub API: `check_runs` timestamps |
| `lesson_count` | Number of LESSON: blocks accumulated in MEMORY.md | `grep -c "^LESSON:" MEMORY.md` |

### Method

1. **Treatment repo**: This repo — `memory-writer.skill.md` appends a `LESSON:` block to `MEMORY.md` after every cloud-agent PR merge. The `memory-reader.agent.md` custom agent reads `MEMORY.md` before planning.
2. **Control repo**: Fork of this repo with the memory-writer skill disabled and `memory-reader.agent.md` replaced by a baseline agent that reads no memory.
3. Run **n = 50 cloud-agent PRs** per arm (100 total).
4. Measure all four metrics above at PR milestones: n=10, 20, 30, 40, 50.

### Falsification Criteria

| Condition | Outcome |
|-----------|---------|
| Δ `pr_acceptance_rate` ≥ 30% at n=50 | **H₁ CONFIRMED** |
| Δ `pr_acceptance_rate` ∈ [10%, 30%) | **Inconclusive** — extend to n=100 |
| Δ `pr_acceptance_rate` < 10% at n=50 | **H₀ NOT REJECTED** — H₁ falsified |

### Timeline

- Data collection: rolling (starts on first cloud-agent merge)
- Analysis checkpoint: after every 10 PRs
- Final verdict: after n=50 per arm

---

## Hypothesis 2 — "MCP Swarm beats Monolith Agent"

### Formal Statement

| | Statement |
|---|---|
| **H₀** | A monolithic cloud-agent with no MCP servers produces **equal or lower** defect density and **equal or higher** Copilot code-review pass rate compared to a swarm of 3 narrow MCP servers (Spec-MCP, Test-MCP, Security-MCP). |
| **H₁** | Decomposing one cloud-agent task into 3 narrow MCP servers invoked by a single custom agent (`swarm-orchestrator.agent.md`) produces **lower defect density** AND **higher Copilot code-review pass rate** than the monolith, without exceeding **2× token cost**. |

### Metrics

| Metric | Description | Collection Method |
|--------|-------------|-------------------|
| `defect_density` | Bugs filed against merged PRs within 72 h | GitHub Issues labeled `bug` + linked PR |
| `review_pass_rate` | % of PRs where Copilot code-review makes zero blocking comments | GitHub API: `pulls/{pr}/reviews` |
| `token_cost_per_pr` | Estimated token consumption per PR (input + output) | OpenAI/Copilot usage API or proxy log |
| `ci_pass_rate` | % of PRs where all CI checks pass on first push | GitHub API: `check_runs` |

### Method

1. Select **20 real GitHub Issues** of comparable complexity (labeled `experiment-h2`).
2. Randomly assign: 10 to **Monolith arm**, 10 to **Swarm arm**.
3. **Monolith**: `gh copilot suggest` / cloud-agent with no MCP tools.
4. **Swarm**: `swarm-orchestrator.agent.md` calls Spec-MCP → Test-MCP → Security-MCP in sequence.
5. Merge all PRs. Track bugs filed within 72 h. Collect token logs.

### Falsification Criteria

| Condition | Outcome |
|-----------|---------|
| Swarm `defect_density` < Monolith AND Swarm `review_pass_rate` > Monolith AND token cost ≤ 2× | **H₁ CONFIRMED** |
| Swarm `defect_density` ≥ Monolith | **H₁ falsified on defects** |
| Swarm token cost > 2× with no quality gain | **H₁ falsified on efficiency** |

### Timeline

- Setup: MCP servers deployed and registered in `.vscode/mcp.json`
- Data collection: 20 issues × automated runs
- Final verdict: after all 20 issues resolved

---

## Hypothesis 3 — "Spaces-as-Compiler: Context Density predicts Agent Quality"

### Formal Statement

| | Statement |
|---|---|
| **H₀** | There is **no statistically significant monotonic relationship** (r² < 0.3) between Copilot Space context density (tokens of curated spec/code/docs) and cloud-agent output quality score. |
| **H₁** | There **is** a measurable monotonic relationship (r² ≥ 0.3) between context density and agent quality, with an empirically locatable **inflection point** (diminishing returns knee) in the curve. |

### Metrics

| Metric | Description | Collection Method |
|--------|-------------|-------------------|
| `context_tokens` | Size of Space context in tokens | Manifest metadata + tokenizer |
| `tests_pass` | 1 if all tests pass, 0 otherwise | CI run result |
| `lint_clean` | 1 if linter reports zero errors, 0 otherwise | CI run result |
| `review_approval` | 1 if Copilot code-review approves (0 blocking comments), 0 otherwise | GitHub API |
| `human_score` | Human rubric score 1–5 (see `rubric/score.md`) | Manual evaluation |
| `composite_quality` | Weighted composite: `0.3*tests_pass + 0.2*lint_clean + 0.2*review_approval + 0.3*human_score/5` | Computed in notebook |

### Method

1. Define one **canonical task**: "Add OAuth2 device flow to this Express app" (see `task/oauth2_device_flow.md`).
2. Create **6 Spaces** with progressively richer context:
   - `0k` — no context (bare task description only)
   - `2k` — minimal context (~2,000 tokens)
   - `8k` — moderate context (~8,000 tokens)
   - `32k` — rich context (~32,000 tokens)
   - `128k` — very rich context (~128,000 tokens)
   - `max` — maximum supported context
3. For each Space, run cloud agent **5 times** → 30 PRs total.
4. Score each PR on all metrics above.
5. Fit log curve to `composite_quality` vs `context_tokens`; locate knee using second-derivative method.

### Falsification Criteria

| Condition | Outcome |
|-----------|---------|
| r² ≥ 0.3 with monotonic trend | **H₁ CONFIRMED** — curve exists |
| Knee point locatable (second-derivative peak) | **Inflection confirmed** — Spaces Optimizer viable |
| r² < 0.3 | **H₀ NOT REJECTED** — context is noise for this task type |

### Timeline

- Data collection: 30 PRs (6 spaces × 5 trials), automated by `h3-density-sweep.yml`
- Analysis: `density_curve.ipynb` after all 30 PRs collected
- Final verdict: r² and curve fit from notebook

---

## Statistical Notes

- All tests use **α = 0.05** significance level.
- For H1 and H2, use Mann-Whitney U test (non-parametric, small samples).
- For H3, use Pearson r² and Spearman rank correlation.
- No p-hacking: analysis script is committed before data collection begins.
- Multiple comparison correction: Bonferroni (3 hypotheses → α_adjusted = 0.017).
