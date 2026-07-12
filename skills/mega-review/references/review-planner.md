# Step 0 — Review Planner

The planner runs **before** the batched interview and dimension fan-out. It produces `{OUTPUT_DIR}/review-plan.md` — the orchestrator's only bulk-intelligence input besides small digests.

## When to run

**Skip trigger:** if the review scope is below ~10 changed files **and** ~500 changed lines (count from the resolved file list + diff stat), skip the planner subagent and use the **Default matrix** below directly. Write a minimal `{OUTPUT_DIR}/review-plan.md` noting "planner skipped — small diff; default matrix applied."

**Otherwise:** launch the planner subagent.

## Planner subagent

Launch via the Agent tool with **flagship capability class** and **xhigh** intelligence level (extended thinking / high reasoning effort). Do **not** use `max` — reserved for explicit user escalation. Do **not** run planning in the orchestrator — a large diff read there is re-billed every subsequent turn and risks window exhaustion.

```
You are the Review Planner for a multi-dimensional code review. Your job is to read the change, digest intent, and write a concise review plan that downstream agents will follow. You do NOT write findings.

**Target scope:** {TARGET}
**Changed files:** {FILE_LIST}
**File count / line count:** {FILE_COUNT} files, ~{LINE_COUNT} changed lines
**Hunks delivery:** {HUNKS_MODE} — either "inline" (path to inline hunk blob) or "index" (path to {OUTPUT_DIR}/hunks/index.md)
**Output file:** {OUTPUT_DIR}/review-plan.md
**Project conventions summary:** {PROJECT_CONVENTIONS_BRIEF}

**You are READ-ONLY. Do not modify any project code.**

**Your tasks:**
1. **Digest intent.** Read PR metadata, commit messages, linked ticket/goal text, and plan docs (`docs/plans/*.md` if present). Write a ≤500-token `{INTENT}` digest: goal, acceptance criteria, non-goals, and explicit requirements (R1, R2, … if a plan exists). If intent is missing, note what's absent — the orchestrator will ask the user in the interview.
2. **Read risky diff regions thoroughly** — not just stats. Identify auth, migrations, concurrency, new endpoints, raw SQL, large loops, API surface changes, and test gaps. This steering multiplies recall-per-token across all downstream agents.
3. **Decide dimension activation** — bias is run everything. You may skip a dimension only with stated rationale (e.g. docs-only diff → skip Performance). Activate conditional specialists when warranted (see Dimension catalog below).
4. **Assign capability class + intelligence level** per role (see Capability classes and Default matrix). Override defaults only with rationale tied to this diff's risk.
5. **Write hot spots** — per-dimension steering notes (1-3 sentences each) telling agents where to focus.
6. **Decide sharding** — if ~50+ files, split affected dimensions into 2-3 agents over file subsets (same checklist, different `{FILE_LIST}` slices).
7. **Decide evidence pass** — default is **attempt** (run existing test/lint/type-check commands; never install deps; timeboxed). Skip only with rationale (no test infra, unbuildable env). Pre-specify exact commands when known from project conventions.

**Write `{OUTPUT_DIR}/review-plan.md` using this structure:**

```markdown
# Review Plan — {date}

## Intent digest
{INTENT — or "MISSING — orchestrator to collect in interview"}

## Scope stats
- Files: {N}
- Changed lines: ~{M}
- Languages / domains: {list}
- Hunks mode: inline | index

## Dimension activation
| Dimension | Active | Rationale / file subset |
|-----------|--------|-------------------------|
| CQ | yes/no | … |
| AR | yes/no | … |
| CR | yes/no | … |
| TQ | yes/no | … |
| SE | yes/no | … |
| PC | yes/no | … |
| RO | yes/no | … |
| PF | yes/no | … |
| IC | yes/no | … |
| DM | yes/no | … |
| BC | yes/no | … |

## Sharding
(If applicable: which dimensions split into multiple agents and their file subsets. Omit if not sharding.)

## Hot spots
- **CQ:** …
- **AR:** …
(only for active dimensions)

## Model assignments
| Role | Capability | Intelligence | Rationale |
|------|------------|--------------|-----------|
| Dimension agents | … | … | … |
| Explorers | … | … | … |
| Verifiers | … | … | … |
| Critical/High double-verify | … | … | … |
| Calibrator | … | … | … |
| Synthesis | … | … | … |
| Consolidator | … | … | … |
| Evidence pass | … | … | … |

## Evidence pass
- **Run:** yes | no
- **Commands:** (if yes — exact commands, timebox)
- **Skip rationale:** (if no)

## Risk summary
(2-4 sentences: top risks this review should catch)
```

**Final response:** ≤3 lines — confirmation, file path, one-line risk summary. The plan file is the deliverable.
```

Also write `{OUTPUT_DIR}/intent.md` containing only the intent digest (for reuse as `{INTENT}` in dimension prompts).

## Capability classes

Use **capability classes**, not hardcoded model names. Map to the harness's available models by relative capability:

| Class | Claude Code examples | Codex / GPT examples | Typical use |
|-------|---------------------|----------------------|-------------|
| **flagship** | Fable, Opus-class | Sol | Judgment, recall-critical review, calibration, synthesis |
| **mid** | Sonnet-class | Terra | Verification, exploration, mechanical assembly |
| **small** | Haiku-class | Luna | Pre-specified command runs only |

When model names change, map by capability — do not update the skill for every lineup change.

**Intelligence level** is a separate lever: reasoning effort / extended-thinking budget where the harness exposes it (`high`, `xhigh`, `low`, etc.). `max` is never part of the default pipeline.

## Default matrix

Fallback when the planner is skipped or when the plan file omits a role:

| Role | Capability | Intelligence | Notes |
|------|------------|--------------|-------|
| Planner | flagship | xhigh | Subagent only; skip on small diffs |
| Dimension agents (all core + conditionals) | flagship | high | Downgrade CQ/TQ to mid only on low-risk diffs with stated rationale |
| Explorers (nested) | mid | medium | Cap ~4 per dimension agent; escalate to flagship/high for subtle control-flow tracing |
| Verifiers | mid | medium | "Could not determine" escape hatch — Calibrator adjudicates |
| Critical/High double-verify | flagship | high | Second independent pass for candidates heading to Critical/High |
| Calibrator | flagship | xhigh | Singleton whose judgment touches every finding |
| Synthesis | flagship | xhigh | Tensions + recurring patterns |
| Consolidator | mid | low | Verbatim assembler — copy finding text, do not paraphrase |
| Evidence pass | mid | low | Small acceptable when commands are pre-specified |

## Dimension catalog

Core dimensions (always-on unless planner skips with rationale):

| # | Dimension | Prefix | Output file |
|---|-----------|--------|-------------|
| 1 | Code Quality | CQ | `code-quality.md` |
| 2 | Architecture | AR | `architecture.md` |
| 3 | Correctness | CR | `correctness.md` |
| 4 | Test Quality | TQ | `test-quality.md` |
| 5 | Security & Error Handling | SE | `security-error-handling.md` |
| 6 | Pattern Conformity | PC | `pattern-conformity.md` |
| 7 | Refactoring Opportunities | RO | `refactoring-opportunities.md` |
| 8 | Performance | PF | `performance.md` |
| 9 | Intent Conformance | IC | `intent-conformance.md` |

Conditional specialists (planner-activated):

| Dimension | Prefix | Output file | Activate when |
|-----------|--------|-------------|---------------|
| Data Migration safety | DM | `data-migration.md` | Diff includes migration/schema artifacts (`db/migrate/*`, `db/schema.rb`, Alembic/Flyway paths, backfill scripts) |
| API/Contract compatibility | BC | `api-contract.md` | Diff touches routes, serializers, public types, API versioning, or exported contracts |

## Evidence pass subagent

When the plan says **Run: yes**, launch an evidence subagent **in the same message as the dimension agents** (parallel, not blocking):

```
You are the Evidence Pass agent. Run the project's existing verification commands and record results. You do NOT modify project code. Never install dependencies.

**Commands (from review plan):** {EVIDENCE_COMMANDS}
**Timebox:** {TIMEBOX — e.g. 10 minutes total}
**Output directory:** {OUTPUT_DIR}/evidence/

**Rules:**
- Run only commands listed in the plan (or discovered from project conventions: Makefile, package.json scripts, pyproject.toml, etc.)
- Capture failures verbatim (full relevant output) to `{OUTPUT_DIR}/evidence/{command-slug}.md`
- Capture passes as counts/summaries only ("42 passed, 0 failed")
- For hard failures (test failures, lint errors, type errors), emit one finding per distinct failure class:

### EV-{N}: {short title}
- **Location:** `file:line` (from tool output, or "n/a" for global failures)
- **Issue:** (what failed)
- **Evidence:** (quoted output excerpt)
- **Severity:** Critical / High / Medium
- **Confidence:** High

Write all EV findings to `{OUTPUT_DIR}/evidence/findings.md`.

**Final response:** ≤3 lines — commands run, pass/fail counts, path to evidence dir.
```

Evidence findings enter verification and calibration — not dimension agents.

## After the planner completes

The orchestrator reads only `{OUTPUT_DIR}/review-plan.md` and `{OUTPUT_DIR}/intent.md`. Proceed to Step 1 (batched interview) in SKILL.md.
