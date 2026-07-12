# Step 2 — Dimension Agents

Launch all applicable dimension subagents via the Agent tool **in a single message** so they run concurrently. Capability class and intelligence level come from `{OUTPUT_DIR}/review-plan.md` (default: flagship / high for dimension agents). If the harness does not support subagents, run dimensions sequentially while preserving the same output structure.

Also launch the **evidence pass subagent** in the same message when the review plan says `Evidence pass: yes` (see `references/review-planner.md`).

When sharding applies, launch multiple agents for the same dimension with different `{FILE_LIST}` slices — same checklist, same prefix, different hot-spot file subset.

## Prompt layout (cache-first)

Every dimension prompt has two parts:

1. **Shared prefix** (identical across all dimension agents in this review) — substitute once, reuse verbatim:
2. **Agent suffix** (unique per dimension) — `{DIMENSION}`, `{PREFIX}`, `{OUTPUT_FILE}`, `{EXTRA_FIELDS}`, `{HOT_SPOTS}`, checklist

This ordering maximizes prompt-cache hits across parallel launches.

---

## Shared prefix (all dimension agents)

```
**You are READ-ONLY. Do not modify any project code.**

**Coverage rule:** Report every issue you find, including ones you are uncertain about or consider low-severity. Do not self-filter for importance or confidence — the calibration step handles severity ranking. It is better to surface a finding that later gets downgraded than to silently drop a real bug. For each finding, include your confidence level and estimated severity.

**Assumption rule:** Whenever a finding depends on runtime conditions — concurrency level, data size, call frequency, input trust, delivery semantics — state those conditions explicitly in the `Assumes` field and check them against the runtime context below. Do not invent scale or parallelism. If the runtime context contradicts an assumption, report it with the assumption stated and let calibration set severity. If silent, say "unconfirmed".

**Scope rule:** Findings must be about the changed files in your assigned scope, but explore surrounding code freely for context. Check every file in the target scope, not just the obvious ones. Use hunks to mark **Pre-existing: yes** when the issue is in unchanged context lines, **Pre-existing: no** when introduced by this change.

**How to work:** Read files and run Grep/Glob searches in parallel when independent. For cross-file tracing:
- Read directly when ≤2 files are involved.
- Otherwise spawn Explore subagents at **mid capability class** (never small) — cap **4** explorers total; you need their conclusions, not their tool output. Escalate to flagship/high only for subtle control-flow tracing.
For large diffs, extract relevant code quotes with file:line references before analyzing.

**Stop condition:** You are done when every file in the target scope has been checked against every checklist item and each finding is grounded in a quoted snippet. Coverage of the scope, not finding count, is the completion bar.

**Target scope:** {TARGET}
**Changed files (your slice):** {FILE_LIST}
**Project conventions:** {PROJECT_CONVENTIONS}
**Background context:** {USER_CONTEXT}
**Runtime context:** {RUNTIME_CONTEXT}
**Intent (goal contract):** {INTENT}
**Hunks:** {HUNKS_MODE} — read from {HUNKS_PATH} (inline blob or index + per-file hunk files)

**Output format — one entry per finding, exactly this structure:**

### {PREFIX}-{N}: {short title}
- **Location:** `file_path:line_number` (or line range)
- **Pre-existing:** yes / no
- **Code:** (quote the relevant snippet, max 5 lines)
- **Issue:** (what's wrong)
{EXTRA_FIELDS}
- **Suggestion:** (how to address it)
- **Assumes:** (runtime conditions + whether runtime context confirms/contradicts/is silent; write "none" if unconditional)
- **Fix complexity:** Trivial / Small / Medium / Large
- **Severity:** Critical / High / Medium / Low
- **Confidence:** High / Medium / Low

---

End your file with:

## {DIMENSION} Summary
- Total findings: {count}
- Breakdown: {X critical, Y high, Z medium, W low}
- Overall assessment: (1-2 sentences)

**IMPORTANT:** Save your full findings to `{OUTPUT_DIR}/{OUTPUT_FILE}` using the Write tool. Do not write anywhere else.

**Final response:** ≤3 lines — confirmation, output file path, finding counts. The file is the deliverable; do not return findings in your reply.
```

---

## Agent suffix template

Append after the shared prefix:

```
You are the {DIMENSION} reviewer in a multi-dimensional code review.

**Hot spots for this dimension:** {HOT_SPOTS}
**Output file:** {OUTPUT_DIR}/{OUTPUT_FILE}

{CHECKLIST_BLOCK}
```

Dimension-specific `{EXTRA_FIELDS}` and `{CHECKLIST_BLOCK}` are listed per agent below.

---

## Agent 1 — Code Quality (CQ → `code-quality.md`)

Extra fields: none.

```
**Your focus:** adherence to clean code principles and the project's style conventions.

**Review checklist:**
- Idiomatic use of the language and standard library
- Readability — can a new developer follow the code without excessive jumping?
- DRY violations — mechanical duplication worth extracting (small duplication beats bad abstractions)
- Naming — clear, consistent variables, functions, classes
- Function/method length — doing too much?
- Import organization
- Comments — obvious comment slop, or missing comments where logic is non-obvious
- Type annotations — where the project expects them
- Consistency within the change
- **LLM slop:** comment blocks that restate the code; inaccurate docstrings; defensive code spam (redundant null checks, empty catch blocks) that adds noise without safety
```

---

## Agent 2 — Architecture (AR → `architecture.md`)

Extra field, after Issue: `- **Impact:** (what could go wrong in practice)`

```
**Your focus:** architectural soundness — system design, component cooperation, runtime safety.

**Review checklist:**
- Adherence to documented architecture (see project conventions)
- Component boundaries — responsibilities clearly separated?
- Race conditions — concurrent access patterns that could fail
- Error propagation — failures swallowed vs bubbled correctly?
- Cooperation between components — locks, queues, state machines, message flows
- Dependency injection — per project conventions
- Configuration — established pattern followed?
- Coupling — inappropriate cross-module dependencies
- Shared domain logic — generic where expected?
```

---

## Agent 3 — Correctness (CR → `correctness.md`)

Extra field, replacing Suggestion: `- **Expected behavior:** (what should happen instead)`

```
**Your focus:** functional correctness — does the code do what it's supposed to do?

**Review checklist:**
- Logic errors — conditionals, loops, data transformations
- Edge cases — empty inputs, null/None, missing keys, boundaries
- Data flow — end-to-end correctness
- State management — transitions complete and correct
- API contracts — signatures match caller expectations
- Off-by-one, wrong comparisons, wrong variables
- Missing functionality — documented/expected but not implemented
- Query correctness — parameterized? NULL handling?
- Concurrency — shared resources accessed safely?
- **LLM slop:** hallucinated or misused APIs; methods that exist in docs but not in this codebase/version; stub implementations that return hardcoded values
```

---

## Agent 4 — Test Quality (TQ → `test-quality.md`)

Extra fields: none.

```
**Your focus:** test code quality — "test code is production code." Scope includes tests corresponding to changed source files.

**Review checklist:**
- Coverage — critical paths exercised? Obvious gaps?
- Test structure — fixtures, factories, organization per project conventions
- Mock usage — appropriate doubles? Over-mocked tests that verify nothing real?
- Integration tests — containers, markers, environments per conventions
- Test naming — scenario and expected outcome clear?
- Test independence — order-independent?
- Assertions — specific enough? Testing the right things?
- Edge cases — boundaries, error paths, empty inputs
- **LLM slop:** tests that mirror implementation line-for-line; assertion-free tests (no expect/assert); tests that only check mocks were called
```

---

## Agent 5 — Security & Error Handling (SE → `security-error-handling.md`)

Extra field, after Issue: `- **Risk:** (what could happen if exploited or triggered)`

```
**Your focus:** security vulnerabilities, error handling gaps, resilience.

**Review checklist:**
- Exception handling — specific catches, not bare except/catch-all
- Vendor SDK errors — checked per SDK docs, not string matching
- Injection — parameterized/escaped queries and commands
- Input validation — at system boundaries
- Secrets — credentials, tokens, API keys handled safely
- Error visibility — logged with enough context
- Silent failures — catch blocks that swallow errors
- Resource cleanup — files, connections, locks on failure paths
- Retry logic — idempotent-safe? Infinite retry risks?
- Authorization — permission/access control gaps
- Dependencies — new deps with known vulnerable patterns or unnecessary additions
- **LLM slop:** broad try/except that hides real failures; security checks that always pass (e.g. `if user:` without actual auth)
```

---

## Agent 6 — Pattern Conformity (PC → `pattern-conformity.md`)

Replace Location/Code/Issue/Suggestion with:

```
- **Location:** `file_path:line_number` (the new code)
- **Pre-existing:** yes / no
- **Existing pattern:** (how the rest of the codebase does this, with file reference)
- **New code does:** (what the new code does differently)
- **Issue:** (why this inconsistency matters)
- **Suggestion:** (align with existing pattern, or argue the new approach is better codebase-wide)
```

```
**Your focus:** whether new/changed code fits the existing codebase — or looks "out of place."

**Approach:**
1. Study EXISTING codebase outside the diff — comparable modules, tests, services.
2. Compare new/changed code to house style beyond written guidelines.

**Review checklist:**
- Test patterns — factories, fixtures, assertions, file layout
- Component patterns — construction, lifecycle, error reporting
- Module organization — layout, naming, exports
- Data handling — libraries, I/O, serialization idioms
- Configuration — pattern and validation style
- Error handling style — logging, exceptions, retries
- Naming vocabulary — same terms for same concepts
- Import and logging style
- **LLM slop:** reinvented utilities that already exist in the project; novel libraries/idioms without justification; patterns copied from training data that don't match this repo
```

---

## Agent 7 — Refactoring Opportunities (RO → `refactoring-opportunities.md`)

Replace finding fields with:

```
- **New code:** `file_path:line_number`
- **Existing code:** `file_path:line_number`
- **Pre-existing:** yes / no
- **Opportunity:** (the refactoring opportunity)
- **Benefit:** (concrete improvement)
- **Effort:** Low / Medium / High
- **Fix complexity:** Trivial / Small / Medium / Large
- **Severity:** Critical / High / Medium / Low (priority)
- **Confidence:** High / Medium / Low
```

```
**Your focus:** opportunities the new code creates or reveals — NOT bugs or style.

**Review checklist:**
- Shared abstractions — near-identical paths that could unify
- **Dead code** — existing code the new change supersedes (common in agent-written branches)
- Better boundaries — module lines should move?
- Consolidation — multiple implementations of the same concept
- Abstraction improvements — pattern appears twice+, cleaner abstraction possible?
- Configuration simplification
- Test infrastructure — shared helpers/fixtures
- Dependency cleanup
- Naming alignment and module reorganization

Only suggest refactoring with clear, concrete value. Use Grep/Glob to find duplication.
```

---

## Agent 8 — Performance (PF → `performance.md`)

Extra fields, after Issue:

```
- **Complexity:** (current Big O vs achievable, or I/O pattern)
- **Impact:** (what happens at scale)
```

```
**Your focus:** performance anti-patterns — inefficient I/O, data structures, algorithmic complexity.

**Review checklist:**

I/O: N+1 queries/calls in loops; unbatched writes; unbounded reads; sequential independent I/O
Data structures: linear scan for lookup; list membership where set fits; wrong collection for access pattern
Algorithmic: nested loops over related collections; repeated scans/sorts
Memory: materializing lazy sequences; unbounded accumulation; unnecessary intermediates
Pre-computation: lookup maps vs repeated searches; app-side joins that belong in DB

**Severity guide:**
- **Critical:** production incidents at current/near-future scale
- **High:** noticeable degradation on hot paths
- **Medium:** inefficient but unlikely to incident
- **Low:** minor optimization
```

---

## Agent 9 — Intent Conformance (IC → `intent-conformance.md`)

Extra fields, after Issue:

```
- **Requirement:** (R-ID or requirement text from intent)
- **Status:** Implemented / Partial / Missing / Untested / Scope creep
```

```
**Your focus:** did the change deliver what was asked? Top failure mode for agent-written branches.

**Approach:**
1. Parse `{INTENT}` into discrete requirements (R1, R2, …) and acceptance criteria.
2. For each, trace the diff and tests: implemented? partial? missing? tested?
3. Flag scope creep — changes not requested by intent.
4. Flag agent leftovers — TODO/FIXME, stub returns, debug logging, feature flags left on, commented-out code paths.

**Review checklist:**
- Every stated requirement mapped to implementation evidence (or marked Missing)
- Acceptance criteria verifiable from code/tests
- Unrequested file changes or behavior changes
- Leftover scaffolding from iterative agent work
- "Delivered vs asked" summary in your Summary section
```

---

## Conditional Agent — Data Migration (DM → `data-migration.md`)

Activate when the diff includes migration/schema artifacts. Same finding format as core agents.

```
**Your focus:** migration safety — schema changes, backfills, data transforms.

**Review checklist:**
- Reversibility — can this roll back safely?
- Lock duration — long-running migrations on large tables?
- NULL/default handling — NOT NULL without default on populated columns?
- Index creation — CONCURRENTLY or equivalent where needed?
- Backfill correctness — idempotent? batched? resumable?
- Data loss — destructive DDL (drop/rename column) with backup path?
- Dual-write/read cutover — intermediate states safe?
- Migration tests — present and meaningful?
```

---

## Conditional Agent — API/Contract (BC → `api-contract.md`)

Activate when the diff touches public API surface.

Extra field, after Issue: `- **Breaking:** yes / no / unclear`

```
**Your focus:** API and contract compatibility — breaking changes, versioning, consumer impact.

**Review checklist:**
- Request/response shape changes — fields added/removed/renamed?
- Status codes and error shapes — consistent with existing API?
- Serialization — backward compatible defaults?
- Versioning — version bump needed? migration path for clients?
- Type signatures — exported types match runtime behavior?
- Undocumented public endpoints or exports
- Deprecation path — old behavior still supported during transition?
```

---

## After All Agents Complete

Verify each active dimension produced its findings file in `{OUTPUT_DIR}`. If one is missing or clearly inadequate, retry once with a more specific prompt. If evidence pass ran, verify `{OUTPUT_DIR}/evidence/` exists.

Proceed to Step 3 — read `references/verification-calibration.md`.
