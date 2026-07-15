# Phase 2 — Analyze

Launch **4 parallel dimension agents** (mid tier — Terra-class — with `reasoning_effort: high`) in a **single message** so they run concurrently. Each agent owns **two related dimensions** that share a detection strategy — one context holding both checklists classifies overlapping findings better than two agents flagging them separately, and it halves the read amplification.

| Agent | Dimensions | Shared detection strategy | Output file |
|-------|-----------|---------------------------|-------------|
| A — Duplication & Types | DU + TC | Find similar shapes (logic or type), judge intentionality | `findings/duplication-types.md` |
| B — Dead & Legacy | DC + LF | Trace callers; judge whether code should exist | `findings/dead-legacy.md` |
| C — Types & Structure | WT + CD | Tool-seeded structural checks (type-checker / dep-graph) + verification | `findings/types-structure.md` |
| D — Guards & Comments | DF + CS | Removal-biased Chesterton's-Fence judgment | `findings/guards-comments.md` |

Each agent:

- Receives the target scope, detected languages, tool outputs (if any), project conventions, and the known `cleanup-sweep-skip` marker list
- Has two primary dimensions but is explicitly permitted to flag cross-dimension findings (breadth over precision — Calibrator dedupes in Phase 3)
- Writes findings to its output file above

For repos above the Phase 1 sharding threshold, use the **area-sharded variant** instead — see the end of this file.

## Common Preamble (all agents)

Every agent prompt starts with this preamble. Substitute `{TARGET}`, `{LANGUAGES}`, `{TOOL_OUTPUT_DIR}`, `{PROJECT_CONVENTIONS}`, `{SKIP_MARKERS}`, `{OUTPUT_DIR}`, `{OUTPUT_FILE}` from Phase 1's `scope.md`.

```
You are a sweep dimension agent. Your job is to find specific categories of cruft in the target codebase and write high-quality findings the Calibrator can dedupe and assign blast radius to.

**Target scope:** {TARGET}
**Languages present (primary → secondary):** {LANGUAGES}
**Tool output directory:** {TOOL_OUTPUT_DIR} (pre-run static-analysis output, if any — read and reconcile with your own findings)
**Project conventions:** {PROJECT_CONVENTIONS}
**Existing cleanup-sweep-skip markers:** {SKIP_MARKERS} — EXCLUDE these regions from your findings entirely.
**Output file:** {OUTPUT_FILE}

**You may modify NO source code.** You produce a findings file only.

**Breadth over precision:** If you notice findings in dimensions outside your two primaries, flag them anyway with the appropriate prefix (see Finding ID Prefixes below). The Calibrator will dedupe cross-agent overlap.

**Finding ID Prefixes:**
- DU = Duplication
- TC = Type Consolidation
- DC = Dead Code
- CD = Circular Dependency
- WT = Weak Type
- DF = Defensive Code
- LF = Legacy / Fallback
- CS = Comment / Slop

**Output format — each finding, use exactly this format:**

### {PREFIX}-{N}: {short title}
- **Location:** `file_path:line_number` (or range `file_path:start-end`)
- **Code:** (quote the minimal relevant snippet, max 10 lines; use fenced code block with language tag)
- **Issue:** (what's wrong — be precise, cite the anti-pattern)
- **Proposed fix:** (concrete — what should replace the current code, or "delete")
- **Confidence:** High / Medium / Low (your self-assessment of whether the proposed fix is correct)
- **Blast radius hint:** your guess at blast radius (Calibrator re-judges) — cite: files affected, control flow impact, externally visible behavior changes, reversibility

End your file with:

## Summary
- Total findings: {count} (per prefix: DU=…, TC=…, …)
- Breakdown: {H confidence, M confidence, L confidence}
- Tools used: {list, or "LLM-only"}
- Overall assessment: (1-2 sentences)

**IMPORTANT:** Save your findings to {OUTPUT_FILE} by writing the file directly. Do not write to any other location.

Read files and run searches in parallel when independent. You may spawn up to 3 explorer subagents to trace cross-file usage; explorers run mid tier at `reasoning_effort: medium`.
```

---

## Agent A — Duplication & Type Consolidation (DU + TC)

```
{COMMON PREAMBLE}

**Primary dimension 1 — Duplication (DU):** repeated *logic/behavior* across functions, modules, or packages that should be consolidated into a single canonical implementation.

DU — what you look for:
- Multiple functions that implement the same behavior with minor variations (consolidate or parameterize)
- Copy-paste code blocks 10+ lines long appearing in 2+ places
- Parallel implementations of the same concept across modules (e.g., two different cache-warming routines)
- Utility functions reimplemented locally when a shared utility exists
- "Near-identical" code paths where the difference is a parameter that should be extracted
- Boilerplate blocks that appear in every X (service constructor, handler setup, etc.) and could become a base pattern

DU — what you do NOT consider duplication:
- Small duplication (< 5 lines) where DRY-ing would add indirection (Sandi Metz: "duplication is far cheaper than the wrong abstraction")
- Test setup/factory duplication (test code is allowed to repeat setup for clarity)

**Primary dimension 2 — Type Consolidation (TC):** repeated *type shapes* (struct/interface/class definitions) that should be unified into a single shared type.

TC — what you look for:
- Two or more dataclasses / TypedDicts / interfaces / structs with identical or near-identical fields that represent the same concept
- Anonymous object/dict shapes that should be a named type (Python dict literals being passed around, TS object literals with repeated shape)
- Types that differ only in one nullable field — those should be a single type with optional field, not two types
- Enum equivalents duplicated across modules (two Literal['a', 'b', 'c'] that should be one Enum/type alias)
- Domain concepts expressed as raw primitives in some places and wrapped types in others (inconsistent modeling)

TC — what you do NOT consider:
- Intentional type divergence (e.g., DTO vs domain entity deliberately differ) — the question is whether the divergence is intentional or accidental
- Weak type uses (`any`, `unknown`, `Any`) — flag with WT prefix, don't develop fully

**Language-specific notes:**
- Python: duplicated `@classmethod` factories, repeated context-manager patterns, parallel `try/except` structures; `TypedDict`, `dataclass`, `pydantic.BaseModel`, `NamedTuple`, protocols
- TypeScript: duplicated reducer/selector patterns, repeated hook logic, similar service classes; `interface`, `type`, object literal shapes
- Scala/Rust: typeclass/trait implementations that repeat core behavior with minor tweaks; `struct`/`enum`/`case class` field duplication
- Go: `struct` field duplication
- Any language: duplicated request/response transformation pipelines

**Your workflow:**
1. Read project conventions and any existing shared-utility and shared-types modules
2. Use Grep/Glob to find candidate repeated patterns (function signature patterns, distinctive string literals, common block shapes, type-definition markers)
3. Cluster type definitions by field overlap (names + types); for clusters with ≥80% overlap, read both and judge consolidation
4. For each behavioral candidate, read all occurrences and judge: true duplication, or legitimate local variation?
5. Write findings with the canonical location/type proposal (e.g., "extract to `src/utils/retry.py` which already has similar logic"; canonical type with field list)
```

---

## Agent B — Dead Code & Legacy/Fallback (DC + LF)

```
{COMMON PREAMBLE}

Both of your dimensions answer one question — "should this code exist?" — at two points on a spectrum: DC is code with **zero references**; LF is code that is **referenced but superseded**. Trace callers once, classify accordingly.

**Primary dimension 1 — Dead Code (DC):** unreachable functions, unused exports, orphaned files, never-imported modules.

**Tool seed evidence (read if present):** {TOOL_OUTPUT_DIR}/vulture.txt, ruff.txt (Python F401/F841), knip.txt, ts-prune.txt (TS), cargo-udeps.txt (Rust), deadcode.txt, staticcheck.txt (Go)

DC — what you look for:
- Unused imports (but: Python `__init__.py` re-exports are NOT dead)
- Unused local variables
- Functions/methods with no callers (check dynamic dispatch, reflection, CLI command registration, decorators)
- Unused exported symbols
- Files that are never imported
- Unused dependencies in `package.json` / `pyproject.toml` / `Cargo.toml`

DC — critical verification rules:
- Tool says unused — verify by grepping the codebase. Tools have false positives from string-based lookups, `getattr`, `eval`, `Reflect.get`, CLI entry points, plugin registrations, `importlib`.
- Python specifically: `__all__`, `pytest` fixtures, `@app.route` decorators, `entry_points` in `setup.cfg`/`pyproject.toml`, `__subclasshook__` — anything reflective
- TypeScript: dynamic imports, DI containers, Next.js page/route files, test files loaded by glob
- When in doubt, lower confidence and note the reflection risk
- Dead *branches* inside live functions: flag as observation, lower confidence

**Primary dimension 2 — Legacy / Fallback (LF):** referenced code that should be removed — superseded implementations, deprecated shims, v1-alongside-v2 patterns.

LF — what you look for:
- Functions/classes named `*_v1`, `*_old`, `*_legacy`, `*_deprecated`, or with comments indicating they're superseded
- Two functions that do the same thing with "old" and "new" implementations, where the new one has full coverage
- Feature flags that have been on for months (code behind an always-on flag should be inlined)
- Migration shims (e.g., "readCompat" / "readLegacy") that were supposed to be temporary
- Code paths that handle data shapes that no longer exist in production
- `@deprecated` annotations where all callers have migrated

LF — critical verification rule: "should be removed" is a judgment call. For each candidate, verify:
1. Is there a current replacement? Identify it by name.
2. Are all callers on the new version? List remaining old-version callers.
3. Is there external API stability that forbids removal? Check for public-API markers.

If any caller is still on the old version, your finding is: "migrate remaining callers, then remove" — two-step, not a direct removal.

**Your workflow:**
1. Read all tool output files listed above
2. Grep for legacy markers (`legacy`, `deprecated`, `_v1`, `_old`, `TODO: remove`, `XXX`, `HACK`)
3. For each candidate (tool-flagged or marker-flagged), trace callers across the full codebase (including string literals, test files, config files); classify DC (zero refs) vs LF (superseded refs)
4. Add LLM-only findings for dynamic/reflective cases the tools miss; low confidence on symbols plausibly accessed reflectively
5. For feature-flag-wrapped code, check the flag's status (config or code)

Blast radius varies — an unused import is LOW, an API removal with external callers is HIGH.
```

---

## Agent C — Weak Types & Circular Dependencies (WT + CD)

```
{COMMON PREAMBLE}

Both of your dimensions are structural checks seeded by static-analysis output — type-checker findings and dependency graphs — verified and enriched by reading the code.

**Primary dimension 1 — Weak Types (WT):** use of weak/loose types that erode static guarantees — `any`, `unknown`, `Any`, `object`, untyped kwargs, wide casts.

**Tool seed evidence (read if present):** {TOOL_OUTPUT_DIR}/mypy.txt, tsc-strict.txt, pyright.txt, clippy.txt

WT — what you look for:

Python:
- `Any` in function signatures (propose narrower)
- Untyped `*args`/`**kwargs` where concrete shape is known
- `Dict[str, Any]` that should be a TypedDict/dataclass
- Bare `dict`, `list`, `tuple` without generics
- `cast(X, y)` where a Protocol could avoid the cast
- `# type: ignore` without a reason comment

TypeScript:
- `any`, `as any`, `<any>` (propose specific)
- `unknown` that's never narrowed (should be narrowed at boundary)
- `Object` / `{}` as a type; `Function` as a type (should be callable signature)
- Widening casts (`as string` when the value is `string | number`)

Rust:
- `Box<dyn Any>` / `dyn Any` usage; excessive `Box<dyn Trait>` where generics would work
- `unwrap()` / `expect()` that hides the error type

Scala:
- `Any`, `AnyRef`, `AnyVal` in signatures; `asInstanceOf[X]` (unchecked cast)

WT — research requirement: for each weak type, work out what the concrete type should be:
1. Read the code around the weak type — what actually flows through?
2. Read upstream producers and downstream consumers to infer the shape
3. Check related packages/SDKs for documented types (e.g., if `any` holds an AWS SDK response, the SDK has types)
4. If the concrete type requires a new type definition, note it (and flag as TC-candidate too)

WT — deprioritize: weak types whose narrowing requires runtime validation (external JSON boundary) — flag lower priority with note.

**Primary dimension 2 — Circular Dependencies (CD):** import/dependency cycles between modules, packages, or components.

**Tool seed evidence (read if present):** {TOOL_OUTPUT_DIR}/madge.txt, dependency-cruiser.txt (TS/JS), pycycle.txt, pydeps.txt (Python)

CD — what you look for:
- Direct cycles: A imports B, B imports A
- Transitive cycles: A → B → C → A
- Package-level cycles: package X imports from package Y, Y imports from X
- Delayed-import workarounds: `import` statements inside functions that exist solely to break an import cycle (flag these — the cycle is real, just hidden)
- TYPE_CHECKING-gated imports that only exist to break cycles (flag the underlying cycle)

CD — critical nuances:
- Type-level-only cycles (imported only in annotations) are still findings but lower priority
- Intentional cycles exist in some frameworks (Django model relationships) — flag and note the framework convention
- Propose a concrete untangling: extract shared types to a neutral module, invert dependency direction, introduce an interface

**Your workflow:**
1. Read tool outputs; cross-reference with project structure
2. For each weak type, do the WT research steps; for each cycle, read both ends and identify the *minimal* coupling (often one symbol)
3. Propose fixes: narrowed types with source of truth; cycle breaks via (a) extract coupling point to neutral module, (b) dependency inversion, or (c) duplicate the single symbol
```

---

## Agent D — Defensive Code & Comment Slop (DF + CS)

```
{COMMON PREAMBLE}

Both of your dimensions are removal-biased and governed by Chesterton's Fence: before flagging anything, articulate why it's safe to remove. When in doubt, don't flag — or flag with LOW confidence and a note.

**Primary dimension 1 — Defensive Code (DF):** defensive programming constructs that do not serve a specific, articulable purpose.

DF — what you look for:
- `try/except Exception` / `try/catch (e)` that logs and swallows, where propagation would be correct
- Nested try/except in a single function where inner and outer do nearly the same thing
- Null-guards in code paths where the value is provably non-null from the caller
- `if x is None: return None` early-returns where the type annotation already says `Optional`
- Bare `except:` or `except BaseException:` (almost always wrong)
- Wrapping code in try/except solely to add logging, then re-raising (use logging at the handler site instead)
- Go: `if err != nil { return nil }` that silently swallows errors
- Scala: `.getOrElse(...)` / `.recover { case _ => }` that hides real errors
- TS: `?.` chaining that hides a real "this should exist" invariant
- Defensive type checks (`isinstance(x, int)` at the start of a function with typed signature)

DF — what counts as "serving a purpose" (leave these alone):
- Handling unsanitized external input (API boundary, CLI input, network parse)
- Catching a specific exception type to convert it (e.g., `JSONDecodeError → InvalidRequestError`)
- Catching at the top-level of a long-running loop to keep processing next item
- Retry logic with explicit backoff
- Resource cleanup (`finally` blocks) — **never** flag these

DF — critical rule: you are evaluating whether each catch/guard has a *reason*. Absence of a reason = finding. Presence of a clear reason (even implicit) = leave it. For each finding, include in the "Issue" field:
- **What this catches / guards against** (describe the defensive stance)
- **Why it is unnecessary** (the specific reason — "the only exception type this can throw is already handled upstream", "the type system already guarantees non-null", etc.)

DF blast radius is almost always HIGH (removing control-flow constructs alters failure behavior). Self-assess HIGH and let the Calibrator confirm.

**Primary dimension 2 — Comment / Slop (CS):** comments that should be removed or replaced.

CS — what you look for:
- Obvious-statement comments: `# increment the counter` above `counter += 1`
- In-motion narration: comments describing work-in-progress, migrations, or "replaces X" references
- AI-assistant slop: "Enhanced function to...", "Added a robust check for..." — restates the code or narrates the AI's work
- Commented-out code blocks (should be deleted; git has history)
- Stale TODOs older than 6 months without context
- Redundant docstrings that restate the function name ("fetches the user" above `def fetch_user`)
- Section banners that add no info; divider comments between functions

CS — what you KEEP (or propose improving rather than deleting):
- Comments explaining *why* (business logic rationale, constraints, workarounds)
- Comments warning about non-obvious gotchas ("this must run before X, else Y")
- Docstrings with parameter/return info, examples, or behavioral contracts
- Licensing headers, attribution
- Module-level explanations of purpose when non-obvious
- Links to tickets/RFCs that explain a decision

CS — judgment rubric: "Would a new developer reading this file understand the code better with this comment, or without it?" If without — remove. If better with — keep. For slop comments that describe work done, replace with a useful why-comment if there's a useful why to articulate; otherwise delete.

CS — never flag:
- `cleanup-sweep-skip` markers (skill metadata)
- Type-checking or linter ignore comments with rationales

CS blast radius is almost always LOW (comments don't affect runtime behavior). Self-assess LOW and let the Calibrator confirm.
```

---

## Launching the 4 Agents

Use subagents on the mid-tier model (Terra-class) with `reasoning_effort: "high"` for each. Launch all 4 in one parallel batch:

```
spawn_agent(agent_type="default", model="<mid-tier>", reasoning_effort="high", message="<Agent A prompt with substitutions>")
spawn_agent(agent_type="default", model="<mid-tier>", reasoning_effort="high", message="<Agent B prompt>")
spawn_agent(agent_type="default", model="<mid-tier>", reasoning_effort="high", message="<Agent C prompt>")
spawn_agent(agent_type="default", model="<mid-tier>", reasoning_effort="high", message="<Agent D prompt>")
```

While agents run, the main thread:
- Updates `status.md` to `Phase: analyze, Step: awaiting-dimension-agents`
- Does not duplicate work (no parallel main-thread grep for findings)

## Area-Sharded Variant (large repos)

When Phase 1 chose area-sharding (scope > ~50k LoC):

1. Partition the scope into N directory subtrees of roughly comparable LoC (N chosen so each shard is a comfortable single-agent read; typically 4–8).
2. Launch one agent per area, same tier/effort, whose prompt is the Common Preamble plus **all eight dimension checklists** from Agents A–D above, scoped to its subtree. Output file: `findings/area-<slug>.md`, using the standard prefixes.
3. Add to each area agent's prompt: *"Cross-file duplication or cycles that cross your area boundary: flag what you can see and mark 'possible cross-area' — the Calibrator has whole-scope visibility."*
4. The Calibrator (Phase 3) additionally merges cross-area findings.

Trade-off, for the record: area-sharding reads the codebase once instead of 4×, at the cost of weaker cross-area duplication detection. That's why it's reserved for large repos where 4× reads dominate cost.

## Post-Analysis Consolidation

After all agents complete:

1. Verify each agent produced its findings file. If any is missing or clearly inadequate, retry once with a more specific prompt addressing what went wrong. If the second attempt fails, note in `status.md` and proceed with the others (note the gap in the final report).

2. Count total findings per dimension prefix. Update `status.md`:

```markdown
- Phase: analyze-complete
- Step: ready-to-calibrate
- Findings per dimension: DU=X, TC=Y, DC=Z, CD=A, WT=B, DF=C, LF=D, CS=E
- Total raw findings: (sum)
- Next action: launch Calibrator agent
```

3. Announce: *"Phase 2 complete. N raw findings across 8 dimensions (4 agents). Entering Phase 3 (Calibrator)."* Read `references/phase-3-calibrate.md` before proceeding.
