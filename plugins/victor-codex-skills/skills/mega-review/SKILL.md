---
name: mega-review
description: >
  Comprehensive multi-dimensional code review producing a structured markdown report.
  Use when the user asks for "mega-review", "mega review", "deep review", "comprehensive review",
  "full review", "review everything", "review all dimensions", or any variation requesting a
  thorough multi-dimensional code review that produces a document.
  Do NOT trigger for ordinary lightweight review requests, bug fixing, code cleanup, or when the
  user wants code changes. This skill is strictly read-only analysis that outputs a report.
---

# Mega Review

Comprehensive, parallel code review across 8 dimensions. Parallel dimension subagents produce findings; a verification pass fact-checks them; a Calibrator assigns final severity; an Architectural Synthesis agent connects findings into deeper tensions; a Consolidator merges everything into one report.

**CRITICAL RULES:**
- **READ-ONLY** — never modify any code. The only output is the review report.
- **Fan out** — launch all applicable dimension subagents simultaneously. If the harness does not support subagents, run the dimensions sequentially yourself while preserving the same output structure.
- **All artifacts go in one dedicated review directory** — see Output Directory below.
- **Coverage over filtering** — dimension agents report everything they find; the calibration step handles severity. A finding downgraded later is cheap; a finding silently dropped is unrecoverable.

## Parse the Request

Extract from the user's message:

1. **Target scope** — resolved using this priority:
   a. **User-specified** — files, a directory, a module, or a PR number → use that
   b. **Open PR** — an open PR on the current branch → review the PR diff
   c. **Diff to base** — otherwise → review the diff from the repo's base branch (`dev`, `main`, or `master` — whichever exists) to current state, committed + uncommitted
   d. **Fallback** — if none of the above yields changed files → ask the user what to review
2. **Focus areas** (optional) — a subset of the dimensions below. If unspecified, run ALL dimensions.
3. **Output directory** — see below. The user may override.
4. **Background context** — migration context, architecture notes, or design docs the user provides inline. Pass this to every subagent as `{USER_CONTEXT}`.

### Scope Resolution

Run these checks before launching subagents:

```bash
gh pr view --json number,title,baseRefName 2>/dev/null  # open PR?
gh pr diff --name-only                                  # if PR exists
git diff <base>...HEAD --name-only                      # if no PR
git diff --name-only; git diff --cached --name-only     # uncommitted work
```

Combine and deduplicate the file lists. Pass the result to each subagent as `{FILE_LIST}`. Subagents may explore surrounding code for context, but findings must be scoped to the changed files.

### Output Directory

```
.docs/reviews/YYYY-MM-DD-pr-NNN-XXXXX/
```

- `pr-NNN` — the PR number (e.g. `pr-97`); if there's no PR, use `diff` (e.g. `2026-03-11-diff-a3b2c`)
- `XXXXX` — 5 random alphanumeric characters to avoid collisions

Create this directory before launching subagents and pass it to every subagent as `{OUTPUT_DIR}`. Subagents must never write outside it. The consolidated report lands at `{OUTPUT_DIR}/report.md`.

**Gitignore preflight**: check that `.docs/` is gitignored (review reports are local artifacts, not PR content):

```bash
grep -qE '^\.docs/?$' .gitignore 2>/dev/null || echo "ADD_NEEDED"
```

If missing, ask: "Append `.docs/` to `.gitignore`? (recommended)". On yes: append and commit `chore: ignore .docs review artifacts`.

## Dimensions

Each dimension runs as a separate parallel subagent. If the user specifies focus areas, map them to dimensions and run only those; otherwise run all 8.

| # | Dimension | Prefix | Output file | Keyword triggers |
|---|-----------|--------|-------------|------------------|
| 1 | Code Quality | CQ | `code-quality.md` | "code quality", "style", "readability", "DRY", "clean code" |
| 2 | Architecture | AR | `architecture.md` | "architecture", "race conditions", "error propagation", "design" |
| 3 | Correctness | CR | `correctness.md` | "correctness", "feature complete", "validate", "functionality" |
| 4 | Test Quality | TQ | `test-quality.md` | "tests", "test coverage", "mocks", "factories" |
| 5 | Security & Error Handling | SE | `security-error-handling.md` | "security", "error handling", "edge cases", "resilience" |
| 6 | Pattern Conformity | PC | `pattern-conformity.md` | "patterns", "consistency", "conventions", "fit in", "out of place" |
| 7 | Refactoring Opportunities | RO | `refactoring-opportunities.md` | "refactor", "consolidate", "simplify", "technical debt" |
| 8 | Performance | PF | `performance.md` | "performance", "N+1", "Big O", "slow", "queries", "memory" |

## Execution

Read only the reference file for the step you're entering. Do not preload all references.

| Step | Purpose | Reference |
|------|---------|-----------|
| **1 — Gather context** | Read project conventions, resolve scope | (below) |
| **2 — Dimension review** | 8 parallel subagents produce findings | `references/dimension-agents.md` |
| **3 — Verify & calibrate** | Fact-check findings, then assign final severity | `references/verification-calibration.md` |
| **4 — Synthesize & consolidate** | Find architectural tensions, merge into `report.md` | `references/synthesis-consolidation.md` |
| **5 — Report to user** | Verify report exists, print summary | (below) |

### Step 1: Gather Context

Read the repository's instruction file if one exists — `AGENTS.md`, `CLAUDE.md`, or similar — and any guideline documents it references. Summarize the conventions relevant to each dimension and pass them to every subagent as `{PROJECT_CONVENTIONS}`. Subagents evaluate code against these conventions, not generic preferences.

### Reasoning Tiers

Always use the latest available Codex model for every phase. Vary only `reasoning_effort` by the cognitive load of the step:

| Role | Reasoning effort | Rationale |
|------|------------------|-----------|
| Dimension subagents (Step 2) | `high` | First-pass review sets the ceiling — a finding missed here cannot be recovered later |
| Verification subagents (Step 3) | `low` | Factual cross-checking is mechanical |
| Calibrator (Step 3) | `xhigh` | Severity judgment, weighing trade-offs |
| Architectural Synthesis (Step 4) | `xhigh` | Meta-analysis, connecting dots across dimensions |
| Consolidator (Step 4) | `low` | Mechanical aggregation; must follow the write-the-file instruction reliably without rethinking severity |

Nested explorer subagents default to `medium`; raise to `high` when tracing subtle control flow or cross-file architectural behavior.

### Execution Discipline

Strong recent models self-filter: they may find an issue and choose not to report it. The pipeline is designed so that dimension agents maximize coverage and later stages handle judgment. Maintain the discipline:

- **Parallel everything** — launch all dimension subagents together; tell subagents to read files and run searches in parallel when independent.
- **Literal scope** — state explicitly when a checklist applies to all files ("check *every* file in the target scope").
- **Fresh-context explorers** — dimension agents should spawn explorer subagents for cross-file tracing; they only need the conclusion, not the tool output.
- **Quote-grounding** — for large diffs, subagents extract relevant code quotes with `file:line` references before analyzing, keeping reasoning anchored to evidence.

### Step 5: Report to User

1. Verify `{OUTPUT_DIR}/report.md` exists and is non-empty. If the Consolidator failed to write, relaunch it once with a stronger "YOU MUST WRITE THE FILE" reminder; if it fails again, write the returned text yourself — never leave the review without a report.
2. Print a brief summary:

```
Review complete.

- Scope: {target}
- Dimensions: {list}
- Findings (after calibration): {N critical, M high, P medium, Q low}
- Rejected (factually incorrect): {count}
- Architectural tensions: {count} (subsuming {M} findings)

Review directory: {OUTPUT_DIR}/
Main report: {OUTPUT_DIR}/report.md
Calibration analysis: {OUTPUT_DIR}/calibration.md
Architectural synthesis: {OUTPUT_DIR}/architectural-synthesis.md
```

If a dimension produced no findings, say so — it's useful signal. If no tensions were identified, note: "No architectural tensions — findings are independent."

## Cross-Skill Boundaries

| If the user wants... | Use... |
|----------------------|--------|
| Review a PR / diff into a report | **mega-review** (this skill) |
| Triage review findings into a plan | `review-triage` |
| Whole-codebase maintenance sweep | `sweep` |
| Implement a feature or proposal | `deep-implement` |
