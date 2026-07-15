# Phase 7 — Report

Final summary. Three components: report file, marker-age nudge, optional test-sweep nudge.

## Generate `report.md`

The orchestrator writes the report inline — it's a small aggregation of session files already at hand (`status.md`, `scope.md`, `calibration.md`, `auto-apply.md`, `triage.md`, `kicked-to-triage.md`); spawning a subagent costs more than the work. Write to `{OUTPUT_DIR}/report.md`:

**Format:**

# Sweep Report — YYYY-MM-DD

Branch: <branch>
Scope: <target>
Mode: interactive | auto
Languages: <detected>
Tools used: <list>
Duration: <start — end> (from status.md timestamps)

## Outcome

<one-paragraph narrative summary: how many findings, how many applied, how many rejected/deferred, CI status>

## Statistics

| Dimension | Raw | After dedup | LOW applied | HIGH applied | HIGH rejected | HIGH deferred | Vetoed |
|-----------|-----|-------------|-------------|--------------|---------------|---------------|--------|
| Duplication | | | | | | | |
| Type Consolidation | | | | | | | |
| Dead Code | | | | | | | |
| Circular Deps | | | | | | | |
| Weak Types | | | | | | | |
| Defensive Code | | | | | | | |
| Legacy / Fallback | | | | | | | |
| Comment & Slop | | | | | | | |
| **Total** | | | | | | | |

## Commits produced

(ordered list of commits from this sweep, with shas and messages)

## Markers placed

(for each reject-with-marker: file:line + rationale)

## Deferred findings

(list of deferred findings for follow-up attention — these will re-surface on next sweep)

## Auto-adjudication (auto mode only)

- Accepted: N findings, each with the Adjudicator's rationale and the tests covering the path
- Deferred for human review: M findings with rationale — **this is the section a human should read first after an unattended run**
- Reverted in Phase 6 (if any): findings whose commits were reverted-and-deferred, with the failing check

## CI status

<result from Phase 6>

## Open items

(anything outstanding: Applier vetoes that weren't triaged, CI failures not fixed, rejected findings without markers placed)

## Marker-age Nudge

After writing the report, run the marker scan and append / print an age-nudge block:

```bash
rg -n "cleanup-sweep-skip" <repo-root> -g '!.docs/**' -g '!node_modules/**' -g '!.venv/**'
```

Parse each match for the trailing `(YYYY-MM-DD)`. Compute age. Classify:
- Fresh (< 3 months): count
- Seasoned (3-12 months): count
- Stale (> 12 months): count, list with location + rationale

Print at end of Phase 7 (and append to `report.md`):

```
## Active cleanup-sweep-skip markers

Total: N markers
- Fresh (<3mo): X
- Seasoned (3-12mo): Y
- Stale (>12mo): Z

Stale markers to consider revisiting:
  - src/ingest/csv.py:142 (2024-11-03, 17 months) — "API backwards-compat through 2026-Q4"
  - src/api/legacy.py:1 (2025-02-14, 14 months) — "orchestrator retries on this catch"
  - ...

The original rationales may no longer apply. No action taken automatically.
```

If there are no markers, skip this block.

## Test-sweep Nudge

In auto mode, skip the nudge — note in the report: *"Test-tree sweep not run. Re-run with `$sweep tests/` when ready."* Interactive mode: if the main sweep excluded tests (default behavior), ask:

```
Main sweep complete.

Tests were excluded from this sweep by default (they legitimately repeat setup, use broad except, have extra comments).

Want me to run the same sweep against the test tree now with relaxed rules? (tests/, test_*/, *_test.* patterns)

[yes / no / later]
```

- **yes** — re-invoke the skill with scope set to test directories and a "relaxed test-sweep" flag that softens:
  - Duplication threshold (tests may legitimately repeat fixtures)
  - Defensive code (tests often have broad exceptions in assert helpers)
  - Slop comments (tests have more scaffolding comments that are acceptable)
- **no** — done. Print the final summary and exit.
- **later** — done. Note in the report: *"Test-tree sweep deferred. Re-run with `$sweep tests/` when ready."*

## Final Summary to User

Print a terse summary to the conversation:

```
Sweep complete.

Branch: <branch>
Mode: <interactive | auto>
Findings applied: X (LOW auto-apply) + Y (HIGH triaged/adjudicated)
Rejected with markers: R (interactive only)
Deferred (will re-surface next run): D
Commits: <sha-start>..<sha-end>
CI status: <result>

Report: .docs/cleanup/<session>/report.md
```

Offer next steps:

```
Next:
- Push branch: git push -u origin <branch>
- Open PR (or use $deep-implement if you want a formal PR flow)
- Run sweep on tests: $sweep tests/
```

## Phase 7 Exit Criteria

- [ ] `report.md` written
- [ ] Marker age nudge printed (if any markers exist)
- [ ] Test-sweep nudge offered
- [ ] Final summary printed to conversation
- [ ] `status.md` marked `Phase: complete`

After all exit criteria: the sweep is done. Do not initiate any further actions without user direction.
