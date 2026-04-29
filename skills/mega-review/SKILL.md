---
name: mega-review
description: >
  Comprehensive multi-dimensional code review producing a structured markdown report.
  Use when the user asks for "mega-review", "mega review", "deep review", "comprehensive review",
  "full review", "review everything", "review all dimensions", or any variation requesting a
  thorough multi-dimensional code review that produces a document.
  Do NOT trigger for one-off code cleanup, or when the user wants code changes —
  this skill is strictly read-only analysis that outputs a report.
---

# Mega Review Skill

Comprehensive, parallel code review across multiple dimensions. Each dimension is handled by a dedicated subagent. A final Consolidator agent merges all findings into one report.

**CRITICAL RULES:**
- **READ-ONLY** — never modify any code. Only produce the review report.
- **Use subagents liberally** — each dimension runs as a parallel subagent via the Agent tool.
- **Output is always under a dedicated review directory** — see Output Directory below.

## Agentic Execution Notes (Claude Opus 4.7)

Opus 4.7 is meaningfully better at finding bugs than prior models, but code-review harnesses tuned for earlier models may see lower *measured* recall. This happens because Opus 4.7 follows instructions like "only report high-severity issues" or "don't nitpick" more faithfully—it may identify a bug and then choose not to report it. To counter this:

- **Coverage over filtering**: In every dimension prompt, explicitly instruct agents to *report every issue they find*, including uncertain or low-severity ones. The calibration step handles severity filtering; the dimension agents' job is coverage.
- **Effort**: Run dimension subagents at `xhigh` effort. Their job is thorough investigation, not speed.
- **Parallel subagents**: Launch all applicable dimension subagents simultaneously in a single turn. Opus 4.7 spawns fewer subagents by default—explicitly fan out.
- **Parallel tool calls**: Tell subagents to read files and run searches in parallel when independent.
- **Literal scope**: State explicitly when a checklist applies to all files (e.g., "Check *every* file in the target scope, not just the obvious ones").
- **Subagent mental test**: Before spawning an Explore subagent from a dimension agent, apply the test: "Will I need this tool output again, or just the conclusion?" Dimension agents should typically only need the conclusion, so they can spawn fresh-context subagents freely. The Consolidator sees only the dimension summaries, keeping its context lean.
- **Quote-grounding for large scopes**: When reviewing large diffs or many files, dimension subagents should extract relevant code quotes with file:line references before analyzing. This cuts through noise and keeps reasoning anchored to specific evidence.

## Parse the Request

Extract from the user's message:

1. **Target scope** — resolved using this priority:
   a. **User-specified** — if the user names specific files, a directory, a module, or a PR number → use that
   b. **Open PR** — if there is an open PR on the current branch → review the PR diff
   c. **Diff to dev** — otherwise → review the diff from `dev` to current state (committed + uncommitted)
   d. **Fallback** — if none of the above yields changed files → review `src/sitesentry_pipelines/`
2. **Focus areas** (optional) — a subset of the dimensions below. If unspecified, run ALL dimensions.
3. **Output directory** — see Output Directory section below. The user may override.
4. **Background context** — any migration context, architecture notes, or design docs the user provides inline. Pass this to every subagent.

### Output Directory

All review artifacts (main report + any per-dimension files) go into a single dedicated directory:

```
.docs/reviews/YYYY-MM-DD-pr-NNN-XXXXX/
```

Where:
- `YYYY-MM-DD` — today's date
- `pr-NNN` — the PR number (e.g. `pr-97`). If there's no PR, use `diff` instead (e.g. `2026-03-11-diff-a3b2c`)
- `XXXXX` — 5 random alphanumeric characters to avoid collisions

Create this directory before launching subagents. The main consolidated report goes at:

```
.docs/reviews/YYYY-MM-DD-pr-NNN-XXXXX/report.md
```

Each dimension subagent MUST write its findings to a file in the same directory (e.g. `code-quality.md`, `architecture.md`, etc.). Pass the full `{OUTPUT_DIR}` path to every subagent. Subagents must NEVER write files outside this directory.

### Scope Resolution

Run these checks **before** launching subagents to determine the target scope:

```bash
# 1. Check for open PR on current branch
gh pr view --json number,title,baseRefName 2>/dev/null

# 2. If PR exists, get the changed file list
gh pr diff --name-only

# 3. If no PR, get diff from dev (committed + uncommitted)
git diff dev...HEAD --name-only
git diff --name-only  # unstaged changes
git diff --cached --name-only  # staged changes
```

Combine the file lists and deduplicate. Pass this file list to each subagent so they know which files to focus on. Subagents should still explore surrounding code for context, but findings should be scoped to the changed files.

## Dimensions

There are 8 review dimensions. Each runs as a **separate parallel subagent**.

If the user specifies focus areas, map them to these dimensions and only run the matching ones. If unspecified, run all 8.

| # | Dimension | Keyword triggers |
|---|-----------|-----------------|
| 1 | Code Quality | "code quality", "style", "pythonic", "readability", "DRY", "clean code" |
| 2 | Architecture | "architecture", "race conditions", "service cooperation", "error propagation", "design" |
| 3 | Correctness | "correctness", "feature complete", "implementation", "validate", "functionality" |
| 4 | Test Quality | "tests", "test quality", "test coverage", "mocks", "factories", "test code" |
| 5 | Security & Error Handling | "security", "error handling", "edge cases", "validation", "resilience" |
| 6 | Pattern Conformity | "patterns", "consistency", "conventions", "fit in", "out of place", "existing patterns", "codebase patterns" |
| 7 | Refactoring Opportunities | "refactor", "consolidate", "abstraction", "simplify", "reorganize", "technical debt", "opportunities" |
| 8 | Performance | "performance", "N+1", "batch", "Big O", "complexity", "slow", "data structures", "queries", "indexing", "memory" |

## Execution

### Step 1: Gather Context

Before launching subagents, read the project's `CLAUDE.md`. If it references additional guideline or convention documents, read those too. Summarize the project conventions relevant to each dimension and pass them to each subagent as `{PROJECT_CONVENTIONS}`. Each subagent must respect these conventions when evaluating code.

### Model Tiers for Subagents

Match the model to the cognitive demand of each step. Use the `model` parameter on the Agent tool:

| Step | Model | Rationale |
|------|-------|-----------|
| Dimension subagents (Step 2) | `opus` | Bug-hunting and design-smell detection across large diffs — depth matters more than cost |
| Verification subagents (Step 3, Phase 1) | `sonnet` | Factual cross-checking — mechanical |
| Calibrator (Step 3, Phase 2) | `opus` | Judgment calls on severity, weighing trade-offs |
| Architectural Synthesis (Step 4) | `opus` | Meta-analysis, connecting dots across dimensions, design thinking |
| Consolidator (Step 5) | `opus` | Follows tool-use instructions reliably — sonnet occasionally self-interprets "save the report" as "return text to the parent" and skips the Write call, leaving the review without a final report.md |

**The principle:** analysis, synthesis, judgment, AND thorough dimension review require high brainpower (opus). Fact-checking can run lower (sonnet). Dimension agents specifically benefit from opus because they set the ceiling on what the later stages can work with — a missed finding at Step 2 cannot be recovered later. The Consolidator is kept on opus because it is the terminal step — a silent failure here throws away the work of every other agent.

### Step 2: Launch Dimension Subagents (in parallel)

Launch all applicable dimension subagents **in a single message** so they run concurrently. Each subagent uses the Agent tool with `model: "opus"`.

**Important:** Each subagent must be told:
- It is READ-ONLY — do not modify any source code
- The target scope to review
- The output directory `{OUTPUT_DIR}` — subagents must write their findings file here, nowhere else
- The relevant project guidelines for its dimension
- Any background context the user provided
- To use Explore subagents when it needs to trace code across files
- To return its findings in the exact format specified below AND save them to a file in `{OUTPUT_DIR}`

---

#### Subagent 1: Code Quality

```
You are a Code Quality reviewer. Analyze the target code for adherence to clean code principles and project style conventions.

**Target scope:** {TARGET}
**Project conventions:** {PROJECT_CONVENTIONS}
**Background context:** {USER_CONTEXT}

**You are READ-ONLY. Do not modify any code.**

**Coverage rule — critical for Opus 4.7:** Report every issue you find, including ones you are uncertain about or consider low-severity. Do not self-filter for importance or confidence at this stage; the calibration step will handle severity ranking. It is better to surface a finding that later gets downgraded than to silently drop a real bug. For each finding, include your confidence level and estimated severity.

**Review checklist:**
- Pythonic idioms (list comprehensions, context managers, f-strings, walrus operator where appropriate)
- Readability — can a new developer follow the code without excessive jumping between files?
- DRY violations — is there mechanical duplication that should be extracted? (But remember: small duplication is preferable to abstractions that add indirection)
- Naming — are variables, functions, classes named clearly and consistently?
- Function/method length — are functions doing too much?
- Import organization
- Comments — are there comments that state the obvious, or missing comments where logic is non-obvious?
- Type annotations — are all function parameters and return types annotated?
- Consistency — does the code follow the same patterns throughout?

**Output directory:** {OUTPUT_DIR}

**How to search:** Read files, use Grep and Glob to explore. Spawn Explore subagents when you need to trace patterns across many files.

**Output format — follow exactly:**

For each finding:

### CQ-{N}: {short title}
- **Location:** `file_path:line_number` (or line range)
- **Code:** (quote the relevant snippet, keep it short — max 5 lines)
- **Issue:** (describe what's wrong)
- **Suggestion:** (how it should look or what principle it violates)
- **Severity:** Critical / High / Medium / Low

---

End with:

## Code Quality Summary
- Total findings: {count}
- Breakdown: {X critical, Y high, Z medium, W low}
- Overall assessment: (1-2 sentences)

**IMPORTANT:** After completing your analysis, save your full findings to `{OUTPUT_DIR}/code-quality.md` using the Write tool.
```

#### Subagent 2: Architecture

```
You are an Architecture reviewer. Analyze the target code for architectural soundness, focusing on system design, service cooperation, and runtime safety.

**Target scope:** {TARGET}
**Project conventions:** {PROJECT_CONVENTIONS}
**Background context:** {USER_CONTEXT}

**You are READ-ONLY. Do not modify any code.**

**Coverage rule — critical for Opus 4.7:** Report every issue you find, including ones you are uncertain about or consider low-severity. Do not self-filter for importance or confidence at this stage; the calibration step will handle severity ranking. It is better to surface a finding that later gets downgraded than to silently drop a real bug. For each finding, include your confidence level and estimated severity.

**Review checklist:**
- Adherence to the documented architecture (orchestrator-managed vs standalone pipeline patterns)
- Service boundaries — are responsibilities clearly separated?
- Race conditions — are there concurrent access patterns that could fail?
- Error propagation — do errors bubble up correctly? Are failures visible or silently swallowed?
- Service cooperation — do services coordinate correctly (locks, queues, state machines)?
- Constructor injection — are dependencies injected for testability?
- Configuration — are config classes frozen dataclasses with from_env()?
- Storage patterns — does each pipeline have its own storage.py?
- Coupling — are there inappropriate dependencies between modules?
- Shared domain logic — is it pipeline-agnostic as it should be?

**Output directory:** {OUTPUT_DIR}

**How to search:** Read files, use Grep and Glob to explore. Spawn Explore subagents to trace service interactions, message flows, and error propagation paths.

**Output format — follow exactly:**

For each finding:

### AR-{N}: {short title}
- **Location:** `file_path:line_number` (or line range, or cross-file reference)
- **Code:** (quote relevant snippet if applicable)
- **Issue:** (describe the architectural concern)
- **Impact:** (what could go wrong in practice)
- **Suggestion:** (how to improve)
- **Severity:** Critical / High / Medium / Low

---

End with:

## Architecture Summary
- Total findings: {count}
- Breakdown: {X critical, Y high, Z medium, W low}
- Overall assessment: (1-2 sentences)

**IMPORTANT:** After completing your analysis, save your full findings to `{OUTPUT_DIR}/architecture.md` using the Write tool.
```

#### Subagent 3: Correctness

```
You are a Correctness reviewer. Analyze the target code for functional correctness — does the code do what it's supposed to do?

**Target scope:** {TARGET}
**Project conventions:** {PROJECT_CONVENTIONS}
**Background context:** {USER_CONTEXT}

**You are READ-ONLY. Do not modify any code.**

**Coverage rule — critical for Opus 4.7:** Report every issue you find, including ones you are uncertain about or consider low-severity. Do not self-filter for importance or confidence at this stage; the calibration step will handle severity ranking. It is better to surface a finding that later gets downgraded than to silently drop a real bug. For each finding, include your confidence level and estimated severity.

**Review checklist:**
- Logic errors — are conditionals, loops, and data transformations correct?
- Edge cases — what happens with empty inputs, None values, missing keys, boundary values?
- Data flow — does data flow correctly through the pipeline stages?
- State management — are state transitions correct and complete?
- API contracts — do function signatures match their callers' expectations?
- Off-by-one errors, incorrect comparisons, wrong variable usage
- Missing functionality — is there anything documented/expected that isn't implemented?
- SQL correctness — are queries parameterized? Do they handle NULL correctly?
- Concurrency — are shared resources accessed safely?

**Output directory:** {OUTPUT_DIR}

**How to search:** Read files, use Grep and Glob. Spawn Explore subagents to trace data flow end-to-end through pipeline stages.

**Output format — follow exactly:**

For each finding:

### CR-{N}: {short title}
- **Location:** `file_path:line_number` (or line range)
- **Code:** (quote the relevant snippet)
- **Issue:** (what's wrong or could go wrong)
- **Expected behavior:** (what should happen instead)
- **Severity:** Critical / High / Medium / Low

---

End with:

## Correctness Summary
- Total findings: {count}
- Breakdown: {X critical, Y high, Z medium, W low}
- Overall assessment: (1-2 sentences)

**IMPORTANT:** After completing your analysis, save your full findings to `{OUTPUT_DIR}/correctness.md` using the Write tool.
```

#### Subagent 4: Test Quality

```
You are a Test Quality reviewer. Analyze the test code with the principle: "test code is production code."

**Target scope:** {TARGET} (and corresponding tests in tests/)
**Project conventions:** {PROJECT_CONVENTIONS}
**Background context:** {USER_CONTEXT}

**You are READ-ONLY. Do not modify any code.**

**Coverage rule — critical for Opus 4.7:** Report every issue you find, including ones you are uncertain about or consider low-severity. Do not self-filter for importance or confidence at this stage; the calibration step will handle severity ranking. It is better to surface a finding that later gets downgraded than to silently drop a real bug. For each finding, include your confidence level and estimated severity.

**Review checklist:**
- Test coverage — are critical code paths exercised? Are there obvious gaps?
- Test structure — function-based tests (no classes), clear arrange/act/assert
- Factories — are make_<thing>(**overrides) factories used with Faker defaults?
- Shared factories in tests/shared/factories.py; domain-specific helpers local to test file
- Mock usage — are mocks used appropriately? Flag tests that over-mock to the point of testing nothing real
- monkeypatch.setattr() on module objects (not MagicMock) for I/O faking
- Integration tests — do they use testcontainers + LocalStack? Marked with @pytest.mark.integration?
- Test naming — do names describe the scenario and expected outcome?
- Test independence — can tests run in any order?
- Assertions — are they specific enough? Do they test the right things?
- Edge case coverage — are boundary conditions, error paths, and empty inputs tested?

**Output directory:** {OUTPUT_DIR}

**How to search:** Read test files, Grep for test patterns, Glob for test file locations. Cross-reference with source to find untested code paths.

**Output format — follow exactly:**

For each finding:

### TQ-{N}: {short title}
- **Location:** `file_path:line_number` (or "missing test for X")
- **Code:** (quote relevant test snippet if applicable)
- **Issue:** (what's wrong with the test, or what's missing)
- **Suggestion:** (how to improve)
- **Severity:** Critical / High / Medium / Low

---

End with:

## Test Quality Summary
- Total findings: {count}
- Breakdown: {X critical, Y high, Z medium, W low}
- Overall assessment: (1-2 sentences)

**IMPORTANT:** After completing your analysis, save your full findings to `{OUTPUT_DIR}/test-quality.md` using the Write tool.
```

#### Subagent 5: Security & Error Handling

```
You are a Security & Error Handling reviewer. Analyze the target code for security vulnerabilities, error handling gaps, and resilience issues.

**Target scope:** {TARGET}
**Project conventions:** {PROJECT_CONVENTIONS}
**Background context:** {USER_CONTEXT}

**You are READ-ONLY. Do not modify any code.**

**Coverage rule — critical for Opus 4.7:** Report every issue you find, including ones you are uncertain about or consider low-severity. Do not self-filter for importance or confidence at this stage; the calibration step will handle severity ranking. It is better to surface a finding that later gets downgraded than to silently drop a real bug. For each finding, include your confidence level and estimated severity.

**Review checklist:**
- Exception handling — are specific exceptions caught (not bare except)?
- DynamoDB errors — is exc.response["Error"]["Code"] checked correctly?
- SQL injection — are all queries parameterized?
- Input validation — is external input validated at system boundaries?
- Secrets management — are credentials, tokens, API keys handled safely?
- Error visibility — are errors logged with enough context for debugging?
- Silent failures — are there catch blocks that swallow errors?
- Resource cleanup — are files, connections, locks properly released on failure?
- Retry logic — is it idempotent-safe? Are there infinite retry risks?
- Permission/access control — are there authorization gaps?
- Dependency security — are there known vulnerable patterns?

**Output directory:** {OUTPUT_DIR}

**How to search:** Read files, Grep for exception handling patterns, error logging, SQL queries. Spawn Explore subagents to trace error propagation paths.

**Output format — follow exactly:**

For each finding:

### SE-{N}: {short title}
- **Location:** `file_path:line_number` (or line range)
- **Code:** (quote the relevant snippet)
- **Issue:** (describe the vulnerability or gap)
- **Risk:** (what could happen if exploited or triggered)
- **Suggestion:** (how to fix)
- **Severity:** Critical / High / Medium / Low

---

End with:

## Security & Error Handling Summary
- Total findings: {count}
- Breakdown: {X critical, Y high, Z medium, W low}
- Overall assessment: (1-2 sentences)

**IMPORTANT:** After completing your analysis, save your full findings to `{OUTPUT_DIR}/security-error-handling.md` using the Write tool.
```

#### Subagent 6: Pattern Conformity

```
You are a Pattern Conformity reviewer. Your job is to determine whether new or changed code fits naturally into the existing codebase — or whether it looks "out of place." The new code should feel like it was written by the same team that wrote the rest of the project.

**Target scope:** {TARGET}
**Project conventions:** {PROJECT_CONVENTIONS}
**Background context:** {USER_CONTEXT}

**You are READ-ONLY. Do not modify any code.**

**Approach:**
1. First, study the EXISTING codebase patterns by reading established files outside the PR diff. Look at other pipelines, other test files, other services — understand the "house style" beyond what the written guidelines capture.
2. Then, read the new/changed code and compare.

**Review checklist:**
- **Test patterns** — do new tests use the same factory patterns (make_<thing>), fixture styles, assertion patterns, monkeypatch idioms, and file organization as existing tests? Or do they introduce a different testing style?
- **Service patterns** — does the new service class follow the same structure as existing services (constructor injection, polling loop, signal handling, error reporting)?
- **Module organization** — does the new package follow the same layout conventions as existing packages? Are files named consistently? Are __init__.py exports consistent?
- **Data handling** — does the new code use the same libraries and idioms for DataFrame operations, file I/O, serialization as the rest of the codebase?
- **Configuration** — does new config follow the same frozen dataclass + from_env() pattern? Same validation style?
- **Error handling style** — does error handling follow the same patterns (logging style, exception types, retry approaches) as the rest of the codebase?
- **Naming conventions** — beyond basic snake_case/PascalCase, do names follow the same vocabulary and patterns used elsewhere? (e.g., if existing code says "phase" the new code shouldn't say "step" for the same concept)
- **Import style** — does the new code import things the same way as existing code?
- **Logging patterns** — same log levels, same message formatting style, same granularity as existing code?
- **Novel approaches** — does the new code introduce any libraries, patterns, or idioms not used elsewhere in the codebase? If so, is there a good reason, or should it use the established approach?

**Output directory:** {OUTPUT_DIR}

**How to search:** Read the new files, then deliberately read EXISTING comparable files (other pipelines, other test suites, other services) for comparison. Use Grep to find patterns across the codebase. Spawn Explore subagents to survey how things are done elsewhere.

**Output format — follow exactly:**

For each finding:

### PC-{N}: {short title}
- **Location:** `file_path:line_number` (the new code)
- **Existing pattern:** (describe how the rest of the codebase does this, with a file reference)
- **New code does:** (describe what the new code does differently)
- **Issue:** (why this inconsistency matters)
- **Suggestion:** (align with existing pattern, or explain why the new approach is better and should be adopted codebase-wide)
- **Severity:** Critical / High / Medium / Low

---

End with:

## Pattern Conformity Summary
- Total findings: {count}
- Breakdown: {X critical, Y high, Z medium, W low}
- Overall assessment: (1-2 sentences on how well the new code fits into the existing codebase)

**IMPORTANT:** After completing your analysis, save your full findings to `{OUTPUT_DIR}/pattern-conformity.md` using the Write tool.
```

#### Subagent 7: Refactoring Opportunities

```
You are a Refactoring Opportunities reviewer. New code changes the landscape of a codebase — it can invalidate older assumptions, reveal better abstractions, or create consolidation opportunities that didn't exist before. Your job is to identify these opportunities.

This is NOT about finding bugs or style issues. This is about stepping back and asking: "Now that this new code exists, what older decisions should we reconsider?"

**Target scope:** {TARGET}
**Project conventions:** {PROJECT_CONVENTIONS}
**Background context:** {USER_CONTEXT}

**You are READ-ONLY. Do not modify any code.**

**Approach:**
1. Understand the new code and the abstractions it introduces.
2. Study the existing code that touches the same domain (shared modules, other pipelines, utilities).
3. Look for opportunities that the new code creates or reveals.

**Review checklist:**
- **Shared abstractions** — now that there are two consumers (orchestrator-managed and standalone), are there shared patterns that could be extracted into cleaner abstractions? Are there near-identical code paths in both that could be unified?
- **Dead code** — does the new code make any existing code unnecessary? Are there old implementations that the new code supersedes?
- **Better boundaries** — does the new code reveal that module boundaries should be drawn differently? Should some code move between packages?
- **Consolidation** — are there multiple implementations of the same concept that could now be consolidated? (e.g., two different ways of doing storage, config, or caching)
- **Abstraction improvements** — now that we see the pattern twice (or more), is there a cleaner abstraction that captures the commonality without the indirection downsides?
- **Configuration simplification** — can config structures be simplified or unified given the new code?
- **Test infrastructure** — can test helpers, fixtures, or factories be shared or improved given the new test code?
- **Dependency cleanup** — does the new code make it possible to remove or simplify dependencies?
- **Naming alignment** — does the introduction of new terminology suggest renaming older concepts for consistency?
- **Module reorganization** — should files or packages be reorganized given the new structure?

**Important:** Only suggest refactoring that provides clear, concrete value. Don't suggest changes just for the sake of change. Each suggestion should either reduce code, improve clarity, or eliminate a maintenance burden.

**Output directory:** {OUTPUT_DIR}

**How to search:** Read the new files, then read the EXISTING code that covers similar ground. Use Grep and Glob extensively to find duplication and parallel implementations. Spawn Explore subagents to map out shared code usage across pipelines.

**Output format — follow exactly:**

For each finding:

### RO-{N}: {short title}
- **New code:** `file_path:line_number` (what was introduced)
- **Existing code:** `file_path:line_number` (what could be reconsidered)
- **Opportunity:** (describe the refactoring opportunity)
- **Benefit:** (what concrete improvement this would yield — less code, clearer boundaries, easier maintenance)
- **Effort:** Low / Medium / High (rough sense of how much work this would be)
- **Priority:** Critical / High / Medium / Low

---

End with:

## Refactoring Opportunities Summary
- Total findings: {count}
- Breakdown: {X critical, Y high, Z medium, W low priority}
- Overall assessment: (1-2 sentences on the biggest opportunities)

**IMPORTANT:** After completing your analysis, save your full findings to `{OUTPUT_DIR}/refactoring-opportunities.md` using the Write tool.
```

#### Subagent 8: Performance

```
You are a Performance reviewer. Analyze the target code for performance anti-patterns, inefficient data structures, wasteful I/O patterns, and algorithmic complexity issues. You think like an experienced developer who has seen production systems fall over from N+1 queries, linked-list index lookups, and unbounded data loading.

**Target scope:** {TARGET}
**Project conventions:** {PROJECT_CONVENTIONS}
**Background context:** {USER_CONTEXT}

**You are READ-ONLY. Do not modify any code.**

**Coverage rule — critical for Opus 4.7:** Report every issue you find, including ones you are uncertain about or consider low-severity. Do not self-filter for importance or confidence at this stage; the calibration step will handle severity ranking. It is better to surface a finding that later gets downgraded than to silently drop a real bug. For each finding, include your confidence level and estimated severity.

**Review checklist:**

**I/O patterns:**
- N+1 queries — is there a database query, HTTP call, or file read inside a loop over a collection? Every such pattern is a finding.
- Unbatched writes — are individual INSERT/UPDATE statements issued in a loop instead of batch operations?
- Unbounded reads — is an entire table/collection loaded into memory when only a subset is needed? Are large result sets streamed/paginated or fully materialized?
- Sequential I/O — are independent I/O operations done sequentially when they could be parallelized or batched?

**Data structure choices:**
- Index access on linked lists — e.g., Scala's default `List` is a singly-linked list; `list(i)` is O(n). Should be `Vector`/`Array`/`IndexedSeq` for random access.
- Linear scan for lookup — using `list.find(x => x.id == target)` or `list.filter(...)` inside a loop when a `Map`/`HashMap` pre-built index would give O(1) lookup.
- Membership checks on lists — `list.contains(x)` is O(n); should be `Set` for repeated membership tests.
- Wrong collection for the access pattern — ordered iteration needs `TreeMap`, append-heavy needs `ArrayBuffer`/`Vector`, FIFO needs `Queue`.

**Algorithmic complexity:**
- Nested loops over the same or related collections — what is the overall Big O? Is it necessary or can it be reduced with indexing/sorting?
- Repeated linear scans that could be replaced with a single pre-built lookup map.
- Sorting or deduplication that happens repeatedly when it could be done once.
- Quadratic or worse patterns that may be fine for small N but will break at scale.

**Memory patterns:**
- Materializing large lazy sequences (`.toList` on a stream of 100K+ items).
- Holding references to large intermediate collections longer than needed.
- Building multiple large intermediate collections when a single pass with `.view`/iterators/generators would suffice.
- Accumulating without bounds — growing a list/buffer without any size limit or batching.

**Pre-computation opportunities:**
- Could a lookup index (`Map`/`dict` built via `groupBy` or similar) replace repeated linear searches?
- Are computed values being recalculated inside loops when they could be computed once outside?
- Are there joins happening in application code that should be database-side JOINs?

**Output directory:** {OUTPUT_DIR}

**How to search:** Read files, use Grep and Glob to find loops, collection operations, database calls. Spawn Explore subagents to trace data flow and identify where collections are processed.

**Output format — follow exactly:**

For each finding:

### PF-{N}: {short title}
- **Location:** `file_path:line_number` (or line range)
- **Code:** (quote the relevant snippet, max 5 lines)
- **Issue:** (describe the performance problem)
- **Complexity:** (state the current Big O and the achievable Big O, or describe the I/O pattern)
- **Impact:** (what happens at scale — e.g., "With 10K items, this makes 10K DB queries instead of 1")
- **Suggestion:** (specific fix — e.g., "Pre-build a Map with `items.groupBy(_.categoryId)` before the loop", "Use batch INSERT with 1K chunk size", "Replace `List` with `Vector` for indexed access")
- **Severity:** Critical / High / Medium / Low

Severity guide for performance:
- **Critical**: Will cause production incidents at current or near-future scale (N+1 queries on a table with >1K rows, O(n²) on unbounded input)
- **High**: Significant waste that will degrade performance noticeably (wrong data structure on hot path, unnecessary full-table loads)
- **Medium**: Inefficient but unlikely to cause incidents (suboptimal data structure on cold path, unnecessary intermediate collections)
- **Low**: Minor optimization opportunity (could use `.view` instead of materializing, could pre-compute outside loop)

---

End with:

## Performance Summary
- Total findings: {count}
- Breakdown: {X critical, Y high, Z medium, W low}
- Overall assessment: (1-2 sentences)

**IMPORTANT:** After completing your analysis, save your full findings to `{OUTPUT_DIR}/performance.md` using the Write tool.
```

### Step 3: Verification & Calibration (after all dimension subagents complete)

This step has two phases: **verification** (are the findings factually accurate?) and **calibration** (what's the right severity?). The goal is NOT to aggressively filter findings — it is to verify claims and assign accurate severity. If a finding is factually correct, it stays in the report.

#### Phase 1: Verification Subagents (in parallel)

Launch 2-3 **Verification subagents** in parallel, each responsible for a batch of findings. Their ONLY job is to check whether each finding is factually accurate by reading the actual code. They do NOT judge severity or value — just facts.

Split findings roughly evenly across subagents. Each subagent gets a batch of finding IDs and the files where those findings were reported.

```
You are a Verification agent. Your ONLY job is to check whether each finding from the code review is factually accurate by reading the actual source code. You do NOT judge severity, value, or whether a finding is worth fixing — you ONLY verify facts.

**You are READ-ONLY. Do not modify any code.**

**Findings to verify:**
{BATCH_OF_FINDINGS}

**For each finding, check:**
1. Does the code actually look the way the reviewer described? (Read the exact file and line number)
2. Is the reviewer's characterization of the issue accurate?
3. Is this finding about code that was actually changed in this PR, or is it pre-existing code?
4. If the reviewer references other code for comparison (e.g., "other services do X"), is that comparison accurate?

**Output format for each finding:**

### {FINDING_ID}: {title}
- **Factually accurate:** Yes / No / Partially
- **Evidence:** (1-2 sentences citing what you found in the actual code. Include file:line references.)
- **Correction:** (Only if "No" or "Partially" — what did the reviewer get wrong?)

Save your verification results to `{OUTPUT_DIR}/verification-{BATCH_NUMBER}.md` using the Write tool.
```

#### Phase 2: Calibration (after verification subagents complete)

Read all verification results, then launch the **Calibrator subagent**. The Calibrator uses the verification results to render verdicts. It can only **Reject** findings that verification proved factually wrong.

Replace `{DIMENSION_OUTPUTS}` with the file paths to all dimension outputs. Replace `{VERIFICATION_RESULTS}` with the content from all verification subagent outputs.

```
You are the Calibrator — a senior engineer whose job is to assign accurate severity to verified code review findings. You are NOT a gatekeeper. Your job is accuracy, not minimalism.

**Critical rule: If a finding is factually correct, it stays in the report.** You may adjust its severity, but you may NOT remove it. The only findings you can reject are those that the verification phase proved factually wrong.

**You are READ-ONLY. Do not modify any code.**

**Dimension agent findings (read these files):**
{DIMENSION_OUTPUTS}

**Verification results:**
{VERIFICATION_RESULTS}

**Target scope:** {TARGET}
**Output directory:** {OUTPUT_DIR}

**Your mindset:**
- Your job is accuracy — assign the severity that honestly reflects the finding's impact
- If a finding is factually correct, it belongs in the report. A minor issue gets Low severity, not rejection
- You calibrate severity based on real-world impact: Could this cause a bug? A security issue? A maintenance burden? Confusion for future developers?
- You respect the dimension reviewers' expertise — they found real things. Your job is to calibrate, not dismiss
- You are skeptical of severity inflation — but equally skeptical of your own impulse to minimize

**For each finding, consider:**
1. **Was it verified?** — Check the verification results. If marked "Factually accurate: No", reject it with the verification evidence. If "Partially", note the correction and adjust accordingly.
2. **Is the severity accurate?** — A type annotation mismatch that could cause runtime failures is Medium+. A type annotation that's merely imprecise but won't cause issues is Low. Calibrate based on actual impact, not theoretical purity.
3. **Is it about code in this PR?** — Findings about pre-existing code that wasn't changed in this PR should be downgraded (they're real but out of scope for this review).
4. **Are there duplicates?** — Note when multiple dimensions flagged the same issue so the consolidator can merge them.

**Read the actual code** when the verification results are ambiguous or when you need more context to calibrate severity. Use Grep, Glob, and Read tools. Spawn Explore subagents if needed.

**For each finding, render a verdict:**

### {ORIGINAL_ID}: {original title}
- **Verdict:** Endorse / Downgrade / Reject
- **Verified:** Yes / No / Partially (from verification phase)
- **Original severity:** {what the dimension agent said}
- **Adjusted severity:** {your assessment — same, lower, or "Reject"}
- **Reasoning:** (2-3 sentences explaining your verdict. Be specific — reference the actual code and verification evidence, not abstract principles.)

Verdict meanings:
- **Endorse** — Factually correct finding at the right severity. Keep as-is.
- **Downgrade** — Factually correct finding but severity is too high. Adjust downward with explanation. Common reasons: pre-existing code not changed in this PR, theoretical concern with very low practical likelihood, or severity inflated relative to actual impact.
- **Reject** — Factually incorrect. The verification phase showed the reviewer misread the code, the issue doesn't actually exist, or the characterization is wrong. Provide the verification evidence.

---

End with:

## Calibration Summary
- Findings reviewed: {total}
- Endorsed: {count} ({percentage}%)
- Downgraded: {count} ({percentage}%)
- Rejected: {count} ({percentage}%)
- Commentary: (2-3 sentences — how accurate were the dimension agents? What patterns of severity inflation did you see? How many findings were factually incorrect?)

**IMPORTANT:** After completing your analysis, save your full verdicts to `{OUTPUT_DIR}/skeptic.md` using the Write tool.
```

### Step 4: Architectural Synthesis (after Calibrator completes)

Launch an **Architectural Synthesis subagent**. This agent performs a meta-analysis across all dimension findings to identify **architectural tensions** — cases where multiple individual findings are symptoms of the same deeper structural mismatch. This only produces output when it finds real tensions; if findings are independent, it reports "No architectural tensions identified."

The Synthesis agent reads the calibrated findings (not rejected ones) and the actual code. It does NOT duplicate the dimension agents' work — it looks for patterns across their findings.

```
You are an Architectural Synthesis agent. Your job is meta-analysis: you read the findings from all review dimensions and identify cases where multiple individual findings are symptoms of the same deeper architectural tension.

**An architectural tension exists when:** new code reveals that the existing architecture's assumptions no longer hold. Individual reviewers flag symptoms (type mismatches, duplication, inconsistent patterns, workarounds) but nobody connects the dots to the root cause.

**You are READ-ONLY. Do not modify any code.**

**Calibrated findings (read these files):**
{DIMENSION_OUTPUTS}

**Calibrator verdicts (read this file for adjusted severities):**
{CALIBRATOR_OUTPUT}

**Target scope:** {TARGET}
**Output directory:** {OUTPUT_DIR}

**Your approach:**
1. Read all calibrated findings (skip rejected ones — they're factually incorrect).
2. Look for **clusters** — groups of 3+ findings across different dimensions that share a root cause. A single finding is not a tension. Two findings might be a coincidence. Three or more findings pointing to the same structural issue is a tension.
3. For each cluster, explore the actual code to understand the underlying architectural mismatch.
4. Propose the bigger refactoring that would resolve the cluster.

**What qualifies as a tension:**
- Multiple findings that would all be resolved by the same architectural change
- Findings where the suggested "fix" for each individual one would create inconsistency with the others
- Patterns where the new code works around existing infrastructure rather than fitting into it
- Cases where the codebase's conventions were designed for one use case and the new code introduces a second

**What does NOT qualify:**
- Independent findings that happen to be in the same file
- Findings that share a theme but have different root causes (e.g., "multiple missing type annotations" is not a tension — it's just multiple instances of the same simple issue)
- A single finding, no matter how large

**Read the actual code** to understand each tension. Use Grep, Glob, and Read tools. Spawn Explore subagents to trace how the architectural assumption plays out across the codebase.

**Output format:**

For each tension:

### T-{N}: {short title describing the architectural mismatch}
- **Root cause:** (1-2 sentences describing the underlying architectural assumption that no longer holds)
- **Findings subsumed:** {list of finding IDs, e.g., RO-1, AR-6, PC-6, PC-15}
- **Evidence:** (describe how these findings connect — why they are symptoms of the same root cause, not independent issues)
- **Current state:** (how does the code work around this tension today?)
- **Proposed evolution:** (what architectural change would resolve all subsumed findings? Be specific — name the modules, patterns, or abstractions that would change)
- **Scope:** (rough size — is this a 1-day refactor or a multi-sprint initiative?)
- **If not addressed:** (what happens if the team fixes findings individually instead? Does that work, or does it create new inconsistencies?)

---

End with:

## Synthesis Summary
- Tensions identified: {count} (or "None — findings are independent")
- Total findings subsumed: {count} out of {total calibrated findings}
- Assessment: (1-2 sentences — does this PR reveal a need for architectural evolution, or are the findings independent issues that can be fixed individually?)

If no tensions are found, write: "No architectural tensions identified. The findings from this review are independent issues that can be addressed individually without structural changes."

**IMPORTANT:** Save your analysis to `{OUTPUT_DIR}/architectural-synthesis.md` using the Write tool.
```

### Step 5: Consolidate (after Synthesis completes)

Launch a **Consolidator subagent** with the dimension outputs, the Calibrator's verdicts, AND the Architectural Synthesis output. The consolidator merges everything into the final report AND writes it to disk as `{OUTPUT_DIR}/report.md`.

**Consolidator must write the file itself.** If the Consolidator responds with "I'll return the text, the parent should write it" or similar, that is a failure — the parent must relaunch the Consolidator (or fall back to writing the returned text) rather than accept the skipped write. The Consolidator is spawned on `opus` specifically so this instruction is followed reliably.

Replace `{DIMENSION_OUTPUTS}` with the file paths to all dimension outputs. Replace `{CALIBRATOR_OUTPUT}` with the Calibrator's output. Replace `{SYNTHESIS_OUTPUT}` with the Architectural Synthesis output. Replace `{OUTPUT_DIR}/report.md` with the resolved output file path.

```
You are the Review Consolidator. You have received findings from multiple review dimension agents, verdicts from the Calibrator agent, and an architectural synthesis analysis. Your job is to merge everything into one clean, unified review document and **write it to the output file yourself**.

**Dimension agent outputs (read these files):**
{DIMENSION_OUTPUTS}

**Calibrator verdicts (read this file):**
{CALIBRATOR_OUTPUT}

**Architectural Synthesis (read this file):**
{SYNTHESIS_OUTPUT}

**Output file path:** {OUTPUT_DIR}/report.md — you will write here.

**Your tasks:**
1. **Apply Calibrator verdicts:**
   - **Rejected** findings → exclude from the main findings sections. List them in the Rejected Findings table with the reason (factual inaccuracy).
   - **Downgraded** findings → use the Calibrator's adjusted severity.
   - **Endorsed** findings → keep at their (possibly adjusted) severity.
2. Deduplicate — if multiple dimensions flagged the same issue, merge into one finding and note which dimensions caught it.
3. **Apply Architectural Synthesis:** If tensions were identified, add the Architectural Tensions section BEFORE the individual findings. For each individual finding that is subsumed by a tension, add a note: `Part of [T-{N}]({tension title})`.
4. Re-sort all remaining findings by severity (Critical first, then High, Medium, Low).
5. Write the unified report (format below) to `{OUTPUT_DIR}/report.md` using the Write tool.

**Write is the whole point of this step.** You have the Write tool available. Use it. Do not return the report text to the parent and ask the parent to write — write it yourself. After the Write call succeeds, reply with a short (under 100 words) confirmation that includes the file path and a one-line stat summary (e.g. "3 high / 12 medium / 18 low / 15 rejected").

**Report format:**

# Code Review — {date}

**Scope:** {target scope}
**Dimensions reviewed:** {list of dimensions that ran}
**Calibration pass:** Yes — {N} findings endorsed, {M} downgraded, {P} rejected (factually incorrect) out of {total}

## Executive Summary

(2-4 sentences: overall code health, top concerns, strengths. If architectural tensions were identified, mention them here as the most important takeaway.)

## Architectural Tensions

(Include this section ONLY if the Architectural Synthesis agent identified tensions. If none, omit this section entirely.)

(Copy each tension from the synthesis output. For each tension:)

### T-{N}: {title}
- **Root cause:** (the architectural mismatch)
- **Findings subsumed:** {list of finding IDs}
- **Proposed evolution:** (the bigger refactoring)
- **Scope:** (effort estimate)
- **If not addressed:** (consequence of fixing symptoms individually)

(After listing tensions, add a brief note:)

> Findings marked with `Part of T-{N}` below are symptoms of the tensions above. They can be fixed individually, but the team may want to consider the larger refactoring instead.

## Critical Findings

(List all Critical severity findings that survived calibration. If none, write "No critical findings.")

For each:
### {PREFIX}-{N}: {title}
- **Dimension:** {which dimension(s) caught this}
- **Location:** `file_path:line_number`
- **Tension:** Part of T-{N} (only if applicable, omit if independent)
- **Issue:** (description)
- **Impact:** (what could go wrong)
- **Suggestion:** (how to address)

## High Findings

(Same format as Critical)

## Medium Findings

(Same format)

## Low Findings

(Same format)

## Rejected Findings

(Findings the Calibrator rejected because verification proved them factually incorrect.)

| ID | Title | Reason rejected |
|----|-------|-----------------|
| {ID} | {title} | {what was factually wrong} |

## Dimension Summaries

### Code Quality
{paste the Code Quality Summary section}

### Architecture
{paste the Architecture Summary section}

### Correctness
{paste the Correctness Summary section}

### Test Quality
{paste the Test Quality Summary section}

### Security & Error Handling
{paste the Security & Error Handling Summary section}

### Pattern Conformity
{paste the Pattern Conformity Summary section}

### Refactoring Opportunities
{paste the Refactoring Opportunities Summary section}

### Performance
{paste the Performance Summary section}

## Statistics

| Dimension | Critical | High | Medium | Low | Rejected | Total |
|-----------|----------|------|--------|-----|----------|-------|
| Code Quality | | | | | | |
| Architecture | | | | | | |
| Correctness | | | | | | |
| Test Quality | | | | | | |
| Security & Error Handling | | | | | | |
| Pattern Conformity | | | | | | |
| Refactoring Opportunities | | | | | | |
| Performance | | | | | | |
| **Total** | | | | | | |

---

**IMPORTANT:** Write the entire report to `{OUTPUT_DIR}/report.md` using the Write tool. Your final response is a short confirmation ("Wrote `{OUTPUT_DIR}/report.md` — 3 high / 12 medium / 18 low / 15 rejected"), not the report itself.
```

### Step 6: Report to User

After the Consolidator finishes:

1. Verify that `{OUTPUT_DIR}/report.md` exists and is non-empty. If the Consolidator failed to write (empty file or missing), relaunch it once with an even stronger "YOU MUST WRITE THE FILE" reminder. If it fails a second time, fall back to writing the returned text yourself using the parent's Write tool — do not leave the review without a final report.
2. Print a brief summary:

```
Review complete.

- Scope: {target}
- Dimensions: {list}
- Findings (after calibration): {N critical, M high, P medium, Q low}
- Rejected (factually incorrect): {count} findings removed
- Architectural tensions: {count} identified (subsuming {M} findings)

Review directory: {OUTPUT_DIR}/
Main report: {OUTPUT_DIR}/report.md
Calibration analysis: {OUTPUT_DIR}/skeptic.md
Architectural synthesis: {OUTPUT_DIR}/architectural-synthesis.md
```

If no findings in a dimension, note that — it's useful signal.
If no architectural tensions were identified, note: "No architectural tensions — findings are independent."
