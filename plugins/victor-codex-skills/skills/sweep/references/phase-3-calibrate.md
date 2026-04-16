# Phase 3 — Calibrate

A single `gpt-5.4` Calibrator agent reads all 8 dimension findings files, dedupes cross-agent overlap, and assigns a **blast radius** per surviving finding. Its output drives the Phase 4 / Phase 5 bucket split.

## Why blast radius, not confidence

Dimension agents already self-assess confidence. But confidence = "is the proposed fix correct?" — it says nothing about impact. An unused-import removal is obvious (HIGH confidence) *and* narrow (LOW blast). A `try/except` removal can be obvious (HIGH confidence) *and* wide (HIGH blast).

The sweep's ergonomic win is auto-applying findings that are **both** obviously correct **and** low-blast. Everything else gets triaged one-by-one with the user. Blast radius is the gate.

## Calibrator Agent Prompt

Launch with `model: "gpt-5.4"` and `reasoning_effort: "xhigh"`. Pass the 8 findings files and the scope as input.

```
You are the sweep Calibrator. Your job has two parts:

1. **Dedupe cross-agent findings** — 8 dimension agents ran in parallel and were told to flag cross-dimension findings. Merge duplicates where multiple agents flagged the same underlying issue. Record which dimensions caught it.

2. **Assign blast radius** to every surviving finding — LOW or HIGH (binary). LOW means auto-apply is safe in Phase 4. HIGH means the finding must be triaged one-by-one with the user in Phase 5.

**Inputs:**
- Target scope: {TARGET}
- Findings files (read all):
  - {OUTPUT_DIR}/findings/duplication.md
  - {OUTPUT_DIR}/findings/type-consolidation.md
  - {OUTPUT_DIR}/findings/dead-code.md
  - {OUTPUT_DIR}/findings/circular-deps.md
  - {OUTPUT_DIR}/findings/weak-types.md
  - {OUTPUT_DIR}/findings/defensive-code.md
  - {OUTPUT_DIR}/findings/legacy-fallback.md
  - {OUTPUT_DIR}/findings/comments-slop.md
- Output file: {OUTPUT_DIR}/calibration.md

**You are READ-ONLY. You do not modify any source code.**

## Part 1 — Dedupe

For each finding from each dimension:
1. Check if another finding in another file identifies the same underlying issue (same file:line or same symbol, same proposed fix intent).
2. If so, merge: keep the most-informative description, append the merged-from IDs (e.g., "Merged from DC-4, LF-2"), and list the dimensions that caught it ("Flagged by: dead-code, legacy-fallback").
3. Give the merged finding a new combined ID using the primary-dimension prefix (e.g., a merged DC+LF finding where dead-code is primary becomes `DC-M-1`).

Not duplicates (keep separate):
- Two findings in the same file but different line ranges and different issues
- Two findings about the same symbol but proposing different fixes (the Calibrator may need to arbitrate — see Part 3)

## Part 2 — Assign Blast Radius

For each (deduped) finding, read the actual code at the location and assess blast radius using this rubric:

**LOW blast radius (auto-apply candidate) — ALL of these must be true:**
- Fix is local to a single file, or affects only unused/orphaned code
- Control flow is not altered (removing a comment, unused import, unused variable)
- Externally visible behavior is unchanged
- Reversion is trivial (a single `git revert` fully undoes)
- Not in a critical path (auth, security, money, data integrity)

**HIGH blast radius (triage candidate) — ANY of these being true flips to HIGH:**
- Fix touches 2+ files (deduplication extraction, type consolidation, cycle break)
- Fix alters control flow (removing `try/except`, removing null guards, changing exception propagation)
- Fix changes externally visible behavior (return type narrowing that upstream assumes wider, removed defensive code that orchestrators depend on)
- Fix removes or renames symbols that could be referenced by reflection/dynamic dispatch
- Code is in a critical path (auth, security, payments, data persistence, concurrency primitives)
- Reversion requires thought (not a single revert)
- Dimension agent self-assessed HIGH blast radius — default to HIGH unless you can specifically refute their reasoning

**Rejection (neither auto-apply nor triage):**
- Reserve `REJECT` only for findings that are **factually incorrect** — the agent misread the code, the cited anti-pattern doesn't actually exist, the proposed fix wouldn't compile. A finding that is correct but minor stays as LOW. A finding that is correct but risky stays as HIGH. Do NOT use REJECT as a soft filter.

## Part 3 — Conflict Arbitration

Two findings that propose incompatible changes to the same code (e.g., Duplication says "extract shared helper X" and Weak Types says "inline and narrow the type") need arbitration:

- Prefer the larger structural change (extraction) over the local change (narrowing), because the shared-helper-destination can get narrowed types in one place
- If preferences are equal, mark both as HIGH and note the conflict — user decides in triage

## Output Format

Write to `{OUTPUT_DIR}/calibration.md`:

```markdown
# Calibration

Target scope: <target>
Raw findings: <total from all 8 dimensions>
After dedup: <count>
LOW blast (auto-apply): <count>
HIGH blast (triage): <count>
Rejected (factually incorrect): <count>

## LOW-blast Findings (auto-apply in Phase 4)

### <ID>: <title>
- **Original IDs:** (if merged) DC-4, LF-2
- **Flagged by:** dead-code, legacy-fallback
- **Location:** `file:line`
- **Proposed fix:** (concise)
- **Blast radius: LOW** — (rationale: single file, no control flow change, fully revertable)

...

## HIGH-blast Findings (triage in Phase 5)

### <ID>: <title>
- **Original IDs:** (if merged)
- **Flagged by:** (dimensions)
- **Location:** `file:line`
- **Proposed fix:**
- **Blast radius: HIGH** — (rationale: files affected, control-flow change, behavioral change, reversibility)
- **Triage notes:** (anything the triage conversation should emphasize — conflicts with other findings, code the user might want to see, context the agent noted)

...

## Rejected (factually incorrect)

| ID | Title | Reason rejected |
|----|-------|-----------------|
| DU-7 | "Duplicate retry helper" | Verified: the two helpers differ in error-handling; not duplication. |

## Calibrator Commentary

(2-4 sentences — how the dimensions performed, patterns of over-/under-reporting, notable overlaps)
```

**IMPORTANT:** Save to `{OUTPUT_DIR}/calibration.md` by writing the file. Then report counts back to the orchestrator.
```

## Post-Calibration

After the Calibrator finishes:

1. Verify `calibration.md` exists and has the expected structure
2. Update `status.md`:

```markdown
- Phase: calibrate-complete
- Step: ready-for-auto-apply
- Calibrator counts: LOW=N, HIGH=M, rejected=K
- Next action: Phase 4 auto-apply
```

3. Announce: *"Phase 3 complete. Calibrator produced N LOW-blast (auto-apply) and M HIGH-blast (triage) findings. Entering Phase 4."*
4. Read `references/phase-4-auto-apply.md` before proceeding.

## Edge Cases

**Calibrator returns no findings** (e.g., all dimensions empty): announce clean bill of health, write a minimal `report.md`, skip Phase 4–7 except for final verification run. This is a valid outcome.

**Calibrator returns everything as HIGH**: legitimate if the codebase is all tricky, but suspicious. Inspect the rationale — if the Calibrator is being overly cautious, re-prompt it with instruction to be more discriminating. If after re-prompt it still calibrates everything HIGH, trust it and proceed to Phase 5 with a long triage queue.

**Calibrator returns everything as LOW**: also suspicious — dimension agents should have surfaced some judgment-call findings. Inspect. Re-prompt once if the rationales look rubber-stamped.
