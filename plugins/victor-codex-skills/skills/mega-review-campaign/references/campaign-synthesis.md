# Campaign Synthesis

Normalize findings across runs, verify what the campaign itself infers, write the system report, and apply the completion gate.

Two subagent roles do this work — the orchestrator dispatches and reads receipts, nothing more:

- **Normalizer** (mid tier): input is the list of completed report paths; output is `findings-index.md` written to the campaign dir per the format below; reply is a ≤3-line receipt (row count, duplicate merges, contradictions found).
- **Synthesis/Verification agent** (flagship, xhigh reasoning): input is `findings-index.md`, the atlas runtime profile, and read access to source; it runs the campaign-level verification below and writes `campaign-synthesis.md`; reply is a ≤3-line receipt.

## Normalize (Step 4)

Build `findings-index.md` from every completed run's report. One row per finding:

```markdown
| ID | Severity | Dimension | Location | One-line summary | Source report | Cluster |
```

- **ID** keeps the namespaced identity (`<node-id>::<prefix-n>`). Provenance — the original report path and quoted evidence — must survive every later step; synthesis may add cluster labels but never discards original IDs.
- Unit-level verification remains **authoritative for local claims**. The campaign never re-litigates a calibrated local finding.

Then, across the index:

1. **Duplicates** — the same defect surfacing in several runs (typical for shared capabilities and seams). Merge into one row listing all source IDs; keep the highest calibrated severity.
2. **Clusters** — distinct findings that share a cause (the same missing invariant, the same misused contract, the same slop pattern). Label the cluster; do not merge the findings.
3. **Contradictions** — two runs asserting incompatible facts about the same code. Resolve by reading the code; record which run was wrong.

## Campaign-level verification

Verification applies only to what the campaign adds: dedup merges, contradiction resolutions, cross-unit inferences, and severity changes.

- **Fact-check every newly inferred cross-unit claim** against source before it enters the synthesis — an inference from two correct local findings can still be wrong.
- **Double-verify** (fresh flagship/xhigh check) any campaign-new finding, or any severity raise, landing at Critical or High.
- **Calibrate assumption-dependent clusters** against the runtime profile and its evidence statuses. A risk resting on an `assumed`/`unknown` claim is reported as conditional on that gap, never as established.

Every non-rejected campaign finding must map to verified source findings or to fresh campaign-level evidence.

## campaign-synthesis.md

- **Cross-unit architectural tensions** — with member finding IDs
- **Recurring patterns** — same mistake class across units
- **Global slop profile** — aggregated from per-unit AS findings; dominant classes, estimated removable volume
- **Runtime / performance risks by named scenario**
- **Contract and invariant mismatches** (largely from seam runs)
- **Cohesion / refactoring candidates** — promoted from the atlas overlay **only** where unit/seam findings supply evidence; unevidenced smells stay observations
- **Evidence gaps** — the atlas ledger's gaps plus new ones, as an operator verification checklist

## report.md — system review

An index and synthesis over the per-unit reports, never their replacement:

```markdown
# System Review: <target> — <campaign-id>

## Verdict
<Ready | Ready with fixes | Not ready> — <one paragraph>
Status: <complete | complete_with_evidence_gaps | blocked | stale>

## Coverage
<items complete / failed / blocked / stale / skipped, with rationales for every non-complete
 item; what fraction of atlas coverage this represents>

## Top findings
<Critical + High across the campaign, namespaced IDs, one line each, link to source report>

## Cross-unit synthesis
<the sections of campaign-synthesis.md that change the verdict, summarized; link to the rest>

## Evidence gaps
<the operator checklist>

## Per-item reports
<table: item — status — findings by severity — report path>
```

Write `reviewed-at.json` with final HEAD, timestamp, and the campaign status.

## Completion gate (Step 5)

Walk before declaring any final status; every line must hold or the status downgrades:

1. Every selected item is `complete`, `failed`, `blocked`, `stale`, or `skipped` — none implicitly unprocessed; every non-complete item has a recorded reason.
2. Every declared sweep ran or has an accepted skip rationale.
3. Every non-rejected finding traces to a source report or campaign evidence.
4. Every merged duplicate lists its source IDs; every rejected finding is recorded as rejected, not dropped.
5. Every unresolved evidence gap appears in the report.
6. `campaign-status.json`, `findings-index.md`, `campaign-synthesis.md`, `report.md`, and `reviewed-at.json` agree on status and counts.

`complete` additionally requires: no failed/blocked/stale items and no unresolved required evidence. Failed or blocked items → `blocked`; unverifiable operational facts as the only remainder → `complete_with_evidence_gaps`; mid-campaign drift → `stale`.
