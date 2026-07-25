---
name: sweep
description: >
  Whole-codebase hygiene pass across duplication, dead code, circular deps, weak types,
  defensive and speculative boilerplate, legacy shims, low-value tests and comment slop,
  with blast-radius calibration and
  triage of high-impact findings (conversational by default, subagent-adjudicated in auto
  mode). Trigger only when the user explicitly says "sweep", "run a sweep", or invokes
  $sweep — not on casual cleanup requests, single-file cleanup, or PR review (that is
  $mega-review).
---

# Sweep

Proactive multi-dimensional codebase hygiene. Four parallel dimension agents (each owning two related cruft dimensions) analyze the repo, a Calibrator dedupes and assigns blast radius per finding, LOW-blast findings auto-apply via per-file Appliers, HIGH-blast findings get triaged — conversationally with the user by default, or by a top-tier Adjudicator subagent in auto mode. Polyglot, Python-leaning, with per-language tool detection.

**Artifact location.** This skill writes scratch, not product. Everything goes under `.scratch/` at the repo root (`~/.scratch/<project>/` outside one); a scratch path named in `AGENTS.md` / `CLAUDE.md` wins. Paths below assume the default.

**CRITICAL RULES:**
- **Preflight is scope-aware, not paranoid** — only uncommitted changes to tracked files *inside the sweep scope* block; unrelated artifacts don't. One consolidated confirmation, not five prompts. See Phase 1.
- **Breadth over precision in analysis** — agents are encouraged to flag cross-dimension findings. The Calibrator dedupes.
- **Blast radius, not confidence, gates auto-apply** — obvious-correct + low-impact auto-applies; obvious-correct + high-impact still goes to triage.
- **Rejects become inline markers, not external ledgers** — `cleanup-sweep-skip: <reason>` lives with the code. Markers encode *human* rationale; auto mode never places them.
- **Session artifacts are ephemeral** — live in `.scratch/docs/cleanup/<session>/`, gitignored.

## Parse the Request

1. **Scope**:
   a. User names a path/module → use it
   b. User says "diff" or passes a PR → `git diff <base>`
   c. User says "tests" → restrict to test directories
   d. Default → whole repo minus tests/generated/vendored/migrations/lockfiles
2. **Exclusions** user may override: `include:tests`, `include:migrations`, etc.
3. **Adjudication mode** — see below.
4. **Resume check** — see Resumption below.

## Adjudication Modes

Two modes for HIGH-blast triage (Phase 5):

- **Interactive (default)** — conversational one-by-one walkthrough with the user.
- **Auto** — a top-tier Adjudicator subagent renders verdicts. Activate when: the user says `auto` (e.g. `$sweep auto`), the sweep runs inside a goal loop or non-interactive exec run, or the harness signals non-interactive execution. Announce the mode at Phase 1.

Auto-mode invariants (details in `references/phase-5-triage.md`):
- Adjudicator verdicts are **accept / defer only** — never reject. Rejection places a skip marker, and markers encode human rationale that suppresses findings from all future sweeps.
- Conservative accept rubric; critical-path findings (auth, security, money, data integrity) always defer.
- Phase 6 red CI in auto mode → autonomously revert the suspect finding-commit and re-defer it (see `references/phase-6-verify.md`). Auto mode never ends in a red state waiting on a human.

Record the mode in `scope.md` and `status.md`.

## Resumption

Before starting, check for existing work:

1. Look for `.scratch/docs/cleanup/*/status.md` in the project
2. If found, read the most-recent session's `status.md` and present: *"Found in-progress sweep from YYYY-MM-DD at phase `X`, step `Y`. Resume?"* (In auto mode: resume without asking.)
3. On resume, pick up at the phase indicated; use per-phase resume rules in the referenced phase file

Per-phase resume rules:
- `preflight` / `analyze` / `calibrate` / `verify` / `report` → re-run from scratch (cheap, state stale)
- `auto-apply` → continue from next unapplied file (read `auto-apply.md` ledger)
- `triage` → continue from next un-verdicted finding (read `✓`/`✗`/`⏸` markers in `triage.md`)

If no session is found, proceed to Phase 1.

## Execution Notes

- **Effort**: If the harness exposes an effort control, run dimension agents at high effort and the Calibrator/Adjudicator at the highest available. Cruft detection requires semantic judgment, not checklist matching.
- **Parallel subagents**: Launch all 4 dimension agents simultaneously in a single turn. The orchestrator must fan out deliberately.
- **Parallel tool calls**: Instruct dimension agents to read files and run searches in parallel when independent.
- **Literal scope**: Be explicit about exclusions and boundaries (e.g., "Skip *all* files in `generated/` and `vendored/`, not just the first ones you see").
- **Minimalism in auto-apply**: Applier subagents should make the minimum change that removes the cruft. Do not refactor adjacent code "while you're there."
- **Proactive checkpointing**: Update `status.md` after every significant step (e.g., after each dimension batch completes, after calibration, after each auto-apply batch). Do not wait until the end of a phase. This preserves state if context compacts or the session is interrupted.

## Workflow Phases

Read only the phase you're entering. Do not preload all references.

| Phase | Purpose | Reference |
|-------|---------|-----------|
| **1 — Preflight** | scope-aware git check, PR-aware branch logic, one consolidated confirmation, language detection, silent tool probe, baseline tests, sharding decision | `references/phase-1-preflight.md` |
| **2 — Analyze** | 4 parallel dimension agents (2 dimensions each) produce findings; area-sharded variant for large repos | `references/phase-2-analyze.md` |
| **3 — Calibrate** | Single top-tier agent: cross-agent dedup + blast radius per finding | `references/phase-3-calibrate.md` |
| **4 — Auto-apply** | Per-file Applier subagents for LOW-blast; orchestrator commits per dimension | `references/phase-4-auto-apply.md` |
| **5 — Triage** | HIGH-blast findings: conversational walkthrough (interactive) or Adjudicator subagent (auto) | `references/phase-5-triage.md` |
| **6 — Verify** | Post-apply test run; final CI-equivalent; 3-attempt fix cycle (autonomous revert-and-defer in auto mode) | `references/phase-6-verify.md` |
| **7 — Report** | Inline final summary + marker-age nudge + optional test-sweep nudge | `references/phase-7-report.md` |

Phase transitions: announce explicitly (*"Phase 1 complete, entering Phase 2."*), read the next phase reference, update `.scratch/docs/cleanup/<session>/status.md`.

## Supporting References

- `references/tool-registry.md` — per-language tool table, install commands, config bootstrap, degradation policy
- `references/markers.md` — `cleanup-sweep-skip` syntax per language, placement rules, age-nudge format

## Model & Reasoning Tiers

Two levers per subagent: **model tier** and **reasoning_effort**. On GPT-5.6-era lineups the tiers are, e.g., Sol (flagship) / Terra (mid, roughly previous-flagship-competitive at lower cost) / Luna (smallest, nano-equivalent); map by relative capability when names change. Mid tier at `high` is the workhorse for scoped research; the flagship tier at `xhigh` is reserved for the steps that gate everything downstream.

| Role | Tier / effort | Rationale |
|------|---------------|-----------|
| 4 dimension agents (Phase 2) | mid tier (Terra-class), `high` | Scoped research with judgment calls — "is this cruft or intentional?" Modern mid-tier models handle a two-dimension brief in one context. |
| Calibrator (Phase 3) | flagship (Sol-class), `xhigh` | Blast-radius judgment gates auto-apply; the single highest-leverage reasoning step. |
| Adjudicator (Phase 5, auto mode only) | flagship (Sol-class), `xhigh` | Renders accept/defer verdicts unsupervised; needs fresh, maximally capable context. |
| Applier (Phase 4) | mid/small tier (Terra/Luna-class), `low` | Mechanical per-file application of pre-analyzed findings, with explicit veto rule (kick back to triage if subtler than judged). |
| Final report (Phase 7) | none — orchestrator writes it inline | Small aggregation of session files; spawn overhead exceeds the work. |

Explorers tracing cross-file behavior: mid tier at `medium`.

Main-thread orchestration (triage walkthrough with user) inherits the session model.

`max` is never part of the default pipeline. Use it only on explicit user request, or as a single retry of a step that demonstrably failed at `xhigh`.

## Artifact Layout

```
.scratch/docs/cleanup/YYYY-MM-DD-<slug>/
  status.md            # phase / step / next-action — drives resume
  scope.md             # target + exclusions + detected languages + tool availability + mode + sharding
  findings/
    duplication-types.md      # DU-* + TC-*  (Agent A)
    dead-legacy.md            # DC-* + LF-*  (Agent B)
    types-structure.md        # WT-* + CD-*  (Agent C)
    guards-comments.md        # DF-* + CS-*  (Agent D)
    area-<slug>.md            # (area-sharded mode only — all prefixes, one file per area)
  calibration.md       # dedup + blast radius per finding
  auto-apply.md        # per-file apply ledger
  triage.md            # HIGH-blast walkthrough (or adjudication log) with verdicts
  report.md            # final summary
```

Preflight ensures `.scratch` is in `.gitignore` before creating this structure.

## Cross-Skill Boundaries

| If the user wants... | Use... |
|----------------------|--------|
| Whole-codebase maintenance sweep | **sweep** (this skill) |
| Review a PR / diff | `$mega-review` |
| Triage review findings | `$review-triage` |
| Implement a specific feature or proposal | `$deep-implement` |
| Design, refactor, or refine code with architectural intent | `forge` |

## Cancellation

If the user stops mid-sweep ("stop", "abandon", "let's not do this"):
1. Ensure no uncommitted half-applied state — commit whatever is clean, warn about anything dirty
2. Tell the user the branch name and `.scratch/docs/cleanup/<session>/` path
3. Ask: *"Clean up (delete branch + `.scratch` session dir), or leave for later resume?"*
4. Act on their choice

## Cross-Phase Principles

### Breadth Over Precision

In Phase 2, dimension agents are told: *"If you notice findings in adjacent dimensions, flag them anyway."* The cost of a duplicate finding is one Calibrator dedup; the cost of a missed finding is permanent cruft.

### Blast Radius, Not Confidence

A finding can be obviously correct (high confidence) *and* high blast radius — e.g., removing a try/catch that wraps a critical retry point. These go to triage, not auto-apply. The Calibrator's job is to judge blast radius with a fresh top-tier context, not to trust the dimension agent's self-assessment.

### Inline Markers, Not External Ledgers

When the user rejects a HIGH-blast finding, the rationale lives on the code line as `cleanup-sweep-skip: <reason>`. No `rejected.md` file to go stale. Future runs see the marker and skip that region. Markers are human-only: auto mode defers instead of rejecting, so no marker is ever placed without a human behind it.

### Test-Aware

Default scope excludes tests; Phase 7 nudges user to run the sweep against tests separately with relaxed rules.

### Chesterton's Fence on Removal Dimensions

Comment-slop, defensive-code and test-slop dimensions are removal-biased. Before flagging:
- **Comments**: distinguish WHAT-comments (slop) from WHY-comments (load-bearing). A comment explaining a non-obvious constraint, workaround, or invariant stays. Only flag comments that restate the code.
- **Defensive code**: a try/except, null check, or fallback may exist because something *did* fail in production. Don't flag unless you can articulate why the failure mode it guards against is impossible.
- **Speculative code**: an interface with one implementer, an unvaried parameter, or a fixed-value flag may be mid-rollout or an external API surface. Check for a recent commit or ticket reference before flagging.
- **Tests**: a weak test usually marks behavior somebody wanted covered. Prefer strengthening it to one real assertion over deleting it; delete only when there is no real behavior left to assert.

When in doubt → mark HIGH-blast and route to triage, not auto-apply.

### Tool-Aware, Tool-Optional

Preflight detects languages and silently probes for tools. Missing tools → agent falls back to LLM-only analysis with a noted caveat. Never aborts on missing tools; never blocks preflight on install prompts.
