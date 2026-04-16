# Phase 5 — Triage

One-by-one conversational walkthrough of HIGH-blast findings. Main thread walks; user gives verdicts; each verdict is applied (or recorded + markered) before moving to the next finding. State lives in `triage.md` so the session is resumable.

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

For each finding, print to the conversation:

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

Mark the finding `▶ in-progress` in `triage.md` table while awaiting user verdict.

## Verdict Handling

### accept

1. Apply the proposed fix. For single-file changes, edit directly. For multi-file changes (extraction, type consolidation, import-cycle break), make all edits atomically.
2. If the fix is complex enough to warrant its own verification, run the relevant tests.
3. Commit with message: `cleanup/{dimension}: {ID} — {short title}` (per-finding granularity here, not reworded — HIGH-blast changes deserve individual commits).
4. Update `triage.md`: mark `✓ applied` with commit SHA.
5. Append the walkthrough block to the Walkthrough section of `triage.md` with the verdict.

### reject

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
2. Update `triage.md`: mark `⏸ deferred` with the user's rationale if they gave one.
3. No commit.

### modify

1. Ask the user for the modified fix. Echo it back for confirmation.
2. Apply the modified fix, commit: `cleanup/{dimension}: {ID} (modified) — {short title}`
3. Update `triage.md`: mark `✓ applied (modified)` with the modified description and commit SHA.

## User Shortcuts

Support bulk-verdict shortcuts when the user wants to move fast:

- `"accept all remaining"` — mass-accept everything left in the queue. Warn: "This applies N findings without individual review. Confirm?"
- `"reject all remaining"` — mass-reject. Offer to place markers for all. Same warning.
- `"defer rest"` — mass-defer. No commits, no markers.
- `"skip to <ID>"` — jump to a specific finding.
- `"show me the full Calibrator note for this one"` — print the raw Calibrator entry before your rendered walkthrough.

## Resume

If `triage.md` exists on session start, read which findings are `⏳`/`▶`/`✓`/`✗`/`⏸`:
- `⏳`: pending — resume from the lowest-numbered pending
- `▶`: in-progress — assume abandoned mid-walkthrough; re-present as a fresh walkthrough
- `✓`/`✗`/`⏸`: already handled, skip

## Phase 5 Exit Criteria

- [ ] Every finding in the queue has a non-pending status (`✓`, `✗`, or `⏸`)
- [ ] `triage.md` is complete with the full walkthrough log
- [ ] All accept/modify fixes committed
- [ ] All reject markers placed (unless user explicitly declined per-finding)
- [ ] `status.md` updated

Announce: *"Phase 5 complete. Accepted: A, Modified: M, Rejected: R (P markers placed), Deferred: D. Entering Phase 6 verification."* Read `references/phase-6-verify.md` before proceeding.
