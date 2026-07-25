---
name: review-triage
description: >
  Walk a mega-review report finding by finding with the user — accept / reject / defer —
  producing an ordered implementation-plan.md plus a persistent notes.md that outlives the
  review folder. Trigger only when the user explicitly says "review-triage" or invokes
  $review-triage. This is the step between $mega-review and $deep-implement, not either
  of them.
---

# Review Triage

Interactive, finding-by-finding triage of a `/mega-review` report. The user and the assistant walk through every finding together, deciding what to fix, what to reject, and what to defer. The output is an ordered implementation plan.

**Artifact location.** Everything this skill writes is scratch, not product. Default to `.scratch/` at the repository root (`git rev-parse --show-toplevel`), unless the project's or user's instruction files (`AGENTS.md`, `CLAUDE.md`, or equivalent) name a different scratch location — those win. Outside a git repo, use `~/.scratch/<project>/`. The paths in this skill assume the default.

**Core principle: architecture preservation.** The burden of proof is on the finding to justify a change, not on the developer to justify keeping the current design. Many review suggestions destroy more value than they create. This skill exists to separate the signal from the noise.

## Execution Notes

- **Effort**: If the harness exposes an effort control, use the highest tier — triage requires judgment about trade-offs and architectural fit.
- **Batched turns**: Every user turn adds reasoning overhead. When presenting findings, batch related low-severity items when possible. Keep the triage moving.
- **Literal scope**: Be explicit about which findings a decision applies to (e.g., "This reject applies to *all* similar pattern-conformity findings in the review").

## Locate the Review

1. The user may provide a path directly. If so, use it.
2. Otherwise, scan `.scratch/docs/reviews/` for the most recent review folder (by date prefix in the directory name).
3. Confirm with the user: "I found a review at `.scratch/docs/reviews/{folder}/`. Is this the one to triage?"

The review folder contains:
- `report.md` — the consolidated report (source of truth for findings, severities, and verdict)
- `review-plan.md`, `intent.md` — planner output (v2+; absent in older reviews)
- `review-context.md` — change-specific runtime assumptions from the batched interview (absent in older reviews)
- Dimension-specific files: `code-quality.md`, `architecture.md`, `correctness.md`, `test-quality.md`, `security-error-handling.md`, `pattern-conformity.md`, `refactoring-opportunities.md`, `performance.md`, `intent-conformance.md`, `data-migration.md`, `api-contract.md` (last three v2+; absent if not activated)
- `evidence/findings.md` — ground-truth failures from test/lint/type-check (v2+; absent if no evidence pass)
- `architectural-synthesis.md`, `calibration.md` (older reviews may name calibration `skeptic.md`)

**Finding ID prefixes:** CQ, AR, CR, TQ, SE, PC, RO, PF, IC (intent), DM (migration), BC (API contract), EV (evidence pass), T- (architectural tension), P- (recurring pattern rollup).

## Setup

### 1. Read the review

Read `report.md` in full — including **Delivered vs. Asked**, **Architectural Tensions**, and **Recurring Patterns** if present. Then read each dimension-specific file in the review folder for detail behind individual findings. Build a mental model of all findings, severities, tensions, patterns, and the overall verdict.

### 2. Identify the project

Derive a short project identifier from the review context. This is used for the persistent notes file. Sources, in priority order:
- The review folder name often contains a PR reference (e.g., `2026-03-16-pr-42-x8k2f` implies the project is whatever repo the PR belongs to)
- The `report.md` scope line names the target codebase
- The current working directory / git remote name
- Ask the user if unclear

### 3. Read the runtime context

Read `.scratch/docs/reviews/{project}/runtime-profile.md` (persistent deployment/scale facts) and `{review_folder}/review-context.md` (change-specific guarantees) if they exist. Findings carry an `Assumes` field stating the runtime conditions they depend on — these two files are the ground truth for judging whether those assumptions hold. If neither file exists, assumptions in findings are unverified; ask the user when a decision hinges on one.

### 4. Create output files

Create two files:

**Implementation plan** (ephemeral, lives with the review):
```
{review_folder}/implementation-plan.md
```

Initialize with:
```markdown
# Implementation Plan

**Source review:** {review_folder}/report.md
**Triaged by:** {user} + Claude
**Date:** {today}

## Accepted Findings

(Findings will be added here as triage proceeds.)

## Rejected Findings

(Findings rejected during triage, with rationale.)
```

**Persistent notes** (survives review folder deletion):
```
.scratch/docs/reviews/{project}/notes.md
```

If this file already exists, read it — it contains prior decisions from earlier reviews. Append to it; never overwrite. If it does not exist, create it with:
```markdown
# Review Notes — {project}

Persistent record of rejected and deferred review findings. This file survives review folder deletion.
Each entry is self-contained — no references to files that may be deleted.

---
```

## Triage Process

### Ordering

Present findings in this order:
1. **Delivered vs. Asked** (IC summary) — if the report has intent gaps (Missing/Partial requirements), discuss whether to accept fixing them before individual findings.
2. **Architectural tensions** (T-1, T-2, ...) — meta-findings subsuming individual findings. Triaging a tension decides all subsumed findings at once.
3. **Recurring patterns** (P-1, P-2, ...) — rolled-up repeated defects. Triaging a pattern decides all listed occurrences at once (same as tensions).
4. **Critical** severity findings (skip IDs marked `Part of T-{N}` or `Part of P-{N}` unless the parent was rejected)
5. **High** severity findings
6. **Medium** severity findings
7. **Low** severity findings

Within each severity level, group by dimension to maintain context continuity.

### For each finding, present

Display the finding to the user with this structure:

```
### {ID}: {title}
**Severity:** {severity} | **Dimension:** {dimension}
**Location:** {file:line} (or location list for P-{N} patterns)
**Fix complexity:** {Trivial / Small / Medium / Large — from the finding; omit if absent in older reviews}

**What the review found:**
{Brief summary — 2-3 sentences max. Pull from the dimension-specific file for detail.}

**Assumes:** {Runtime conditions and whether the runtime profile / change context confirms or contradicts them. Omit if unconditional.}

**Risk if we fix it:**
{Regressions, complexity, abstraction cost, maintenance burden. Be honest.}

**Risk if we leave it:**
{Bugs, performance, confusion for future developers.}

**Recommendation:** {ACCEPT / REJECT / DEFER}
**Rationale:** {1-3 sentences. Apply guardrails below.}
```

For **architectural tensions**, present the tension plus subsumed finding summaries. Accept → all subsumed findings accepted. Reject → triage subsumed findings individually.

For **recurring patterns**, present the pattern, all locations, and the systemic fix. Same accept/reject logic as tensions.

### Recommendation guardrails

Apply these principles when making recommendations:

**Readily accept:**
- Bugs and correctness issues (the code is wrong)
- Security vulnerabilities with real attack surface
- Missing error handling that could cause silent data loss
- Race conditions or concurrency bugs
- Intent conformance gaps (Missing/Partial requirements from IC or Delivered vs. Asked)
- Evidence-pass failures (EV-* findings from test/lint/type-check output)

**Accept with scrutiny:**
- Performance issues — is there evidence of real impact, or is it theoretical? "This is O(n^2)" matters only if n is large enough to matter in practice. Check the claimed scale against the runtime profile, not the reviewer's guess.
- Concurrency findings — real only under the deployment's actual parallelism. A race that requires ≥2 instances is not a bug under a hard single-instance guarantee; recommend reject with that rationale, noting the condition under which it becomes real.
- Test gaps — missing tests for important behavior are worth adding. Missing tests for trivial getters are not.
- DRY violations — is the duplication actually causing maintenance problems, or is it harmless parallelism?

**Default to reject (burden of proof on the finding):**
- Architectural suggestions that introduce new abstractions — abstractions have cost. Does this abstraction hide meaningful complexity, or does it just add indirection?
- "Code quality" suggestions that make code different but not better — renaming, restructuring, stylistic preferences
- Pattern conformity findings where the "inconsistency" is actually the better approach — sometimes the new code is right and the old pattern is wrong
- Refactoring opportunities that are real but not worth the effort right now

**Always reject:**
- Suggestions that would undo deliberate architectural decisions (check `notes.md` for prior decisions)
- Findings that were already addressed in a previous review cycle (check `notes.md`)
- Findings whose stated assumptions the runtime profile or change context contradicts — record the contradicted assumption in the rejection rationale so the decision is revisitable if the guarantee changes

**Keeping the runtime profile current:** when the user's triage answers reveal a runtime fact not yet in `.scratch/docs/reviews/{project}/runtime-profile.md` (e.g. "we only ever run one instance", "that table is tiny"), append it to the profile — dated, like `notes.md` entries — so future reviews calibrate against it automatically.

### Trivial findings

For findings that are obviously correct and trivially fixable (e.g., a missing type annotation, an unused import, a typo in a docstring), you may recommend **auto-accept** — but still present the finding and wait for user confirmation. Never silently accept anything.

### Batching low-severity findings

When you reach Low severity findings and there are many of them, you may present them in batches of 3-5 with a brief summary for each, rather than the full presentation format. The user can still accept/reject individually or batch-accept/batch-reject.

## Recording decisions

### On ACCEPT

Add the finding to the **Accepted Findings** section of `implementation-plan.md`:

```markdown
### {N}. {ID}: {title}
- **Severity:** {severity}
- **Location:** {file:line}
- **What to do:** {Concrete action — not just "fix this" but what the fix looks like}
- **Complexity:** {Trivial / Small / Medium / Large — prefer Fix complexity from the finding; fall back to your judgment}
```

The number `{N}` is the sequential order (1, 2, 3, ...) — this becomes the implementation order.

### On REJECT

Add to **both** files:

In `implementation-plan.md` (Rejected Findings section):
```markdown
### {ID}: {title}
- **Severity:** {severity}
- **Decision:** Rejected
- **Rationale:** {Why this finding does not warrant a change. Be specific.}
```

In `notes.md` (the persistent file):
```markdown
## {ID}: {title}
- **Date:** {today}
- **Review:** {review_folder_name}
- **Severity:** {severity}
- **Dimension:** {dimension}
- **Location:** {file:line}
- **Finding:** {Self-contained description of what the review found. No references to review files.}
- **Decision:** Rejected
- **Rationale:** {Self-contained rationale. Someone reading this 6 months later should understand why without needing any other file.}
```

### On DEFER

Add to `notes.md` only (not to the implementation plan):

```markdown
## {ID}: {title}
- **Date:** {today}
- **Review:** {review_folder_name}
- **Severity:** {severity}
- **Dimension:** {dimension}
- **Location:** {file:line}
- **Finding:** {Self-contained description.}
- **Decision:** Deferred
- **Rationale:** {Why now is not the right time. What would need to change for this to become worth doing.}
```

## Finalization

After all findings have been triaged:

### 1. Order the implementation plan

Review the accepted findings and reorder them for implementation efficiency:
- Group related changes (same file, same module)
- Put foundational changes before dependent ones
- Put quick wins early for momentum

Replace the sequential numbers with the final order.

### 2. Add summary header

Update `implementation-plan.md` with a summary:

```markdown
## Summary

- **Total findings reviewed:** {count}
- **Accepted:** {count} ({breakdown by severity})
- **Rejected:** {count}
- **Deferred:** {count}
- **Estimated scope:** {Trivial / Small / Medium / Large — based on the accepted findings}
```

### 3. Present the final plan

Show the user:
- The summary statistics
- The ordered list of accepted findings (just IDs and titles)
- The path to `implementation-plan.md`
- The path to `notes.md`
- Suggest next step: "To implement these findings, run `/deep-implement` and point it at `{review_folder}/implementation-plan.md`"

## Resumption

If the user invokes `/review-triage` and an `implementation-plan.md` already exists in the review folder:

1. Read it to determine progress — which findings have been triaged?
2. Cross-reference with `report.md` to identify un-triaged findings
3. Present: "I found an in-progress triage with {N} findings triaged ({X} accepted, {Y} rejected, {Z} deferred) and {M} remaining. Continue?"
4. If confirmed, resume from the next un-triaged finding

## Edge Cases

- **Empty review:** If the review has no findings, say so and skip triage.
- **All findings rejected:** This is a valid outcome. The implementation plan will have zero accepted findings. Note this explicitly.
- **User wants to change a prior decision:** Allow it. Update both files accordingly. If changing a reject to accept, add to the accepted list and remove from rejected. If changing an accept to reject, reverse the operation.
- **User wants to skip a finding and come back:** Allow it. Track skipped findings and present them at the end.
- **Review has no dimension files:** Fall back to `report.md` only. The triage still works — findings are all in the report.
