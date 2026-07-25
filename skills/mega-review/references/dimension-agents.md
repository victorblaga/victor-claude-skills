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

**Slop ownership:** a dedicated AI Slop (AS) reviewer owns cross-cutting bloat — unnecessary defensiveness, single-caller abstractions, unrequested config, ceremony, narration comments, dead scaffolding. Flag the slop your own checklist names and move on; do not hunt outside your lens. Overlap is merged later.

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
- **Would it have failed?** For every test covering a bug fix or a behavior change, ask whether it would fail against the pre-change code. A test that passes both before and after documents the implementation instead of pinning the behavior, and it is the most common way a diff arrives with coverage that would not have caught the bug it cites. Where the diff makes this checkable — the old branch is still visible, a condition is inverted, a constant changed — state the answer. Where it is not checkable from the diff alone, report the test as unproven rather than adequate.
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

## Agent 10 — AI Slop (AS → `ai-slop.md`)

Extra fields, after Issue:

```
- **Slop class:** S1 defensive excess / S2 speculative generality / S3 ceremony / S4 low-value test / S5 narration / S6 reinvention / S7 abandoned scaffolding / S8 hedged deliverable
- **Load-bearing check:** (what you searched for and what you found — callers, subclasses, config keys, dynamic or string access, tests, a requirement in intent, a failure mode this repo actually hit. "Nothing found after checking X, Y, Z" is a finding; "could not determine" is not.)
- **Removal:** (the concrete deletion — what goes, what replaces it if anything, approximate lines removed)
```

```
**Your focus:** code that works, breaks nothing, and earns nothing. Machine-written code accumulates weight by default — guards with no failure mode, abstractions with one caller, tests that assert on mocks, comments narrating the diff. Every other reviewer asks "is this wrong?" You ask "why is this here at all?"

**Why this dimension exists.** Coding models are trained against rewards that fire when the tests
pass and the build stays green. Nothing in that signal charges for weight: an extra guard, a wider
interface, one more mock-asserting test all score the same as the lean version, and some score
better, because they make a green run likelier. The cost of the weight arrives months later and
lands on a maintainer — precisely the signal the training loop cannot reach. So expect this class of
defect by default and in volume. It is the predictable output of the process, not an occasional
lapse, and it will not look like a mistake, because locally it never was one.

**The test — carried cost with no beneficiary.** A slop finding is not a bug and not a matter of taste. It is code a maintainer must read, trust, and keep working forever in exchange for nothing. You must be able to name the cost and fail to name the beneficiary.

**Slop classes:**

- **S1 — Defensive excess.** try/except, null guards, `?.` chains, isinstance checks, fallbacks, retries, and default values with no named failure mode. Error handling that turns a loud crash into a silent wrong answer. Nested guards where the outer already covers the inner. The same validation repeated at three layers.
- **S2 — Speculative generality.** Interfaces, base classes, registries, strategy/factory/plugin indirection, and type parameters with exactly one implementation or one caller. Config keys, env vars, and constructor options nobody asked for. Extension points for a hypothetical second use case. Parameters no caller ever varies.
- **S3 — Ceremony.** Wrappers whose whole body is one delegating call; helper layers that add a name and nothing else; single-field value objects; a class where a function would do; INFO logging on every step; docstrings on every trivial private function.
- **S4 — Low-value tests.** Tests that assert only that a mock was called; tests that restate the implementation line for line; assertion-free tests; ten parameterized cases covering one branch; tests of library or framework behavior; snapshots nobody reads; twenty lines of setup for a trivial assertion. Coverage theater — the number goes up, nothing is caught.
- **S5 — Narration.** Comments and docs describing the work rather than the code's reason for existing: "Enhanced X to…", "Now also handles…", "This is backwards compatible", banner dividers, docstrings restating the signature. Unrequested README / CHANGELOG / summary files.
- **S6 — Reinvention.** A helper duplicating an existing project utility or a standard-library call; a second way to do what the codebase already does one way; hand-rolled parsing, date math, retry, or caching where a dependency already in the manifest does it.
- **S7 — Abandoned scaffolding.** Leftovers from iterative agent work: both paths alive after a migration, compatibility shims for callers that do not exist, TODO/FIXME, commented-out alternatives, debug logging, unused imports / parameters / exports, branches behind a constant that is never the other value.
- **S8 — Hedged deliverable.** A decided change shipped with an escape hatch nobody asked for: a feature flag or env toggle guarding approved work, a fallback to the old path, the old implementation kept beside the new one "so we can revert easily", a try/except wrapped around the new code, or an invented cap / timeout / retry to make the change feel safer. Check `{INTENT}` — if the hedge is not in the goal contract, it is slop, and it is the class that costs most, because it leaves two live behaviors in the codebase.

**Before you flag — the load-bearing check.** Search for what depends on the code: callers, subclasses, config references, string or reflective access, tests, and any requirement in `{INTENT}`. Then ask whether the construct guards a real boundary. Flag only when that search comes back empty, and record what you searched in the `Load-bearing check` field. "I don't see why this is here" is not a finding. "No caller, no config key, no test, and the type already guarantees non-null" is.

**Never flag:**
- Guards on data crossing a trust boundary — HTTP request bodies, CLI arguments, file or network parsing, third-party API responses, deserialization.
- `finally` blocks, context managers, and resource cleanup on failure paths.
- A catch that converts one error type into a domain error, or one that keeps a long-running loop alive per item.
- Retry with explicit backoff around a known-flaky remote call.
- A short test that makes one real assertion — brevity is not low value.
- House style. If `{PROJECT_CONVENTIONS}` or the surrounding code docstrings everything, wraps everything, or configures everything, that is this repo's bar; deviation from it belongs to Pattern Conformity, not to you.
- Suspected duplication you have not located — no S6 finding without a `file:line` for the original.

**Severity — grade carried cost, not failure probability:**
- **High** — slop that hides defects or blocks change: swallowed errors, mock-only or assertion-free tests standing in for real coverage, two live code paths after a migration, a flag or fallback keeping replaced behavior reachable.
- **Medium** — structure a maintainer carries forever with nothing behind it: single-implementation abstraction, unrequested config surface, wrapper layers, a reinvented utility, a substantial block of dead scaffolding.
- **Low** — local noise: narration comments, trivial docstrings, one redundant guard, an unused import.
- **Critical** — only when the slop has a live correctness or security consequence. Report it anyway; Correctness or Security will likely report it too and the duplicate is merged later.

**Do not soften a finding because the fix is a deletion.** Deletions are the cheapest fixes in the report.

**Review checklist:**
- Every added guard, catch, fallback, and default — is there a named failure mode?
- Every new abstraction, interface, and config key — how many implementations and callers? Was it asked for?
- Every new test — what defect would it catch that another test would not?
- Every new comment and doc line — does it explain why, or narrate what?
- Every new helper — does the project or standard library already have it?
- Anything left half-migrated, flagged, stubbed, or commented out.
- The diff as a whole: what fraction of the added lines is load-bearing?

**Add a slop profile to your Summary section:**
- Added lines in scope: ~{N}
- Removable slop lines (your estimate): ~{M} ({P}%)
- Findings per class: S1=… S2=… S3=… S4=… S5=… S6=… S7=… S8=…
- Dominant class, and what it says about how this change was produced (1-2 sentences)
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
