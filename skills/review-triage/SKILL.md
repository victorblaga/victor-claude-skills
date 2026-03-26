---
name: review-triage
description: >
  Interactive triage of a mega-review report into an implementation plan.
  Takes findings from /mega-review and walks through them one at a time with
  the user, deciding accept / reject / defer for each. Produces an ordered
  implementation-plan.md and maintains a persistent notes.md for rejected and
  deferred findings that survives review folder deletion.
  Trigger when the user says "review-triage", "triage the review", "triage findings",
  or invokes /review-triage.
  Do NOT trigger for running a review (/mega-review) or for implementing findings
  (/deep-implement) — this skill is strictly the triage step between those two.
---

# Review Triage

Interactive, finding-by-finding triage of a `/mega-review` report. The user and the assistant walk through every finding together, deciding what to fix, what to reject, and what to defer. The output is an ordered implementation plan.

**Core principle: architecture preservation.** The burden of proof is on the finding to justify a change, not on the developer to justify keeping the current design. Many review suggestions destroy more value than they create. This skill exists to separate the signal from the noise.

## Locate the Review

1. The user may provide a path directly. If so, use it.
2. Otherwise, scan `docs/reviews/` for the most recent review folder (by date prefix in the directory name).
3. Confirm with the user: "I found a review at `docs/reviews/{folder}/`. Is this the one to triage?"

The review folder contains:
- `report.md` — the consolidated report (source of truth for findings and severities)
- Dimension-specific files (`code-quality.md`, `architecture.md`, `correctness.md`, `test-quality.md`, `security-error-handling.md`, `pattern-conformity.md`, `refactoring-opportunities.md`, `performance.md`, `architectural-synthesis.md`, `skeptic.md`)

## Setup

### 1. Read the review

Read `report.md` in full. Then read each dimension-specific file in the review folder — these contain the detailed analysis behind each finding. Build a mental model of all findings, their severities, and any architectural tensions.

### 2. Identify the project

Derive a short project identifier from the review context. This is used for the persistent notes file. Sources, in priority order:
- The review folder name often contains a PR reference (e.g., `2026-03-16-pr-42-x8k2f` implies the project is whatever repo the PR belongs to)
- The `report.md` scope line names the target codebase
- The current working directory / git remote name
- Ask the user if unclear

### 3. Create output files

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
docs/reviews/{project}/notes.md
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
1. **Architectural tensions** (T-1, T-2, ...) first — these are meta-findings that subsume individual findings. Triaging a tension decides the fate of all its subsumed findings at once.
2. **Critical** severity findings
3. **High** severity findings
4. **Medium** severity findings
5. **Low** severity findings

Within each severity level, group by dimension to maintain context continuity.

### For each finding, present

Display the finding to the user with this structure:

```
### {ID}: {title}
**Severity:** {severity} | **Dimension:** {dimension}
**Location:** {file:line}

**What the review found:**
{Brief summary of the issue — 2-3 sentences max. Pull from the dimension-specific file for detail.}

**Risk if we fix it:**
{What could go wrong with the change — regressions, added complexity, abstraction cost, maintenance burden. Be honest.}

**Risk if we leave it:**
{What could go wrong if we don't fix it — bugs, performance issues, confusion for future developers.}

**Recommendation:** {ACCEPT / REJECT / DEFER}
**Rationale:** {1-3 sentences explaining the recommendation. Apply the guardrails below.}
```

For **architectural tensions**, present the tension itself plus a summary of all subsumed findings. If the user accepts the tension, all subsumed findings are accepted. If rejected, each subsumed finding must be triaged individually.

### Recommendation guardrails

Apply these principles when making recommendations:

**Readily accept:**
- Bugs and correctness issues (the code is wrong)
- Security vulnerabilities with real attack surface
- Missing error handling that could cause silent data loss
- Race conditions or concurrency bugs

**Accept with scrutiny:**
- Performance issues — is there evidence of real impact, or is it theoretical? "This is O(n^2)" matters only if n is large enough to matter in practice.
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
- **Complexity:** Trivial / Small / Medium
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
