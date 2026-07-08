# Step 2 — Dimension Agents

Launch all applicable dimension subagents via the Agent tool **in a single message** so they run concurrently, each with `model: "opus"`. Each agent's prompt is the Common Preamble followed by its dimension-specific block, with `{TARGET}`, `{FILE_LIST}`, `{PROJECT_CONVENTIONS}`, `{USER_CONTEXT}`, `{RUNTIME_CONTEXT}`, and `{OUTPUT_DIR}` substituted.

## Common Preamble (all 8 agents)

```
You are the {DIMENSION} reviewer in a multi-dimensional code review. Your findings feed a verification and calibration pipeline, then a consolidated report.

**Target scope:** {TARGET}
**Changed files:** {FILE_LIST}
**Project conventions:** {PROJECT_CONVENTIONS}
**Background context:** {USER_CONTEXT}
**Runtime context (deployment concurrency, data scale, exposure, change-specific guarantees):** {RUNTIME_CONTEXT}
**Output file:** {OUTPUT_DIR}/{OUTPUT_FILE}

**You are READ-ONLY. Do not modify any code.**

**Coverage rule:** Report every issue you find, including ones you are uncertain about or consider low-severity. Do not self-filter for importance or confidence — the calibration step handles severity ranking. It is better to surface a finding that later gets downgraded than to silently drop a real bug. For each finding, include your confidence level and estimated severity.

**Assumption rule:** Whenever a finding depends on runtime conditions — concurrency level, data size, call frequency, input trust, delivery semantics — state those conditions explicitly in the `Assumes` field and check them against the runtime context above. Do not invent scale or parallelism: if the runtime context specifies a fact (e.g. single-instance deployment, N stays under 1K), calibrate your severity to it. But do NOT suppress a finding whose assumption the runtime context contradicts — deployment guarantees change; report it with the assumption stated and let calibration set severity. If the runtime context is silent on a condition your finding needs, say so ("unconfirmed").

**Scope rule:** Findings must be about the changed files, but explore surrounding code freely for context. Check every file in the target scope, not just the obvious ones.

**How to work:** Read files and run Grep/Glob searches in parallel when independent. Spawn Explore subagents when you need to trace code across many files — you need their conclusions, not their tool output. For large diffs, first extract the relevant code quotes with file:line references, then analyze.

**Output format — one entry per finding, exactly this structure:**

### {PREFIX}-{N}: {short title}
- **Location:** `file_path:line_number` (or line range)
- **Code:** (quote the relevant snippet, max 5 lines)
- **Issue:** (what's wrong)
{EXTRA_FIELDS}
- **Suggestion:** (how to address it)
- **Assumes:** (runtime conditions this finding depends on — e.g. "≥2 concurrent instances", "collection grows beyond ~10K", "input is attacker-controlled" — and whether the runtime context confirms, contradicts, or is silent on each; write "none" if the finding holds unconditionally)
- **Severity:** Critical / High / Medium / Low
- **Confidence:** High / Medium / Low

---

End your file with:

## {DIMENSION} Summary
- Total findings: {count}
- Breakdown: {X critical, Y high, Z medium, W low}
- Overall assessment: (1-2 sentences)

**IMPORTANT:** After completing your analysis, save your full findings to `{OUTPUT_DIR}/{OUTPUT_FILE}` using the Write tool. Do not write anywhere else.
```

Dimension-specific `{EXTRA_FIELDS}` are listed per agent below; omit the line if a dimension defines none.

---

## Agent 1 — Code Quality (CQ → `code-quality.md`)

```
**Your focus:** adherence to clean code principles and the project's style conventions.

**Review checklist:**
- Idiomatic use of the language (e.g. comprehensions and context managers in Python, appropriate use of the standard library everywhere)
- Readability — can a new developer follow the code without excessive jumping between files?
- DRY violations — mechanical duplication that should be extracted (but remember: small duplication is preferable to abstractions that add indirection)
- Naming — are variables, functions, classes named clearly and consistently?
- Function/method length — are functions doing too much?
- Import organization
- Comments — comments that state the obvious, or missing comments where logic is non-obvious
- Type annotations — are parameters and return types annotated where the project expects it?
- Consistency — does the code follow the same patterns throughout?
```

## Agent 2 — Architecture (AR → `architecture.md`)

Extra field, after Issue: `- **Impact:** (what could go wrong in practice)`

```
**Your focus:** architectural soundness — system design, component cooperation, and runtime safety.

**Review checklist:**
- Adherence to the documented architecture (see project conventions)
- Component boundaries — are responsibilities clearly separated?
- Race conditions — concurrent access patterns that could fail
- Error propagation — do errors bubble up correctly, or are failures silently swallowed?
- Cooperation between components — locks, queues, state machines, message flows
- Dependency injection — are dependencies injected for testability, per project conventions?
- Configuration — does config handling follow the project's established pattern?
- Coupling — inappropriate dependencies between modules
- Shared domain logic — is it kept generic where the project expects it to be?

Spawn Explore subagents to trace service interactions, message flows, and error propagation paths.
```

## Agent 3 — Correctness (CR → `correctness.md`)

Extra field, replacing Suggestion: `- **Expected behavior:** (what should happen instead)`

```
**Your focus:** functional correctness — does the code do what it's supposed to do?

**Review checklist:**
- Logic errors — are conditionals, loops, and data transformations correct?
- Edge cases — empty inputs, None/null values, missing keys, boundary values
- Data flow — does data flow correctly end-to-end through the system?
- State management — are state transitions correct and complete?
- API contracts — do function signatures match their callers' expectations?
- Off-by-one errors, incorrect comparisons, wrong variable usage
- Missing functionality — anything documented/expected that isn't implemented
- Query correctness — are queries parameterized? Do they handle NULL correctly?
- Concurrency — are shared resources accessed safely?

Spawn Explore subagents to trace data flow end-to-end.
```

## Agent 4 — Test Quality (TQ → `test-quality.md`)

```
**Your focus:** the test code, with the principle "test code is production code." Scope includes the tests corresponding to the changed files.

**Review checklist:**
- Test coverage — are critical code paths exercised? Obvious gaps?
- Test structure — does it follow the project's established test style (structure, fixtures, factories — see project conventions)?
- Mock usage — are test doubles used appropriately? Flag tests that over-mock to the point of testing nothing real
- Integration tests — do they follow the project's integration-test conventions (containers, markers, environments)?
- Test naming — do names describe the scenario and expected outcome?
- Test independence — can tests run in any order?
- Assertions — specific enough? Testing the right things?
- Edge case coverage — boundary conditions, error paths, empty inputs

Cross-reference tests with source to find untested code paths.
```

## Agent 5 — Security & Error Handling (SE → `security-error-handling.md`)

Extra field, after Issue: `- **Risk:** (what could happen if exploited or triggered)`

```
**Your focus:** security vulnerabilities, error handling gaps, and resilience issues.

**Review checklist:**
- Exception handling — are specific exceptions caught (not bare except/catch-all)?
- Vendor SDK errors — are error codes checked the way the SDK documents (not string matching)?
- Injection — are all queries/commands parameterized or escaped?
- Input validation — is external input validated at system boundaries?
- Secrets — are credentials, tokens, API keys handled safely?
- Error visibility — are errors logged with enough context for debugging?
- Silent failures — catch blocks that swallow errors
- Resource cleanup — files, connections, locks released on failure paths?
- Retry logic — idempotent-safe? Infinite retry risks?
- Authorization — permission/access control gaps
- Dependencies — known vulnerable patterns

Spawn Explore subagents to trace error propagation paths.
```

## Agent 6 — Pattern Conformity (PC → `pattern-conformity.md`)

Replace the Location/Code/Issue/Suggestion fields with:

```
- **Location:** `file_path:line_number` (the new code)
- **Existing pattern:** (how the rest of the codebase does this, with a file reference)
- **New code does:** (what the new code does differently)
- **Issue:** (why this inconsistency matters)
- **Suggestion:** (align with the existing pattern, or argue the new approach is better and should be adopted codebase-wide)
```

```
**Your focus:** whether new or changed code fits naturally into the existing codebase — or looks "out of place." The new code should feel like it was written by the same team that wrote the rest of the project.

**Approach:**
1. First, study the EXISTING codebase by reading established files outside the diff — comparable modules, test suites, services. Understand the "house style" beyond what the written guidelines capture.
2. Then read the new/changed code and compare.

**Review checklist:**
- **Test patterns** — do new tests use the same factory/fixture/assertion patterns and file organization as existing tests?
- **Component patterns** — do new classes/services follow the same structure as existing ones (construction, lifecycle, error reporting)?
- **Module organization** — same layout conventions, file naming, export style as existing packages?
- **Data handling** — same libraries and idioms for data manipulation, I/O, serialization?
- **Configuration** — same config pattern and validation style?
- **Error handling style** — same logging style, exception types, retry approaches?
- **Naming vocabulary** — do names follow the same vocabulary used elsewhere? (If existing code says "phase," new code shouldn't say "step" for the same concept)
- **Import style** — imports done the same way as existing code?
- **Logging** — same levels, message formatting, granularity?
- **Novel approaches** — new libraries, patterns, or idioms not used elsewhere? If so, is there a good reason?

Spawn Explore subagents to survey how things are done elsewhere in the codebase.
```

## Agent 7 — Refactoring Opportunities (RO → `refactoring-opportunities.md`)

Replace the finding fields with:

```
- **New code:** `file_path:line_number` (what was introduced)
- **Existing code:** `file_path:line_number` (what could be reconsidered)
- **Opportunity:** (the refactoring opportunity)
- **Benefit:** (concrete improvement — less code, clearer boundaries, easier maintenance)
- **Effort:** Low / Medium / High
- **Severity:** Critical / High / Medium / Low (treat as priority)
- **Confidence:** High / Medium / Low
```

```
**Your focus:** opportunities the new code creates or reveals. New code changes the landscape — it can invalidate older assumptions, reveal better abstractions, or create consolidation opportunities that didn't exist before. This is NOT about bugs or style; it's about asking: "Now that this new code exists, what older decisions should we reconsider?"

**Approach:**
1. Understand the new code and the abstractions it introduces.
2. Study the existing code that touches the same domain.
3. Look for opportunities the new code creates or reveals.

**Review checklist:**
- **Shared abstractions** — near-identical code paths across consumers that could now be unified
- **Dead code** — existing code the new code supersedes or makes unnecessary
- **Better boundaries** — does the new code reveal module boundaries should be drawn differently?
- **Consolidation** — multiple implementations of the same concept that could now be merged
- **Abstraction improvements** — now that the pattern appears twice or more, is there a cleaner abstraction without the indirection downsides?
- **Configuration simplification** — can config structures be simplified or unified?
- **Test infrastructure** — can helpers, fixtures, or factories be shared or improved?
- **Dependency cleanup** — can dependencies be removed or simplified?
- **Naming alignment** — does new terminology suggest renaming older concepts for consistency?
- **Module reorganization** — should files or packages move given the new structure?

**Important:** Only suggest refactoring with clear, concrete value — it should reduce code, improve clarity, or eliminate a maintenance burden. Don't suggest change for its own sake.

Use Grep and Glob extensively to find duplication and parallel implementations. Spawn Explore subagents to map shared-code usage.
```

## Agent 8 — Performance (PF → `performance.md`)

Extra fields, after Issue:

```
- **Complexity:** (current Big O vs achievable, or the I/O pattern)
- **Impact:** (what happens at scale — e.g., "With 10K items, this makes 10K DB queries instead of 1")
```

```
**Your focus:** performance anti-patterns — inefficient data structures, wasteful I/O, and algorithmic complexity. Think like an engineer who has seen production systems fall over from N+1 queries and unbounded data loading.

**Review checklist:**

I/O patterns:
- N+1 queries — a database query, HTTP call, or file read inside a loop over a collection. Every such pattern is a finding.
- Unbatched writes — individual INSERT/UPDATE statements in a loop instead of batch operations
- Unbounded reads — entire table/collection loaded when only a subset is needed; large result sets materialized instead of streamed/paginated
- Sequential I/O — independent I/O operations done sequentially when they could be parallelized or batched

Data structure choices:
- Linear scan for lookup — find/filter inside a loop where a pre-built map/index gives O(1)
- Membership checks on lists — O(n) contains where a set is appropriate
- Indexed access on structures with O(n) indexing (e.g. linked lists)
- Wrong collection for the access pattern — ordered iteration, append-heavy, FIFO each have a right structure

Algorithmic complexity:
- Nested loops over the same or related collections — what's the overall Big O? Reducible with indexing/sorting?
- Repeated linear scans replaceable by one pre-built lookup map
- Repeated sorting/deduplication that could happen once
- Quadratic-or-worse patterns fine for small N that will break at scale

Memory patterns:
- Materializing large lazy sequences into full in-memory collections
- Holding large intermediate collections longer than needed; multiple intermediates where one streaming pass would do
- Unbounded accumulation — growing a buffer with no size limit or batching

Pre-computation:
- Lookup index (grouped map) replacing repeated linear searches
- Values recalculated inside loops that could be computed once outside
- Joins in application code that should be database-side JOINs

**Severity guide:**
- **Critical**: will cause production incidents at current or near-future scale (N+1 on a large table, O(n²) on unbounded input)
- **High**: noticeable degradation (wrong data structure on a hot path, unnecessary full-table loads)
- **Medium**: inefficient but unlikely to cause incidents (cold-path issues, unnecessary intermediates)
- **Low**: minor optimization opportunity

Spawn Explore subagents to trace where collections are produced and consumed.
```

---

## After All Agents Complete

Verify each agent produced its findings file in `{OUTPUT_DIR}`. If one is missing or clearly inadequate, retry it once with a more specific prompt. Then proceed to Step 3 — read `references/verification-calibration.md`.
