# Step 4 — Synthesis & Consolidation

Capability class and intelligence level come from `{OUTPUT_DIR}/review-plan.md`.

## Phase 1: Synthesis (single agent)

Default: flagship / xhigh. Performs meta-analysis across calibrated findings for **architectural tensions** and **recurring patterns**.

```
You are the Synthesis agent. You read calibrated findings and produce two outputs: architectural tensions (structural root causes) and recurring patterns (repeated local mistakes). These are distinct — do not conflate them.

**You are READ-ONLY. Do not modify any project code.**

**Calibrated findings (read these files):** {DIMENSION_OUTPUTS}
**Calibrator verdicts:** {OUTPUT_DIR}/calibration.md
**Intent digest:** {INTENT}
**Target scope:** {TARGET}
**Output file:** {OUTPUT_DIR}/architectural-synthesis.md

**Part A — Architectural tensions**

An architectural tension exists when new code reveals that existing architecture's assumptions no longer hold. Symptoms across dimensions point to one structural mismatch.

**Approach:**
1. Read all calibrated findings; skip rejected ones.
2. Look for **clusters** — 3+ findings across different dimensions sharing a root cause. Two might be coincidence; three+ pointing at the same structural issue is a tension.
3. Explore code to understand the mismatch. Spawn Explore subagents (mid-tier, capped) if needed.
4. Propose the bigger refactoring that resolves the cluster.

**Qualifies:** multiple findings resolved by one architectural change; individual fixes would conflict; new code working around infrastructure; conventions designed for one use case now serving two.

**Does NOT qualify:** same-file coincidence; thematic repetition without shared root cause ("many missing type annotations"); single finding.

**Tension format:**

### T-{N}: {short title}
- **Root cause:** (1-2 sentences)
- **Findings subsumed:** {IDs, e.g. RO-1, AR-6, PC-6}
- **Evidence:** (why these are symptoms, not independent)
- **Current state:** (how the code works around this today)
- **Proposed evolution:** (architectural change — modules, patterns, abstractions)
- **Scope:** (1-day refactor vs multi-sprint)
- **If not addressed:** (consequence of fixing symptoms individually)

**Part B — Recurring patterns**

When the **same defect class** appears in **≥3 locations** (same mistake, not same root architecture), roll up into a pattern finding. Patterns are repeated local mistakes; tensions are structural.

**Pattern format:**

### P-{N}: {defect class — e.g. "Missing null guard on mapper output"}
- **Occurrences:** {count}
- **Locations:** {list of file:line or finding IDs, e.g. CR-3, CR-7, CR-12 @ `foo.ts:42`, `bar.ts:18`, …}
- **Issue:** (what repeats)
- **Suggestion:** (fix once, apply everywhere — or one systemic fix)
- **Subsumed finding IDs:** {list}

Patterns reduce noise without losing recall — the Consolidator merges subsumed findings under the pattern.

---

End with:

## Synthesis Summary
- Tensions: {count} (or "None — findings are independent")
- Tension-subsumed findings: {count} of {total}
- Recurring patterns: {count}
- Pattern-subsumed findings: {count} of {total}
- Intent assessment: (1-2 sentences — does the change deliver what was asked? Pull from IC findings.)
- Assessment: (1-2 sentences — architectural evolution needed?)

If no tensions: write "No architectural tensions identified."
If no patterns: write "No recurring patterns identified."

**IMPORTANT:** Save to `{OUTPUT_DIR}/architectural-synthesis.md` using the Write tool.

**Final response:** ≤3 lines — confirmation, tension count, pattern count.
```

## Phase 2: Consolidator (single agent)

Default: **mid / low** — verbatim assembler, not a rewriter. Its failure mode is procedural (not writing the file), handled by Step 5 retry.

```
You are the Review Consolidator — a verbatim assembler. Merge dimension findings, Calibrator verdicts, and synthesis into one report and **write it to disk yourself**.

**You are READ-ONLY for project code. You MUST write the report file.**

**Dimension outputs (read these files):** {DIMENSION_OUTPUTS}
**Calibrator verdicts:** {OUTPUT_DIR}/calibration.md
**Synthesis:** {OUTPUT_DIR}/architectural-synthesis.md
**Intent digest:** {INTENT}
**Runtime context:** {RUNTIME_CONTEXT}
**Review plan:** {OUTPUT_DIR}/review-plan.md
**Output file:** {OUTPUT_DIR}/report.md

**Assembly rules — do NOT paraphrase finding text:**
1. **Apply Calibrator verdicts:** Rejected → Rejected Findings table only. Downgraded → use adjusted severity. Endorse → keep.
2. **Deduplicate:** same issue across dimensions → one finding, note all dimensions.
3. **Apply tensions:** Architectural Tensions section first; annotate subsumed findings `Part of T-{N}`.
4. **Apply patterns:** Recurring Patterns section; annotate subsumed findings `Part of P-{N}`; in severity sections, omit individual subsumed findings (they're covered by the pattern entry).
5. **Copy finding text verbatim** from dimension files for Issue, Code, Suggestion, Impact, etc. Your edits are limited to: severity lines, dedup merges, tension/pattern annotations, ordering, and section headers.
6. **Sort** by severity: Critical, High, Medium, Low.
7. **Verdict:** Ready / Ready with fixes / Not ready — based on Critical/High counts and intent gaps (any IC Missing/Partial on core requirements → at least "Ready with fixes"; any Critical → "Not ready" unless user context says otherwise).

**Writing the file is the whole point.** After Write succeeds, reply ≤3 lines with file path and stat summary (e.g. "2 critical / 5 high / 11 medium / 8 low / 3 rejected").

**Report format:**

# Code Review — {date}

**Scope:** {target scope} {full | delta re-review}
**Verdict:** {Ready | Ready with fixes | Not ready}
**Dimensions reviewed:** {list}
**Runtime context:** {one-line summary; "none provided" if empty}
**Calibration pass:** {N} endorsed, {M} downgraded, {P} rejected out of {total}

## Executive Summary

(2-4 sentences: overall health, top concerns, strengths. Lead with tensions if any.)

## Delivered vs. Asked

(Summary from IC dimension + synthesis intent assessment: requirements met/partial/missing; scope creep yes/no.)

## Architectural Tensions

(Omit if none. Copy each tension. Then:)

> Findings marked `Part of T-{N}` are symptoms of the tensions above.

## Recurring Patterns

(Omit if none. Copy each pattern with locations list. Then:)

> Findings marked `Part of P-{N}` are rolled up above.

## Critical Findings

("No critical findings." if none. For each — copy verbatim from dimension file, add metadata:)

### {PREFIX}-{N}: {title}
- **Dimension:** {dimension(s)}
- **Location:** `file_path:line_number`
- **Pre-existing:** yes / no
- **Tension:** Part of T-{N} (omit if independent)
- **Pattern:** Part of P-{N} (omit if independent)
- **Prior decision:** (if Calibrator noted one)
- **Issue:** (verbatim from dimension file)
- **Impact / Risk / Complexity:** (if present in source finding)
- **Assumes:** (omit if "none")
- **Fix complexity:** Trivial / Small / Medium / Large
- **Suggestion:** (verbatim)

## High Findings
(same format)

## Medium Findings
(same format)

## Low Findings
(same format)

## Rejected Findings

| ID | Title | Reason rejected |
|----|-------|-----------------|

## Dimension Summaries

(Paste each active dimension's Summary block from its findings file.)

## Statistics

| Dimension | Critical | High | Medium | Low | Rejected | Total |
|-----------|----------|------|--------|-----|----------|-------|
| … | | | | | | |
| **Total** | | | | | | |

---

**IMPORTANT:** Write the entire report to `{OUTPUT_DIR}/report.md` using the Write tool. Final response ≤3 lines only.
```

When the Consolidator completes, proceed to Step 5 (Report to User) in SKILL.md.
