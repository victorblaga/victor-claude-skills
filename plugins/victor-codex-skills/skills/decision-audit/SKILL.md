---
name: decision-audit
description: >
  Audit the decisions a coding session made — the choices, not the diff. Elicits a
  structured self-report by category, cross-checks it against an independent fresh-context
  extraction from the diff, then triages risky decisions one at a time (keep / revise /
  revert). Works same-session or from the decision log an overnight goal run left behind.
  Trigger only on explicit invocation — "decision-audit", "$decision-audit", "audit your
  decisions". Not for general code review (that is $mega-review), and never auto-fire after
  finishing implementation work.
---

# Decision Audit

Audit the *choices* a session made, not the code. The failure mode this skill targets: a
model implements decisions flawlessly but decides badly where the task was underspecified,
then declares success — a fix that works by coincidence, a scope-narrowing nobody approved,
a trade-off taken silently.

**Artifact location.** Everything this skill writes is scratch, not product. Default to `.scratch/` at the repository root (`git rev-parse --show-toplevel`), unless the project's or user's instruction files (`AGENTS.md`, `CLAUDE.md`, or equivalent) name a different scratch location — those win. Outside a git repo, use `~/.scratch/<project>/`. The paths in this skill assume the default.

Asking "which choices are you not confident of?" is not enough: it only surfaces *known*
uncertainty, from the same model that made the bad choice. This skill hardens the idea with
three mechanisms:

1. **Structured elicitation by category** — enumeration against a fixed checklist, not an
   open-ended confidence question.
2. **Fresh-context cross-check** — an independent subagent extracts decisions from the diff
   alone, never seeing the self-report.
3. **Blindspot ranking** — decisions visible in the diff but absent from the self-report are
   the loudest finding class.

This is a 5–15 minute pre-merge ritual, not another mega-review. It does not judge code
quality, style, or test coverage — only discretionary decisions.

## Execution Notes

- **Explicit invocation only.** Never run this because implementation "just finished".
- **Effort**: if the harness exposes an effort control, use a high tier for comparison and
  triage — judging blast radius requires judgment. The cross-check subagent runs at the
  session's default tier.
- **Honesty over image**: the self-elicitation is enumeration, not confession. A decision
  made confidently still gets listed. Omitting a decision to look better defeats the skill.

## Modes

Detect the mode — do not ask:

- **Same-session** — the implementing conversation is in the current context.
  Self-elicitation (Phase 2) draws on it.
- **Fresh-session** — the implementation happened elsewhere (overnight goal run, a previous
  session). Phase 2 instead reads the decision log at
  `.scratch/docs/decision-logs/<branch-or-goal-slug>.md` if present. If no log exists, skip Phase 2,
  run the audit on the cross-check extraction alone, and state that limitation explicitly in
  the triage and the report.

## Phase 1 — Scope the Diff

1. Determine the base branch: `origin/HEAD` if set, else `main`/`master` — whichever exists.
2. Default scope: uncommitted changes plus commits on the current branch vs. the base.
   User-supplied arguments override: an explicit commit range or a PR number.
3. Confirm scope in one line before proceeding, e.g.:
   "Auditing decisions in 7 files changed vs `master` (feature X work). Proceed?"
4. If the diff is empty, say so and stop.
5. If the diff is very large (roughly >2,000 changed lines), offer to split the audit by
   commit or by module before running the cross-check.

## Phase 2 — Structured Self-Elicitation

Read `references/elicitation-categories.md` and walk **every** category in order,
enumerating the decisions made during the audited work. Rules:

- Cover each category explicitly; write "none" for a category rather than skipping it.
- Record every decision using the schema in the reference file: what was decided,
  alternatives considered, why, confidence, reversibility, blast radius if wrong.
- Number self-reported decisions `D-1`, `D-2`, ...
- In fresh-session mode, parse the decision log into the same schema (provenance: `log`)
  instead of recalling from conversation.

Present the self-report to the user compactly (one line per decision) before Phase 3 — no
approval gate, just visibility while the cross-check runs.

## Phase 3 — Fresh-Context Cross-Check

Spawn **one** subagent whose input is the diff and read access to the codebase — never the
self-report, the conversation, or the decision log. Prompt template:

> You are auditing a code change for the *decisions* it embodies — not reviewing its
> quality. Run `git diff <scope>` and read any touched files you need for context.
>
> Enumerate every discretionary decision the change embodies: places where the author chose
> among plausible alternatives. Look specifically for: scope of a fix (root cause vs.
> symptom; general vs. coincidentally specific), new abstractions/dependencies/files,
> silent trade-offs (performance, storage, complexity, API shape), behavior changes beyond
> the obvious task, error-handling and edge-case choices, and test/verification scope.
>
> For each decision report: what was decided, the plausible alternatives, what the code
> suggests about why, and the blast radius if the choice is wrong (what breaks, how
> visibly, how hard to undo). Number them X-1, X-2, ... Return the list as structured text.
> Do not report style preferences or nitpicks — only genuine decisions.

## Phase 4 — Compare & Rank

Match `D-*` and `X-*` entries by file and topic. Build the triage queue in this order:

1. **Blindspots** — `X-*` decisions with no matching `D-*`. Loudest class: the session made
   a choice it did not report.
2. **Mismatches** — matched pairs where the self-reported claim and what the code actually
   does disagree.
3. **Low confidence** — self-reported decisions with low confidence or high blast radius.
4. **The rest** — ordered by blast radius.

Matched, low-risk decisions may be batch-listed as "presumed sound" — shown to the user in
one block, not triaged individually.

## Phase 5 — Triage One-by-One

For each decision in the queue, present:

```
### {ID}: {one-line decision}
**Category:** {elicitation category} | **Source:** {self-report / cross-check / both}
**Location:** {file:line}

**The decision:** {what was chosen, alternatives, why}
**Risk if kept:** {what goes wrong if this choice is bad}
**Risk if changed:** {cost/regression risk of redoing it}

**Recommendation:** {KEEP / REVISE / REVERT}
**Rationale:** {1-3 sentences}
```

Verdicts:

- **KEEP** — the decision stands; record the rationale in the report.
- **REVISE** — change the approach. Small revisions (single-file, low-risk) are applied
  immediately in-session and verified with the project's local checks. Larger ones are
  appended to a fix list in the report.
- **REVERT** — undo the change; same small-vs-large handling as revise.

Wait for the user's verdict on each item; never silently apply a recommendation. Batch
low-risk items 3–5 at a time to keep triage moving.

## Report

Save to `.scratch/docs/decision-audits/YYYY-MM-DD-<slug>.md`:

```markdown
# Decision Audit — {slug}

**Date:** {today} | **Mode:** {same-session / fresh-session} | **Scope:** {diff scope}
{If fresh-session without a log: note that self-report was unavailable.}

## Triaged Decisions
{Per decision: ID, one-line summary, source, verdict, rationale, fix applied (if any).}

## Presumed Sound
{Batch-listed matched low-risk decisions.}

## Fix List
{Queued large revisions/reverts, if any — concrete enough to hand to /deep-implement.}
```

If the fix list is non-empty, suggest: "To implement the queued fixes, run `/deep-implement`
and point it at this report."

## Edge Cases

- **No decisions found by either pass** — say so; no report file needed.
- **Decision log exists but does not match the current branch/diff** — note the mismatch,
  ignore stale entries, and proceed with the cross-check extraction.
- **User rejects the scope in Phase 1** — ask for the intended range and re-scope.
