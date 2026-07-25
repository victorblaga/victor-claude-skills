---
name: mega-review
description: >
  Read-only multi-dimensional review of a diff or PR: parallel dimension agents, an evidence
  pass, verification, severity calibration, and synthesis into a markdown report. Changes no
  code. Trigger only when the user explicitly says "mega-review" or invokes /mega-review —
  not on generic review requests.
---

# Mega Review

Comprehensive, parallel code review across 9 core dimensions (plus conditional specialists). A planner subagent steers the review; parallel dimension subagents produce findings; an evidence pass runs ground-truth checks; verification fact-checks findings; a Calibrator assigns final severity; Synthesis connects tensions and recurring patterns; a Consolidator assembles the report.

**READ-ONLY.** Never modify project code. The only output is the review report and its artifact files.

Operating notes: launch all applicable dimension subagents (plus the evidence subagent when planned) in a single turn; write every artifact into the one review directory (see Output Directory); and let dimension agents report everything they find — calibration assigns severity, since a finding downgraded later is cheap and one silently dropped is unrecoverable.

## Token economics

Spend where it buys recall and judgment; cut pure overhead:

- **Files are the data channel; replies are receipts.** Every subagent returns ≤3 lines — confirmation + counts. The written file is the deliverable.
- **The orchestrator never ingests bulk content.** No diff reading, no findings inlining, no evidence output in the parent. It reads only small artifacts (`review-plan.md`, `intent.md`, interview answers, subagent confirmations).
- **Cache-first prompt layout.** Dimension prompts share an identical prefix (static rules + conventions + runtime + intent + inline hunks); per-agent material goes last.
- **Centralize curation, distribute reading.** Small digests (conventions, intent, hot spots, hunk index) are built once and passed down; bulk code reading stays in each agent's disposable context.
- **Explorer floor is mid-tier, never small.** Cap ~4 explorer spawns per dimension agent; read directly when ≤2 files are involved. These caps are ceilings, not targets — do not spawn ad-hoc re-checks outside the defined steps. Phase 1b's Critical/High double-verification is the one sanctioned second pass.
- **Deliverables are sized, not padded.** `report.md` is assembled verbatim from finding text; the Consolidator adds severity lines, dedup merges, tension/pattern annotations, ordering, and headers — nothing else. Written output runs longer than the format wants by default, and lowering effort does not reliably shorten it. The section spec is a ceiling.

## Parse the Request

Extract from the user's message:

1. **Target scope** — resolved using this priority:
   a. **User-specified** — files, a directory, a module, or a PR number → use that
   b. **Open PR** — an open PR on the current branch → review the PR diff
   c. **Diff to base** — otherwise → review the diff from the merge-base with the repo's default branch to current state, committed + uncommitted
   d. **Fallback** — if none of the above yields changed files → ask the user what to review
2. **Focus areas** (optional) — a subset of dimensions. If unspecified, run all active dimensions per the review plan.
3. **Output directory** — see below. The user may override.
4. **Background context** — migration context, architecture notes, or design docs the user provides inline. Pass this to every subagent as `{USER_CONTEXT}`.
5. **Re-review** — if the user asks to re-review after fixes, or a prior review folder exists for this branch/PR, use delta mode (see Re-review mode).

### Scope Resolution

Resolve the base branch, then compute the diff. Do **not** read file contents in the orchestrator — only metadata and paths.

**Base branch detection** (in order):
```bash
git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##'
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name' 2>/dev/null
# fallback: first existing among dev, main, master
```

**Diff and file list:**
```bash
BASE=$(git merge-base HEAD origin/<base> 2>/dev/null || git merge-base HEAD <base>)
git diff --stat $BASE                          # line count for planner skip trigger
git diff --name-only $BASE                     # committed changes
git diff --name-only                           # unstaged
git diff --cached --name-only                  # staged
git ls-files --others --exclude-standard       # untracked new files — include in scope
gh pr view --json number,title,baseRefName,body 2>/dev/null  # if PR exists
```

Combine and deduplicate file lists → `{FILE_LIST}`. Record `{BASE}` and current `HEAD` SHA.

**Hunks delivery** (orchestrator prepares paths only; subagents read content):
- If total diff ≲15-20K tokens: write `{OUTPUT_DIR}/hunks-inline.md` with the full diff from merge-base.
- Otherwise: write `{OUTPUT_DIR}/hunks/` (one file per changed source file) and `{OUTPUT_DIR}/hunks/index.md` listing paths.

Pass `{HUNKS_MODE}` (`inline` or `index`) and the path to subagents. Findings must distinguish **changed vs pre-existing** code using hunk context.

### Output Directory

**Artifact location.** This skill writes scratch, not product. Everything goes under `.scratch/` at the repo root (`~/.scratch/<project>/` outside one); a scratch path named in `AGENTS.md` / `CLAUDE.md` wins. Paths below assume the default.

```
.scratch/docs/reviews/YYYY-MM-DD-pr-NNN-XXXXX/
```

- `pr-NNN` — the PR number (e.g. `pr-97`); if there's no PR, use `diff` (e.g. `2026-03-11-diff-a3b2c`)
- `XXXXX` — 5 random alphanumeric characters to avoid collisions

Create this directory before Step 0. Pass it to every subagent as `{OUTPUT_DIR}`. Subagents must never write outside it. The consolidated report lands at `{OUTPUT_DIR}/report.md`.

Also write `{OUTPUT_DIR}/reviewed-at.json`:
```json
{"head_sha": "<current HEAD>", "base": "<merge-base>", "branch": "<branch name>", "timestamp": "<ISO date>"}
```

**Gitignore preflight**: if `.scratch/` is not matched by `.gitignore`, offer to append it and commit that as a `chore:` on its own — these are local artifacts, not PR content.

## Dimensions

Nine core dimensions plus two conditional specialists. Full catalog and activation rules: `references/review-planner.md`.

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
| 9 | Intent Conformance | IC | `intent-conformance.md` | "intent", "requirements", "scope", "delivered vs asked" |
| — | Data Migration (conditional) | DM | `data-migration.md` | migrations, schema dumps, backfills |
| — | API/Contract (conditional) | BC | `api-contract.md` | routes, serializers, public API, breaking changes |

If the user specifies focus areas, map them to dimensions and run only those (unless the review plan overrides).

## Execution

Read only the reference file for the step you're entering. Do not preload all references.

| Step | Purpose | Reference |
|------|---------|-----------|
| **0 — Plan review** | Digest intent, assign tiers, activate dimensions, hot spots | `references/review-planner.md` |
| **1 — Gather context** | Conventions summary, batched interview, runtime + intent | (below) |
| **2 — Dimension review** | Parallel subagents produce findings + evidence pass | `references/dimension-agents.md` |
| **3 — Verify & calibrate** | Fact-check findings, then assign final severity | `references/verification-calibration.md` |
| **4 — Synthesize & consolidate** | Tensions, patterns, merge into `report.md` | `references/synthesis-consolidation.md` |
| **5 — Report to user** | Verify report exists, print summary + verdict | (below) |

### Step 0: Plan Review

Read `references/review-planner.md`. Resolve scope metadata (file list, line count) without reading source files. Summarize project conventions briefly from `CLAUDE.md` / `AGENTS.md` (headings only — full digest is the planner's job) as `{PROJECT_CONVENTIONS_BRIEF}`.

Launch the planner subagent unless the skip trigger applies (~10 files AND ~500 lines). The orchestrator reads the resulting `review-plan.md` and `intent.md` only.

### Step 1: Gather Context

Read the project's `CLAUDE.md` (and guideline documents it references). Summarize conventions relevant to each dimension → `{PROJECT_CONVENTIONS}`. Pass to all subagents.

**Prior decisions:** read `.scratch/docs/reviews/{project}/notes.md` if it exists → `{PRIOR_DECISIONS}`. Pass to the Calibrator in Step 3 (not to dimension agents — avoid anchoring).

**Runtime context** — deployment and scale facts that decide whether assumption-dependent findings are real or theoretical. Combined into `{RUNTIME_CONTEXT}`.

#### Runtime profile (persistent, per project)

Path: `.scratch/docs/reviews/{project}/runtime-profile.md`

**If it exists:** read it, note a one-line summary for the interview preview, proceed.

**If missing:** infer candidates from deployment manifests, README, migrations — then collect answers in the **batched interview** below (do not run a separate interview turn).

#### Batched interview (one user turn)

Merge into a **single** batched question turn:

1. **Runtime profile** (if missing) — concurrency, data scale, load, exposure, durability/consistency. Present inferred defaults; user confirms or corrects. "Skip" → record "unknown."
2. **Change assumptions** — up to 5 targeted questions from what the **planner** flagged as assumption-sensitive (loops, migrations, new endpoints, feature flags, etc.). End with: "Any other constraints a reviewer couldn't see in the code?"
3. **Missing intent** — if `{OUTPUT_DIR}/intent.md` says MISSING, ask for the goal contract: what was asked, acceptance criteria, non-goals.
4. **Plan preview** — show the review plan summary (active dimensions, hot spots, evidence pass) and proceed unless the user objects.

Record Q&A in `{OUTPUT_DIR}/review-context.md`. Compose `{RUNTIME_CONTEXT}` from the profile + change-specific answers. If the user declines, proceed with inferred values marked "unconfirmed."

### Capability classes & model assignment

Do **not** hardcode model names. Use capability classes (`flagship`, `mid`, `small`) and intelligence levels from `{OUTPUT_DIR}/review-plan.md`. When the plan is skipped, use the **Default matrix** in `references/review-planner.md`.

Map to the harness at dispatch time:
- Claude Code: flagship → highest available reasoning model; mid → Sonnet-class; small → Haiku-class
- Codex: flagship → Sol; mid → Terra; small → Luna; use `reasoning_effort` per the plan

### Re-review mode

When a prior review folder exists for the same branch/PR (match on branch name or PR number in the folder name):

1. Read the prior `{OUTPUT_DIR}/reviewed-at.json` for `head_sha`.
2. Offer **delta review**: scope = hunks since that SHA; exclude unchanged files from dimension `{FILE_LIST}`.
3. If the prior review has an `implementation-plan.md` with accepted findings, spawn **fix-verification** at flagship/high: confirm each accepted finding was actually fixed (not merely edited near the original location).
4. Record the new `reviewed-at.json` after completion.

Delta re-review is the largest cost saver in the review→fix→re-review loop.

### Execution Discipline

- **Parallel everything** — dimension agents + evidence pass in one message; subagents read/search in parallel when independent.
- **Literal scope** — "check *every* file in the target scope."
- **Fresh-context explorers** — mid-tier; cap ~4 per dimension agent; conclusions only, not tool dumps.
- **Quote-grounding** — findings grounded in quoted snippets with `file:line`.

### Step 5: Report to User

1. Verify `{OUTPUT_DIR}/report.md` exists and is non-empty. If the Consolidator failed to write, relaunch once with a stronger "YOU MUST WRITE THE FILE" reminder; if it fails again, write the returned text yourself — never leave the review without a report.
2. Print a brief summary:

```
Review complete.

- Scope: {target} {delta | full}
- Verdict: {Ready | Ready with fixes | Not ready}
- Dimensions: {list}
- Findings (after calibration): {N critical, M high, P medium, Q low}
- Rejected (factually incorrect): {count}
- Architectural tensions: {count} (subsuming {M} findings)
- Recurring patterns: {count}

Review directory: {OUTPUT_DIR}/
Main report: {OUTPUT_DIR}/report.md
Review plan: {OUTPUT_DIR}/review-plan.md
Calibration: {OUTPUT_DIR}/calibration.md
Synthesis: {OUTPUT_DIR}/architectural-synthesis.md
```

If a dimension produced no findings, say so. If no tensions: "No architectural tensions — findings are independent."

## Cross-Skill Boundaries

| If the user wants... | Use... |
|----------------------|--------|
| Review a PR / diff into a report | **mega-review** (this skill) |
| Triage review findings into a plan | `review-triage` |
| Whole-codebase maintenance sweep | `sweep` |
| Implement a feature or proposal | `deep-implement` |
