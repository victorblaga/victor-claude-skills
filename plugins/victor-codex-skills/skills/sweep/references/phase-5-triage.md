# Phase 5 — Triage

HIGH-blast findings get individual verdicts. Two modes (recorded in `scope.md` at Phase 1):

- **Interactive (default)** — one-by-one conversational walkthrough; the user gives verdicts.
- **Auto** — a top-tier Adjudicator subagent renders verdicts under a conservative rubric. See "Auto Mode" at the end of this file; the queue construction, state format, and verdict mechanics below apply to both modes.

State lives in `triage.md` so the session is resumable.

## Triage Queue Construction

1. Read `calibration.md` HIGH-blast findings
2. Read `kicked-to-triage.md` (Phase 4 vetoes) — prepend these to the queue, tagged as `[Applier-vetoed]`
3. Sort the queue by: Applier-vetoed first, then by dimension in a sensible order (CS and DC last — least-judgment findings).

Suggested triage order within the HIGH pool (highest judgment first):
1. Applier-vetoed
2. Defensive Code (DF)
3. Legacy / Fallback (LF)
4. Weak Types (WT) with structural implications
5. Duplication (DU) with extraction proposals
6. Type Consolidation (TC)
7. Circular Deps (CD)
8. Dead Code (DC) — only the HIGH ones (reflection-risky, etc.)
9. Comment / Slop (CS) — only if any reached HIGH (rare)

## Initialize triage.md

Write `{OUTPUT_DIR}/triage.md`:

```markdown
# Triage

Mode: interactive | auto
Total HIGH-blast findings: N
Status legend: ⏳ pending · ▶ in-progress · ✓ applied · ✗ rejected · ⏸ deferred

## Queue

| # | ID | Dim | Title | Status |
|---|----|----|-------|--------|
| 1 | DF-3 | defensive-code | Broad except in csv ingest | ⏳ |
| 2 | LF-1 | legacy-fallback | v1 parser still referenced | ⏳ |
| ... |

## Walkthrough

(Each finding's walkthrough block is appended here as triage progresses.)
```

## Per-Finding Walkthrough Format

For each finding, print to the conversation (interactive) or include in the Adjudicator's input (auto):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Finding N of M — {ID}: {title}
Dimension: {dimension(s) that flagged this}
Location: file_path:line_range

## Current code

```<lang>
(snippet from the actual file — re-read freshly, not just the finding text)
```

## Proposed fix

{what the agent suggests, concisely}

## Blast radius: HIGH

{Calibrator's rationale — files affected, control flow impact, etc.}

## Context

{Re-read the surrounding code and callers; summarize in 2-4 sentences:
- Why does this code likely exist?
- What calls/uses it?
- What pattern is it part of?}

## Impact analysis

**If changed:** {failure modes, behavior shifts, caller impact}
**If kept:** {cruft that persists, signal that stays hidden, future work that's blocked}

## Your call

accept · reject · defer · modify (describe the change)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Mark the finding `▶ in-progress` in `triage.md` table while awaiting the verdict.

## Verdict Handling

### accept

1. Apply the proposed fix. For single-file changes, edit directly. For multi-file changes (extraction, type consolidation, import-cycle break), make all edits atomically.
2. If the fix is complex enough to warrant its own verification, run the relevant tests.
3. Commit with message: `cleanup/{dimension}: {ID} — {short title}` (per-finding granularity here — HIGH-blast changes deserve individual commits; in auto mode this is also what makes autonomous revert-and-defer possible in Phase 6).
4. Update `triage.md`: mark `✓ applied` with commit SHA.
5. Append the walkthrough block to the Walkthrough section of `triage.md` with the verdict.

### reject (interactive mode only)

1. Offer to place an inline `cleanup-sweep-skip` marker at the location. Format per `references/markers.md`:

   ```
   I'll add a marker so future sweeps skip this. Draft rationale:
   
     # cleanup-sweep-skip: orchestrator requires this to swallow (edit the reason if you want a better one)
   
   Accept marker / edit rationale / skip marker placement?
   ```

2. On accept: Edit the file to add the marker on the line/block immediately above the code (per `references/markers.md` placement rules). Commit with message: `cleanup: mark skip for {ID} — {short title}`. This is a separate commit so future cleanup or git blame stays clean.
3. On "skip marker placement": do not add a marker; just record rejection in `triage.md`. Note: without a marker, this will re-surface on the next sweep.
4. Update `triage.md`: mark `✗ rejected`, note whether marker was placed.

### defer

1. Do NOT place a marker. The finding will re-surface on next sweep (that's the point of defer).
2. Update `triage.md`: mark `⏸ deferred` with the rationale.
3. No commit.

### modify (interactive mode only)

1. Ask the user for the modified fix. Echo it back for confirmation.
2. Apply the modified fix, commit: `cleanup/{dimension}: {ID} (modified) — {short title}`
3. Update `triage.md`: mark `✓ applied (modified)` with the modified description and commit SHA.

## User Shortcuts (interactive mode)

Support bulk-verdict shortcuts when the user wants to move fast:

- `"accept all remaining"` — mass-accept everything left in the queue. Warn: "This applies N findings without individual review. Confirm?"
- `"reject all remaining"` — mass-reject. Offer to place markers for all. Same warning.
- `"defer rest"` — mass-defer. No commits, no markers.
- `"skip to <ID>"` — jump to a specific finding.
- `"show me the full Calibrator note for this one"` — print the raw Calibrator entry before your rendered walkthrough.
- `"adjudicate the rest"` — switch to auto mode for the remainder of the queue (Adjudicator subagent, rules below).

## Auto Mode — Adjudicator Subagent

When the sweep runs in auto mode (or the user says "adjudicate the rest"), a fresh subagent on the flagship-tier model (Sol-class) with `reasoning_effort: "xhigh"` renders verdicts instead of the user. Fresh context matters: the Adjudicator must not inherit the dimension agent's enthusiasm for its own finding — same reason the Calibrator re-judges blast radius.

Batch findings sensibly (e.g., 5–10 per Adjudicator invocation, grouped by dimension) so each gets genuine attention; one subagent per finding is acceptable for short queues.

### Invariants

1. **Verdict set is accept / defer only. Never reject.** Rejection places a `cleanup-sweep-skip` marker, and markers encode *human* rationale that suppresses the finding from all future sweeps. A wrong auto-reject silently poisons every future run; a wrong defer merely re-surfaces next time. Defer is the safe failure mode.
2. **No markers are ever placed in auto mode.**
3. **Critical-path findings always defer** — auth, security, payments, data persistence/integrity, concurrency primitives — regardless of how confident the analysis is.
4. **If Phase 1 recorded no test command, defer everything.** No verification safety net means nothing gets accepted unsupervised.

### Adjudicator Prompt

```
You are the sweep Adjudicator. HIGH-blast cleanup findings normally get a human verdict; this sweep runs unattended, so you decide — under a deliberately conservative rubric. Your verdicts are accept or defer. You cannot reject.

**Findings to adjudicate:** {walkthrough blocks, rendered per the Per-Finding Walkthrough Format, with freshly re-read code}
**Scope and conventions:** {from scope.md}
**Baseline test command:** {command} (baseline {green|red-with-known-set})

For each finding, re-read the actual code and its callers yourself — do not trust the finding text alone. Then apply this rubric. ACCEPT only if ALL hold:

1. You can articulate specifically why the failure mode the code guards against is impossible, or why the removal/change cannot alter externally visible behavior.
2. The affected code path is exercised by the test suite (name the tests, or the module's test file), so a mistake would be caught in Phase 6.
3. The finding is not in a critical path (auth, security, money, data persistence/integrity, concurrency).
4. The fix is mechanically unambiguous — no design choice you'd be making on the user's behalf.

Anything less — "probably fine", "seems unused", "tests likely cover this" — is a DEFER. In unattended mode the worst outcome must be "fewer changes applied", never "wrong change applied unsupervised".

**Output per finding:**

### {ID}: {accept | defer}
- **Rationale:** (2-4 sentences; for accept, address all four rubric points explicitly)
- **Tests covering this path:** (for accept — named)

You modify no code. The orchestrator applies accepted findings.
```

### Orchestrator handling of Adjudicator verdicts

- **accept** → apply per the standard accept flow above (per-finding commit). Record `✓ applied (auto-adjudicated)` in `triage.md` with the Adjudicator's rationale.
- **defer** → record `⏸ deferred (auto-adjudicated)` with rationale. These findings are the headline of the report's "for human review" section.

## Resume

If `triage.md` exists on session start, read which findings are `⏳`/`▶`/`✓`/`✗`/`⏸`:
- `⏳`: pending — resume from the lowest-numbered pending
- `▶`: in-progress — assume abandoned mid-walkthrough; re-present as a fresh walkthrough
- `✓`/`✗`/`⏸`: already handled, skip

## Phase 5 Exit Criteria

- [ ] Every finding in the queue has a non-pending status (`✓`, `✗`, or `⏸`)
- [ ] `triage.md` is complete with the full walkthrough/adjudication log
- [ ] All accept/modify fixes committed (one commit per finding)
- [ ] All reject markers placed (interactive mode; unless user explicitly declined per-finding)
- [ ] `status.md` updated

Announce: *"Phase 5 complete. Accepted: A, Modified: M, Rejected: R (P markers placed), Deferred: D. Entering Phase 6 verification."* Read `references/phase-6-verify.md` before proceeding.
