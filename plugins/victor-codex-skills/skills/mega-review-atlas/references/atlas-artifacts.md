# Atlas Artifacts

Contents: atlas.md · unit packets · coverage.md · runtime-profile.md · decisions.md · cohesion-overlay.md · Freeze checklist

Formats for everything the atlas writes. `atlas.md` is authoritative; unit packets and `coverage.md` are projections that must never contradict it. Regenerate projections whenever the manifest changes.

## atlas.md — canonical manifest

```markdown
# Review Atlas: <target name>

- **Atlas ID:** <directory name>
- **Status:** draft | frozen
- **Source mode:** snapshot | diff | hybrid
- **Repository root:** <path>   **HEAD:** <sha>   **Base:** <sha, diff mode only>
- **Entry points:** <list>
- **Behavioral closure:** <one paragraph: what is in, and the rule that decided it>
- **Opaque platforms:** <name — contract relied on, one line each>
- **External dependencies:** <list>
- **Dimensions:** <mega-review dimensions in play>

## Hierarchy
<indented tree of all nodes along the lifecycle spine; each line: `<kind> <id> — <label>`;
 reviewable nodes marked ▶>

## Nodes
### <id>  (<kind>)
- **Label:** ...
- **Parent:** <group id>
- **Guarantee:** given X, guarantees Y            (units/seams)
- **Primary scope:** path — symbols | whole-file  (one line per entry)
- **Context scope:** ...
- **Size:** ~<files> files / ~<lines> lines [+ oversize rationale if flagged]
- **Dimensions:** <subset if trimmed, else "all">
- **Edges:** <kind> → <node id> — <contract, one line>   (calls / artifact / database /
  configuration / deployment / opaque-contract / shares-invariant / executes-after)

## Exclusions
| Path / symbol | Reason |
```

Node IDs are stable kebab-case semantic names (`commit-ingest`, `dedup-store-seam`), never ordinals. Edge kinds are from the list above. Keep per-node detail here to what navigation needs — full detail lives in the unit packet.

## units/<unit-id>.md — review packet

Each reviewable node (unit, seam, sweep) gets one packet. It must be **sufficient input for `mega-review` in unit-packet mode without reconstruction** — the campaign passes it verbatim.

```markdown
# Unit Packet: <unit-id>

- **Atlas:** <atlas-id>   **Kind:** unit | seam | sweep   **Revision:** <HEAD sha>
- **Guarantee:** given X, this unit guarantees Y
- **Intent:** <2-5 sentences: purpose, why it exists, what depends on it>

## Primary scope
| Path | Symbols (or whole-file) |

## Context-only scope
| Path | Why a reviewer needs it |

## Behavior
- **Inputs / outputs / side effects:** ...
- **Invariants:** ...
- **Failure / retry / concurrency:** ...

## Tests & evidence
- Focused tests: <paths>
- Evidence commands: <runnable commands, if any>

## Runtime
- Scenarios that apply: <names from runtime-profile.md>
- Assumption-sensitive spots: <list or "none">

## Review guidance
- **Dimensions:** <list>   **Hot spots:** <list>
- **Exclusions:** <what a reviewer must not report on, and why>
- **Adjacent seams:** <ids>
- **Cohesion signals:** <from the overlay, or "none">
```

Seam packets add: both endpoint units, which side is primary vs context, and the contract under review. Sweep packets replace Guarantee with the sweep's single question and list the exact units/symbols swept.

## coverage.md — ownership ledger

```markdown
| Path | Symbol / whole-file | Disposition | Owner node | Reason |
```

Disposition: `owned` / `excluded` / `opaque` / `external`. One row per symbol for split files; one whole-file row otherwise. This table is the proof of coverage — "likely modules" prose is not acceptable.

## runtime-profile.md

Named workload scenarios (typically normal / heavy / growth, plus adversarial skew when input distribution matters): the scale drivers that define each — input volume, data cardinality, concurrency, resource limits, latency/SLA expectations — with a value or "unknown" per scenario. Separate source-system input volume from current stored cardinality.

Every factual claim in this file (and every runtime claim elsewhere in the atlas) carries one evidence status:

`repository_verified` · `locally_measured` · `snapshot_measured` · `operator_confirmed` · `assumed` · `unknown` · `externally_unverifiable`

Close with an **Evidence gaps** section: every `assumed` / `unknown` / `externally_unverifiable` claim that a review will depend on. The campaign carries this ledger into its final report.

## decisions.md

One entry per boundary decision: the question, options considered, the decision (or "unknown"), and rationale. Append-only during iteration — later reversals reference the original entry.

## cohesion-overlay.md

One entry per smell: description, affected node IDs, evidence (paths/symbols), and *no* recommended fix.

## Freeze checklist

Walk this against the actual files before Step 8 offers the atlas for acceptance. Any ✗ returns to the offending step:

1. Hierarchy is acyclic; every node's parent exists. (Dependency edges may form cycles — those stay visible, they don't block.)
2. Coverage holds at the level the format can prove: every path in the `inventory/` files appears in `coverage.md`; for files split across units, the symbol rows are checked exhaustively for gaps and double ownership; unsplit files are checked at directory level plus targeted sampling. State what was sampled.
3. Every reviewable node has: guarantee (or sweep question), primary scope, dimensions, and a packet file.
4. Every oversize unit has a rationale.
5. Every opaque dependency has a seam.
6. Every material cross-unit risk from Step 4's candidate classes is owned by a seam or sweep, or its absence is justified in `decisions.md`.
7. Every runtime claim has an evidence status; every gap a review depends on is in the Evidence gaps section.
8. Packets and `coverage.md` agree with `atlas.md` — spot-check at minimum every seam and every oversize unit.
9. No orphan nodes, edges, or packet files.
