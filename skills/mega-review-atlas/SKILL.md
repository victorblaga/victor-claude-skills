---
name: mega-review-atlas
description: >
  Decompose a system too large for one mega-review into a frozen review atlas: behavioral
  units, seams, sweeps, and a coverage ledger, built interactively and fingerprinted to a
  source state. Produces scope artifacts only — reviews nothing, changes no code. Trigger
  only when the user explicitly says "mega-review-atlas" or invokes /mega-review-atlas —
  not on generic "map the codebase" requests.
disable-model-invocation: true
---

# Mega Review Atlas

Build and freeze a **review atlas** — an agreed, exhaustive decomposition of a system into review units small enough for one `mega-review` each, plus the seams between them and the horizontal sweeps across them. The atlas is the input to `mega-review-campaign`, which executes the reviews. This skill only maps.

It exists because adding agents does not fix an oversized scope — the unit of reasoning must narrow **before** any review fan-out begins.

**SCOPE-ONLY.** Never report code-review findings. Never modify project code. The only output is the atlas directory.

## Parse the Request

1. **Target** — the system, subsystem, pipeline, package, directory, or broad PR to decompose. If ambiguous, ask.
2. **Source mode** — `snapshot` (the system as it stands), `diff` (a broad change set), or `hybrid`.
3. **Output directory** — see below; the user may override.
4. **Refresh** — if the user points at an existing atlas that went stale, load it, re-verify only the drifted parts, and produce a new frozen version. Do not rebuild from scratch.

## Output Directory

Scratch, not product: `.scratch/` at the repo root (`~/.scratch/<project>/` outside one); a scratch path named in `AGENTS.md` / `CLAUDE.md` wins. Same gitignore preflight as `mega-review`: if `.scratch/` is not ignored, offer to append it as a standalone `chore:` commit.

```
.scratch/docs/reviews/atlases/YYYY-MM-DD-<target>-XXXXX/
```

`XXXXX` — 5 random alphanumeric characters to avoid collisions.

Contents when finished:

```
atlas.md               # canonical manifest: hierarchy, nodes, edges — authoritative
units/<unit-id>.md     # one self-contained review packet per reviewable node
coverage.md            # symbol/file ownership ledger — every symbol owned, excluded, opaque, or external
decisions.md           # boundary decisions, rationale, unresolved questions
runtime-profile.md     # named workload scenarios + evidence status per claim
cohesion-overlay.md    # structural smells (observations, not findings)
inventory/             # explorer output files from Step 2
frozen-at.json         # source fingerprint + status
```

`atlas.md` is authoritative; every other file is a projection or supplement. Formats: `references/atlas-artifacts.md`.

## Execution

Read only the reference for the step you're entering.

| Step | Purpose | Reference |
|------|---------|-----------|
| **0 — Orient** | Target, mode, output dir | (below) |
| **1 — Boundary contract** | Closure, opaque platforms, envelope — interview | (below) |
| **2 — Inventory** | Execution/data-flow graph via parallel explorers | (below) |
| **3 — Compile units** | Apply the stopping rule, assign ownership | `references/decomposition.md` |
| **4 — Seams & sweeps** | Cross-unit risks get explicit owners | `references/decomposition.md` |
| **5 — Runtime & evidence** | Workload scenarios, evidence status | `references/atlas-artifacts.md` |
| **6 — Cohesion overlay** | Structural smells, no prescriptions | `references/decomposition.md` |
| **7 — Validate & render** | Coverage self-check, write artifacts | `references/atlas-artifacts.md` |
| **8 — Feedback & freeze** | Iterate with user, fingerprint | (below) |

### Step 0: Orient

Read repository instructions (`CLAUDE.md` / `AGENTS.md` and what they reference). Resolve target, entry points, repo root, source mode. Create the output directory; record the current HEAD SHA. Tell the user: this builds scope, not review findings.

### Step 1: Boundary Contract

Explore the code **before** asking anything the repository can answer. Interview only for judgment calls and facts the code cannot show (production topology, operational constraints). One question at a time, each with a recommended answer. Resolve:

- **Behavioral closure** — which locally owned code (across packages/repos) is needed to determine the target's behavior. Follow behavior, not directory boundaries.
- **Opaque platforms** — dependencies assumed to work internally; the atlas reviews how the target *uses* their contract, never their implementation.
- **Production envelope** — whether deployment wiring, configuration, scheduling, resource sizing, and database contracts are in scope.
- **Review dimensions** — default to the full `mega-review` catalog; the user may trim.
- **Cohesion overlay** — capture structural smells? Default yes, as a separate overlay.

Record every decision — including "unknown" — with rationale in `decisions.md`.

### Step 2: Inventory

Build the actual execution and data-flow graph: entry points, orchestration, workers, adapters, artifact/schema handoffs, database mutations, tests, deployment wiring. Follow calls into locally owned dependencies until an opaque or external boundary.

Use parallel explorer subagents (mid-tier or better) for independent lifecycle branches. Each explorer writes a bounded file to `inventory/` listing **source paths and qualified symbols**, not just prose; replies are ≤3-line receipts. The orchestrator samples source to steer but never loads bulk implementation into its own context.

Done when every reachable branch terminates in owned implementation, an opaque seam, an external dependency, or an explicit exclusion.

### Steps 3–6

Read the reference for each step, then compile the node set:

- **Units** (Step 3) — apply the stopping rule and ownership rules from `references/decomposition.md`.
- **Seams & sweeps** (Step 4) — give every material cross-unit risk a named seam or sweep owner; candidate classes are in `references/decomposition.md`.
- **Runtime profile** (Step 5) — workload scenarios and evidence statuses per `references/atlas-artifacts.md`.
- **Cohesion overlay** (Step 6) — structural smells as observations, never prescriptions (`references/decomposition.md`).

### Step 7: Validate & Render

Read `references/atlas-artifacts.md`. Run the freeze checklist yourself, line by line, against the actual artifacts — it is a gate, not a formality. Any failure returns to the offending step. Then write `atlas.md`, `units/*.md`, and `coverage.md` in the specified formats.

### Step 8: Feedback & Freeze

1. Present the atlas: node counts, the lifecycle spine, and the **highest-uncertainty boundaries** first.
2. Iterate — one feedback question at a time; regenerate affected artifacts after each accepted change.
3. Freeze **only on explicit user acceptance**, and only from a **clean working tree** — uncommitted changes make the fingerprint unverifiable, so ask the user to commit or stash first. Write `frozen-at.json`:

```json
{"status": "frozen", "atlas_id": "<dir name>", "head_sha": "<HEAD>", "base": "<merge-base, diff mode only>",
 "timestamp": "<ISO date>"}
```

An atlas without `"status": "frozen"` is a draft; `mega-review-campaign` must refuse it.

4. Report: node counts by kind, coverage summary (owned / excluded / opaque / external), open evidence gaps, and the path. Remind the user the next step is `/mega-review-campaign` — or stopping here, which is a valid outcome.

## Cross-Skill Boundaries

| If the user wants... | Use... |
|----------------------|--------|
| Map a large system into review units | **mega-review-atlas** (this skill) |
| Execute the reviews from a frozen atlas | `mega-review-campaign` |
| Review one diff / PR directly | `mega-review` |
| Understand a codebase conversationally | `cross-examine` |
| Whole-codebase hygiene pass | `sweep` |
