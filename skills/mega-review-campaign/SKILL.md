---
name: mega-review-campaign
description: >
  Execute, resume, and synthesize a multi-unit review from a frozen mega-review-atlas: one
  mega-review per unit and seam, horizontal sweeps, drift detection, idempotent resume, and
  a system-level synthesis that preserves every per-unit report. Read-only — changes no
  code. Trigger only when the user explicitly says "mega-review-campaign" or invokes
  /mega-review-campaign.
---

# Mega Review Campaign

Run the reviews a frozen `mega-review-atlas` planned: one `mega-review` (unit-packet mode) per selected unit and seam, then the declared horizontal sweeps, then a system-level synthesis. Mechanical, expensive, resumable. `mega-review` stays the review engine — this skill never redefines its dimensions, verification, or calibration.

**READ-ONLY.** Never modify project code. Output is the campaign directory only.

Non-negotiables:

- **A frozen atlas is required.** A draft atlas, or none, → stop and direct the user to `/mega-review-atlas`. Never silently repair or reinterpret a malformed atlas.
- **No review under drift.** If the working tree no longer matches the atlas fingerprint where it matters, affected items are `stale`, not reviewed.
- **Per-unit reports are the record.** The system report indexes and synthesizes them; it never replaces them.
- **"Complete" is earned.** Never a synonym for "the orchestrator stopped."

## Parse the Request

1. **Atlas** — a path to an atlas directory, or find the newest under the scratch atlases directory. Validate before anything else (Step 0).
2. **Mode** — `full` (default), `selection` (named nodes plus every seam incident to a selected unit, far endpoint as context), `resume`, `delta` (after code changed: requires a **refreshed** atlas covering the changed region — see the delta rules), or `status` (read-only progress report, then stop).
3. **Output directory** — `.scratch/docs/reviews/campaigns/YYYY-MM-DD-<target>-XXXXX/` (same scratch-root, suffix, and gitignore rules as `mega-review`; the atlas ID lives in `campaign-status.json`). `resume`/`status` reuse the existing directory.

Campaign directory contents:

```
campaign.md            # execution plan: every selected item + skip rationales
campaign-status.json   # state machine — one entry per item, updated after every transition
units/<id>/            # unmodified mega-review output dir per unit
seams/<id>/  sweeps/<id>/
findings-index.md      # normalized findings, provenance preserved
campaign-synthesis.md  # cross-unit tensions, patterns, evidence gaps
report.md              # final system review
reviewed-at.json       # final fingerprint + completion status
```

## Execution

| Step | Purpose | Reference |
|------|---------|-----------|
| **0 — Load & validate** | Frozen atlas, drift check, state | `references/campaign-protocol.md` |
| **1 — Plan** | Select items, order, record skips | `references/campaign-protocol.md` |
| **2 — Pilot** | One unit + one seam prove the decomposition | (below) |
| **3 — Units, seams, sweeps** | Sequential mega-review runs | `references/campaign-protocol.md` |
| **4 — Normalize & verify** | Dedup, cross-unit fact-check | `references/campaign-synthesis.md` |
| **5 — Synthesize & gate** | System report + completion gate | `references/campaign-synthesis.md` |

### Step 0: Load & Validate

Read `references/campaign-protocol.md` (validation + drift rules). Read repository instructions, `frozen-at.json`, `atlas.md`, `runtime-profile.md`, and packet paths (not all packet bodies). Run the drift check. Create or resume `campaign-status.json`.

### Step 1: Plan

Select items per mode; every selected item gets a status entry, every skipped reviewable node a recorded rationale in `campaign.md`. Order (pilot always first; the rest is a default — adapt with reason): pilot → highest-risk stateful/destructive units → shared capabilities → remaining leaves → seams → sweeps. Present the plan (item count, order, estimated mega-review runs) and get user confirmation before Step 2 — this is the expensive part.

### Step 2: Pilot

Run one representative medium-sized unit and one adjacent seam through `mega-review` first. Inspect only each run's `review-plan.md`, `review-summary.md`, and artifact existence — not bulk findings. Pass criteria, each checkable from those inputs: every `Locations:` entry in the summary falls inside the packet's primary scope (context-only code produced no findings of its own); the guarantee and invariants sufficed as intent; every dimension's `Scope fit:` line reads `ok`.

Fail → mark the campaign `blocked` with a concrete atlas revision request and stop. Never silently split a frozen unit.

### Step 3: Execute Units, Seams, Sweeps

**One mega-review at a time** — each run already fans out internally. The parallel-batch exception is defined in `references/campaign-protocol.md`. For each item, follow the invocation contract in `references/campaign-protocol.md`; record every status transition in `campaign-status.json` immediately.

The orchestrator reads per-run `review-summary.md` receipts only — never full reports. Retry a missing-artifact or procedural failure once, keeping both attempts' receipts; a second failure marks the item `failed`.

### Steps 4–5: Normalize, Synthesize, Gate

Read `references/campaign-synthesis.md`. Normalize findings with provenance, dedup and cluster across units, verify newly inferred cross-unit claims, then write `campaign-synthesis.md` and `report.md`, and apply the completion gate. Final status is one of:

- `complete` — all selected items done, no drift, no unresolved required evidence
- `complete_with_evidence_gaps` — code review done; named operational facts remain unverifiable
- `blocked` — a required item cannot proceed (includes pilot failure)
- `stale` — source drifted mid-campaign; completed compatible items keep their results

Report to the user: status, counts (complete/failed/blocked/stale/skipped), verdict, top cross-unit tensions, evidence gaps, and paths. Point to `/review-triage` for walking the findings.

## Cross-Skill Boundaries

| If the user wants... | Use... |
|----------------------|--------|
| Execute reviews from a frozen atlas | **mega-review-campaign** (this skill) |
| Build or refresh the atlas | `mega-review-atlas` |
| Review one diff / PR directly | `mega-review` |
| Triage findings into a plan | `review-triage` |
| Implement accepted fixes | `deep-implement` |
