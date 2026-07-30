# Campaign Protocol

Validation, drift, state, and the mega-review invocation contract.

## Atlas validation (Step 0)

Refuse to proceed — with a specific message and a pointer back to `/mega-review-atlas` — when any of these fail:

1. `frozen-at.json` exists with `"status": "frozen"`.
2. `atlas.md` exists and its atlas ID matches `frozen-at.json`.
3. Every reviewable node in `atlas.md` has a packet file under `units/`.
4. `coverage.md` exists and is non-empty.
5. `mega-review` is installed and its SKILL.md documents **unit-packet mode**.

Do not repair, reinterpret, or "work around" a failing atlas. The fix happens in the atlas skill.

## Drift check (Step 0, and before dispatching each item)

Compare current `HEAD` and working-tree state against `frozen-at.json`:

- Identical HEAD, clean tree → proceed. (a dirty tree is drift by definition — ask the user to commit or stash)
- Drifted → diff the frozen SHA against current state; any item whose **primary scope** intersects changed paths/symbols is `stale`. A changed contract also stales its incident seams and the dependent units the atlas names on that edge. Non-intersecting items proceed.
- All or most items stale → stop; direct the user to refresh the atlas.
- **Historical-review mode** (reviewing the frozen revision itself) is allowed only in a worktree at the exact frozen SHA that the user supplies or approves.

## campaign-status.json

```json
{
  "campaign_id": "<dir name>",
  "atlas_id": "<atlas id>", "atlas_head": "<frozen sha>",
  "mode": "full", "status": "planned | running | complete | complete_with_evidence_gaps | blocked | stale",
  "items": [
    {"id": "<node-id>", "kind": "unit | seam | sweep",
     "status": "pending | running | complete | failed | blocked | stale | skipped",
     "packet": "<path>", "output_dir": "<path>",
     "attempts": 0, "started_at": null, "completed_at": null,
     "finding_counts": null, "failure_reason": null, "skip_rationale": null}
  ]
}
```

Rewrite the whole file after **every** transition (write to a temp file in the campaign dir, then rename). This file is what makes resume idempotent; `campaign.md` is its human-readable projection plus rationales.

## Mega-review invocation contract (Steps 2–3)

Each item runs as **one fresh flagship-class subagent** whose job is to invoke the installed `mega-review` skill in unit-packet mode — the orchestrator never runs a review inline (it would flood its own context) and never re-implements the review procedure in the prompt. The subagent runs non-interactively and replies with a ≤3-line receipt; everything of substance lands in the output directory.

Dispatch prompt template (adapt paths, keep the shape):

```
Invoke the mega-review skill in unit-packet mode. Non-interactive: never ask the user
anything; record unknowns as "unconfirmed".

- Packet (defines all scope — do not widen or reconstruct): <packet path>
- Output directory: <campaign dir>/units/<id>/
- Runtime context: <runtime-profile.md path> — scenarios <names>, with their evidence statuses
- Finding namespace: prefix every finding ID with "<node-id>::"
- Prior decisions: <notes.md path, if any>
- Prior evidence: <path + fingerprint of reusable campaign-level evidence results, if valid>

When done, reply with only: item ID, finding counts by severity, and the report path.
```

Notes beyond what the template shows:

- **Packet:** passed verbatim — scope, intent, invariants, dimensions, exclusions all come from it; never reconstruct scope.
- **Prior evidence:** pass only when still valid for reuse (see evidence reuse below).

Seams run through the same contract; the packet already marks which endpoint is primary vs context.

**Sweeps** also run through mega-review unit-packet mode, but with only the dimensions the sweep declares (usually one), the sweep's question as intent, and the exact unit/symbol list from its packet as scope. Never widen a sweep to "the whole repo".

**Evidence reuse:** if a broad evidence command (full test suite, typecheck, lint) already ran this campaign at the same source state, later items receive its result path via the Prior evidence input instead of rerunning it. Reuse requires the same HEAD, a clean tree, and the same command; otherwise rerun.

After each run, validate that `report.md` exists and is non-empty in the item's output dir before marking `complete` and recording finding counts from the run's summary.

## Resume and delta rules

- **Resume** selects `pending`, `running` (crashed mid-run — reset and rerun), `failed` (one more attempt max), and newly `stale`-cleared items. A completed item is reusable only when its packet is unchanged and its source fingerprint still matches; never rerun completed compatible items just because the process restarted.
- **Atlas rebinding (resume):** stale items can only be revived through a refreshed frozen atlas. When the user points a resume at one, compare packets: byte-identical packet → the completed result carries over; changed or new packet → the item resets to `pending`. Update `atlas_id`/`atlas_head` in `campaign-status.json` and record the rebind in `campaign.md`.
- **Delta** (after code changed) requires a **refreshed frozen atlas** covering the changed region — the "no review under drift" rule has no delta exception; the drift check runs against the refreshed fingerprint. Rebind as above, then select: units owning changed symbols, seams incident to changed contracts, and sweeps whose declared scope intersects the changes. Everything else keeps its completed results. A changed runtime profile additionally stales assumption-sensitive findings (performance, architecture, capacity) but not local factual-correctness findings — note this in the synthesis rather than rerunning whole units.
- **Status** mode prints per-item status, counts, and remaining work from `campaign-status.json`, then stops.

## Concurrency & context economy

- Default: one mega-review at a time (each fans out ~10+ subagents internally). A small parallel batch is allowed only with demonstrated independent harness capacity and no shared evidence resources (databases, ports, containers, generated files).
- The orchestrator reads: atlas metadata, packets for dispatch, run receipts/summaries, `findings-index.md`. It never inlines full unit reports or bulk source. Unit agents read implementation; synthesis reads normalized findings plus only the source needed to verify inferred cross-unit relationships.

## Capability classes

As in `mega-review`: do not hardcode model names. Item dispatch subagents run at flagship class; the Normalizer runs mid tier; cross-unit verification and synthesis run at flagship/xhigh (see `campaign-synthesis.md`). Planning, dispatch bookkeeping, and status reporting are orchestrator work — no subagents.
