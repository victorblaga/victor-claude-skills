---
name: sweep
description: >
  Use when the user asks for "sweep", "cleanup sweep", "run a sweep", "sweep the codebase",
  "do a cleanup pass", "purge cruft", "clean up the whole codebase", or invokes $sweep —
  a whole-codebase hygiene workflow across duplication, dead code, circular deps, weak types,
  defensive boilerplate, legacy shims, and comment slop, with blast-radius calibration and
  one-by-one triage for high-impact findings.
  Do NOT trigger for single-file cleanup (use $simplify), PR-specific review (use $mega-review),
  feature implementation (use $deep-implement), or casual "clean this up" requests without
  whole-codebase scope. Trigger ONLY when the user explicitly opts into the heavyweight sweep.
---

# Sweep

Proactive multi-dimensional codebase hygiene. Eight parallel `gpt-5.4` review subagents analyze the repo, a Calibrator dedupes and assigns blast radius per finding, LOW-blast findings auto-apply via per-file Appliers, and HIGH-blast findings get walked through conversationally with the user. Polyglot, Python-leaning, with per-language tool detection.

**CRITICAL RULES:**
- **Preflight is strict** — no dirty git, no auto-run on dev/main, baseline test check. See Phase 1.
- **Breadth over precision in analysis** — agents are encouraged to flag cross-dimension findings. The Calibrator dedupes.
- **Blast radius, not confidence, gates auto-apply** — obvious-correct + low-impact auto-applies; obvious-correct + high-impact still goes to triage.
- **Rejects become inline markers, not external ledgers** — `cleanup-sweep-skip: <reason>` lives with the code.
- **Session artifacts are ephemeral** — live in `.docs/cleanup/<session>/`, gitignored.

## Parse the Request

1. **Scope**:
   a. User names a path/module → use it
   b. User says "diff" or passes a PR → `git diff <base>`
   c. User says "tests" → restrict to test directories
   d. Default → whole repo minus tests/generated/vendored/migrations/lockfiles
2. **Exclusions** user may override: `include:tests`, `include:migrations`, etc.
3. **Resume check** — see Resumption below.

## Resumption

Before starting, check for existing work:

1. Look for `.docs/cleanup/*/status.md` in the project
2. If found, read the most-recent session's `status.md` and present: *"Found in-progress sweep from YYYY-MM-DD at phase `X`, step `Y`. Resume?"*
3. On resume, pick up at the phase indicated; use per-phase resume rules in the referenced phase file

Per-phase resume rules:
- `preflight` / `analyze` / `calibrate` / `verify` / `report` → re-run from scratch (cheap, state stale)
- `auto-apply` → continue from next unapplied file (read `auto-apply.md` ledger)
- `triage` → continue from next un-verdicted finding (read `✓`/`✗`/`⏸` markers in `triage.md`)

If no session is found, proceed to Phase 1.

## Execution Notes

- **Parallel subagents**: Launch all 8 dimension agents simultaneously in a single turn. Spawn fewer subagents by default; the orchestrator must fan out deliberately.
- **Parallel tool calls**: Instruct dimension agents to read files and run searches in parallel when independent.
- **Literal scope**: Be explicit about exclusions and boundaries (e.g., "Skip *all* files in `generated/` and `vendored/`, not just the first ones you see").
- **Minimalism in auto-apply**: Applier subagents should make the minimum change that removes the cruft. Do not refactor adjacent code "while you're there."
- **Proactive checkpointing**: Update `status.md` after every significant step (e.g., after each dimension batch completes, after calibration, after each auto-apply batch). Do not wait until the end of a phase. This preserves state if context compacts or the session is interrupted.

## Workflow Phases

Read only the phase you're entering. Do not preload all references.

| Phase | Purpose | Reference |
|-------|---------|-----------|
| **1 — Preflight** | git clean, branch choice, `.gitignore` for `.docs`, language detection, tool probe + install offers, baseline tests | `references/phase-1-preflight.md` |
| **2 — Analyze** | 8 parallel `gpt-5.4` dimension subagents produce findings | `references/phase-2-analyze.md` |
| **3 — Calibrate** | Single `gpt-5.4` calibrator: cross-agent dedup + blast radius per finding | `references/phase-3-calibrate.md` |
| **4 — Auto-apply** | Per-file `gpt-5.4` Applier subagents for LOW-blast; dimension-grouped commit reword | `references/phase-4-auto-apply.md` |
| **5 — Triage** | Conversational walkthrough of HIGH-blast findings with accept / reject / defer / modify verdicts | `references/phase-5-triage.md` |
| **6 — Verify** | Post-apply test run; final CI-equivalent; 3-attempt fix cycle | `references/phase-6-verify.md` |
| **7 — Report** | Final summary + marker-age nudge + optional test-sweep nudge | `references/phase-7-report.md` |

Phase transitions: announce explicitly (*"Phase 1 complete, entering Phase 2."*), read the next phase reference, update `.docs/cleanup/<session>/status.md`.

## Supporting References

- `references/tool-registry.md` — per-language tool table, install commands, config bootstrap, degradation policy
- `references/markers.md` — `cleanup-sweep-skip` syntax per language, placement rules, age-nudge format

## Model Tiers

| Role | Model | Reasoning effort | Rationale |
|------|-------|------------------|-----------|
| 8 dimension agents (Phase 2) | `gpt-5.4` | `high` | Each agent makes "is this cruft or intentional?" judgment calls across one dimension without needing the slowest setting. |
| Calibrator (Phase 3) | `gpt-5.4` | `xhigh` | Blast-radius judgment and cross-agent dedup are the highest-leverage reasoning step. |
| Applier (Phase 4) | `gpt-5.4` | `medium` | Per-file application is narrower and more mechanical, but still benefits from the full model. |
| Final report (Phase 7) | `gpt-5.4` | `medium` | Formatting and statistics aggregation are structured tasks. |

Main-thread orchestration (triage walkthrough with user) inherits the session model.

## Artifact Layout

```
.docs/cleanup/YYYY-MM-DD-<slug>/
  status.md            # phase / step / next-action — drives resume
  scope.md             # target + exclusions + detected languages + tool availability
  findings/
    duplication.md            # DU-*
    type-consolidation.md     # TC-*
    dead-code.md              # DC-*
    circular-deps.md          # CD-*
    weak-types.md             # WT-*
    defensive-code.md         # DF-*
    legacy-fallback.md        # LF-*
    comments-slop.md          # CS-*
  calibration.md       # dedup + blast radius per finding
  auto-apply.md        # per-file apply ledger
  triage.md            # HIGH-blast walkthrough with verdicts
  report.md            # final summary
```

Preflight ensures `.docs` is in `.gitignore` before creating this structure.

## Cross-Skill Boundaries

| If the user wants... | Use... |
|----------------------|--------|
| Whole-codebase maintenance sweep | **sweep** (this skill) |
| Single-file or single-function cleanup | `$simplify` |
| Review a PR / diff | `$mega-review` |
| Triage review findings | `$review-triage` |
| Implement a specific feature or proposal | `$deep-implement` |
| Design, refactor, or refine code with architectural intent | `forge` |

## Cancellation

If the user stops mid-sweep ("stop", "abandon", "let's not do this"):
1. Ensure no uncommitted half-applied state — commit whatever is clean, warn about anything dirty
2. Tell the user the branch name and `.docs/cleanup/<session>/` path
3. Ask: *"Clean up (delete branch + `.docs` session dir), or leave for later resume?"*
4. Act on their choice

## Cross-Phase Principles

### Breadth Over Precision

In Phase 2, dimension agents are told: *"If you notice findings in adjacent dimensions, flag them anyway."* The cost of a duplicate finding is one Calibrator dedup; the cost of a missed finding is permanent cruft.

### Blast Radius, Not Confidence

A finding can be obviously correct (high confidence) *and* high blast radius — e.g., removing a try/catch that wraps a critical retry point. These go to triage, not auto-apply. The Calibrator's job is to judge blast radius with a fresh high-reasoning context, not to trust the dimension agent's self-assessment.

### Inline Markers, Not External Ledgers

When the user rejects a HIGH-blast finding, the rationale lives on the code line as `cleanup-sweep-skip: <reason>`. No `rejected.md` file to go stale. Future runs see the marker and skip that region.

### Test-Aware

Default scope excludes tests; Phase 7 nudges user to run the sweep against tests separately with relaxed rules.

### Chesterton's Fence on Removal Dimensions

Comments-slop and defensive-code dimensions are removal-biased. Before flagging:
- **Comments**: distinguish WHAT-comments (slop) from WHY-comments (load-bearing). A comment explaining a non-obvious constraint, workaround, or invariant stays. Only flag comments that restate the code.
- **Defensive code**: a try/except, null check, or fallback may exist because something *did* fail in production. Don't flag unless you can articulate why the failure mode it guards against is impossible.

When in doubt → mark HIGH-blast and route to triage, not auto-apply.

### Tool-Aware, Tool-Optional

Preflight detects languages and probes for tools. Missing tools → agent falls back to LLM-only analysis with a noted caveat. Never aborts on missing tools.
