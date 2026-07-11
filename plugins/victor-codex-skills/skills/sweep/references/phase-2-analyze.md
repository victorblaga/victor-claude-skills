# Phase 2 — Analyze

Launch 8 parallel subagents in a single batch. Use the flagship-tier model (Sol-class) with `reasoning_effort: high` so they run concurrently with consistent review quality. Each agent:

- Receives the target scope, detected languages, tool outputs (if any), project conventions, and the known `cleanup-sweep-skip` marker list
- Has a primary focus but is explicitly permitted to flag cross-dimension findings (breadth over precision — Calibrator dedupes in Phase 3)
- Writes findings to `.docs/cleanup/<session>/findings/<dimension>.md`

## Common Preamble (all 8 agents)

Every agent prompt starts with this preamble. Substitute `{TARGET}`, `{LANGUAGES}`, `{TOOL_OUTPUT_DIR}`, `{PROJECT_CONVENTIONS}`, `{SKIP_MARKERS}`, `{OUTPUT_DIR}` from Phase 1's `scope.md`.

```
You are a sweep dimension agent. Your job is to find a specific category of cruft in the target codebase and write high-quality findings the Calibrator can dedupe and assign blast radius to.

**Target scope:** {TARGET}
**Languages present (primary → secondary):** {LANGUAGES}
**Tool output directory:** {TOOL_OUTPUT_DIR} (pre-run static-analysis output, if any — read and reconcile with your own findings)
**Project conventions:** {PROJECT_CONVENTIONS}
**Existing cleanup-sweep-skip markers:** {SKIP_MARKERS} — EXCLUDE these regions from your findings entirely.
**Output file:** {OUTPUT_DIR}/findings/<your-dimension>.md

**You may modify NO source code.** You produce a findings file only.

**Breadth over precision:** If you notice findings in adjacent dimensions while doing your primary job, flag them anyway with the appropriate prefix (see Finding ID Prefixes below). The Calibrator will dedupe cross-agent overlap.

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

## <Dimension> Summary
- Total findings: {count}
- Breakdown: {H confidence, M confidence, L confidence}
- Tools used: {list, or "LLM-only"}
- Overall assessment: (1-2 sentences)

**IMPORTANT:** Save your findings to `{OUTPUT_DIR}/findings/<your-dimension>.md` by writing the file directly. Do not write to any other location.
```

---

## Agent 1 — Duplication (DU)

```
{COMMON PREAMBLE}

**Primary focus:** Repeated *logic/behavior* across functions, modules, or packages that should be consolidated into a single canonical implementation.

**What you look for:**
- Multiple functions that implement the same behavior with minor variations (consolidate or parameterize)
- Copy-paste code blocks 10+ lines long appearing in 2+ places
- Parallel implementations of the same concept across modules (e.g., two different cache-warming routines)
- Utility functions reimplemented locally when a shared utility exists
- "Near-identical" code paths where the difference is a parameter that should be extracted
- Boilerplate blocks that appear in every X (service constructor, handler setup, etc.) and could become a base pattern

**What you do NOT consider duplication:**
- Small duplication (< 5 lines) where DRY-ing would add indirection (Sandi Metz: "duplication is far cheaper than the wrong abstraction")
- Test setup/factory duplication (test code is allowed to repeat setup for clarity)
- Types-only duplication (leave that for the Type Consolidation agent — but flag it if you spot it)

**Language-specific notes:**
- Python: look for duplicated `@classmethod` factories, repeated context-manager patterns, parallel `try/except` block structures
- TypeScript: look for duplicated reducer/selector patterns, repeated hook logic, similar service classes
- Scala/Rust: look for typeclass/trait implementations that repeat core behavior with minor tweaks
- Any language: look for duplicated request/response transformation pipelines

**Your workflow:**
1. Read project conventions and any existing shared-utility modules
2. Use Grep/Glob to find candidate repeated patterns (function signature patterns, distinctive string literals, common block shapes)
3. For each candidate, read all occurrences and judge: is this true behavioral duplication, or legitimate local variation?
4. For confirmed duplication, write a finding with the canonical location proposal (e.g., "extract to `src/utils/retry.py` which already has similar logic")

Spawn explorer subagents if you need to trace how candidates are used across the codebase. Do not spawn more than 3.
```

---

## Agent 2 — Type Consolidation (TC)

```
{COMMON PREAMBLE}

**Primary focus:** Repeated *type shapes* (struct/interface/class definitions) that should be unified into a single shared type.

**What you look for:**
- Two or more dataclasses / TypedDicts / interfaces / structs with identical or near-identical fields that represent the same concept
- Anonymous object/dict shapes that should be a named type (Python dict literals being passed around, TS object literals with repeated shape)
- Types that differ only in one nullable field — those should be a single type with optional field, not two types
- Enum equivalents duplicated across modules (two Literal['a', 'b', 'c'] that should be one Enum/type alias)
- Domain concepts expressed as raw primitives in some places and wrapped types in others (inconsistent modeling)

**What you do NOT consider:**
- Intentional type divergence (e.g., DTO vs domain entity deliberately differ) — the question is whether the divergence is intentional or accidental
- Weak type uses (`any`, `unknown`, `Any`) — leave for Weak Types agent
- Pure duplication of behavior — leave for Duplication agent

**Language-specific notes:**
- Python: `TypedDict`, `dataclass`, `pydantic.BaseModel`, `NamedTuple`, protocols
- TypeScript: `interface`, `type`, object literal shapes
- Rust: `struct`, `enum`, trait object shapes
- Scala: `case class`, sealed traits
- Go: `struct` with field duplication

**Your workflow:**
1. Enumerate type definitions in scope (grep for language-appropriate markers)
2. Cluster by field overlap (names + types)
3. For clusters with ≥80% field overlap, read both definitions and judge consolidation
4. Propose a single canonical type + where it should live (often a shared types module)
5. For flagged accidental uses of raw primitives, propose a newtype/wrapper

Include in each finding: the canonical type proposal with field list.
```

---

## Agent 3 — Dead Code (DC)

```
{COMMON PREAMBLE}

**Primary focus:** Code with **zero references** in the codebase — unreachable functions, unused exports, orphaned files, never-imported modules.

**Tool seed evidence (read if present):**
- `{TOOL_OUTPUT_DIR}/vulture.txt` (Python)
- `{TOOL_OUTPUT_DIR}/ruff.txt` (Python F401/F841)
- `{TOOL_OUTPUT_DIR}/knip.txt` (TS)
- `{TOOL_OUTPUT_DIR}/ts-prune.txt` (TS)
- `{TOOL_OUTPUT_DIR}/cargo-udeps.txt` (Rust)
- `{TOOL_OUTPUT_DIR}/deadcode.txt` (Go)
- `{TOOL_OUTPUT_DIR}/staticcheck.txt` (Go)

**What you look for:**
- Unused imports (but: Python `__init__.py` re-exports are NOT dead)
- Unused local variables
- Functions/methods with no callers (check dynamic dispatch, reflection, CLI command registration, decorators)
- Unused exported symbols
- Files that are never imported
- Unused dependencies in `package.json` / `pyproject.toml` / `Cargo.toml`

**Critical verification rules:**
- Tool says unused — verify by grepping the codebase. Tools have false positives from string-based lookups, `getattr`, `eval`, `Reflect.get`, CLI entry points, plugin registrations, `importlib`.
- Python specifically: `__all__`, `pytest` fixtures, `@app.route` decorators, `entry_points` in `setup.cfg`/`pyproject.toml`, `__subclasshook__` — anything reflective
- TypeScript: dynamic imports, DI containers, Next.js page/route files, test files loaded by glob
- When in doubt, lower confidence and note the reflection risk

**What you do NOT consider:**
- Code that is called but *shouldn't* exist (legacy/fallback — leave for Legacy agent)
- Dead *branches* inside live functions (not pure dead-code — flag as observation, lower confidence)

**Your workflow:**
1. Read all tool output files listed above
2. For each tool finding, verify by grepping the symbol name across the full codebase (including string literals, test files, config files)
3. Add LLM-only findings for dynamic/reflective cases the tools miss
4. Low-confidence findings on symbols that could plausibly be reflectively accessed
```

---

## Agent 4 — Circular Dependencies (CD)

```
{COMMON PREAMBLE}

**Primary focus:** Import/dependency cycles between modules, packages, or components.

**Tool seed evidence (read if present):**
- `{TOOL_OUTPUT_DIR}/madge.txt` (TS/JS)
- `{TOOL_OUTPUT_DIR}/dependency-cruiser.txt` (TS/JS)
- `{TOOL_OUTPUT_DIR}/pycycle.txt` (Python)
- `{TOOL_OUTPUT_DIR}/pydeps.txt` (Python)

**What you look for:**
- Direct cycles: A imports B, B imports A
- Transitive cycles: A → B → C → A
- Package-level cycles: package X imports from package Y, Y imports from X
- Delayed-import workarounds: `import` statements inside functions that exist solely to break an import cycle (flag these — the cycle is real, just hidden)
- TYPE_CHECKING-gated imports that only exist to break cycles (flag the underlying cycle)

**Critical nuances:**
- Some cycles are at the type level only (imported only in type annotations); still findings but lower priority
- Intentional cycles exist in some frameworks (Django's circular imports for model relationships) — flag and note the framework convention
- Propose a concrete untangling: extract shared types to a neutral module, invert dependency direction, introduce an interface

**Your workflow:**
1. Read tool outputs; cross-reference with project structure
2. For each cycle, read both ends and identify the *minimal* coupling (often one symbol)
3. Propose: (a) extract coupling point to a neutral shared module, or (b) dependency inversion, or (c) duplicate the single symbol to break the cycle
4. If only type-level, propose converting to TYPE_CHECKING / conditional-import as an intermediate step
```

---

## Agent 5 — Weak Types (WT)

```
{COMMON PREAMBLE}

**Primary focus:** Use of weak/loose types that erode static guarantees — `any`, `unknown`, `Any`, `object`, untyped kwargs, wide casts.

**Tool seed evidence (read if present):**
- `{TOOL_OUTPUT_DIR}/mypy.txt`
- `{TOOL_OUTPUT_DIR}/tsc-strict.txt`
- `{TOOL_OUTPUT_DIR}/pyright.txt`
- `{TOOL_OUTPUT_DIR}/clippy.txt`

**What you look for:**

Python:
- `Any` in function signatures (propose narrower)
- Untyped `*args`/`**kwargs` where concrete shape is known
- `Dict[str, Any]` that should be a TypedDict/dataclass
- Bare `dict`, `list`, `tuple` without generics
- `cast(X, y)` where a protocol/Protocol subclass could avoid the cast
- `# type: ignore` without a reason comment

TypeScript:
- `any`, `as any`, `<any>` (propose specific)
- `unknown` that's never narrowed (should be narrowed at boundary)
- `Object` / `{}` as a type
- `Function` as a type (should be callable signature)
- Widening casts (`as string` when the value is `string | number`)

Rust:
- `Box<dyn Any>` / `dyn Any` usage
- Excessive `Box<dyn Trait>` where generics would work
- `unwrap()` / `expect()` that hides the error type

Scala:
- `Any`, `AnyRef`, `AnyVal` in signatures
- `asInstanceOf[X]` (unchecked cast)

**Research requirement:**
For each weak type, research what the concrete type should be:
1. Read the code around the weak type — what is actually flowing through?
2. Read upstream producers and downstream consumers to infer the shape
3. Check related packages/SDKs for documented types (e.g., if `any` holds an AWS SDK response, the SDK has types)
4. If the concrete type requires a new type definition, note it (and flag as TC-candidate too)

**What you do NOT consider:**
- Type shapes that should be consolidated from multiple locations — flag to TC agent
- Weak types whose narrowing requires runtime validation (e.g., external JSON boundary) — flag as lower priority with note
```

---

## Agent 6 — Defensive Code (DF)

```
{COMMON PREAMBLE}

**Primary focus:** Defensive programming constructs that do not serve a specific, articulable purpose.

**What you look for:**
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

**What counts as "serving a purpose":**
- Handling unsanitized external input (API boundary, CLI input, network parse)
- Catching a specific exception type to convert it (e.g., `JSONDecodeError → InvalidRequestError`)
- Catching at the top-level of a long-running loop to keep processing next item
- Retry logic with explicit backoff
- Resource cleanup (`finally` blocks) — **never** flag these

**Critical rule:** You are evaluating whether each catch/guard has a *reason*. Absence of a reason = finding. Presence of a clear reason (even an implicit one) = leave it.

For each finding, include in the "Issue" field:
- **What this catches / guards against** (describe the defensive stance)
- **Why it is unnecessary** (the specific reason — "the only exception type this can throw is already handled upstream", "the type system already guarantees non-null", etc.)

Blast radius is almost always HIGH for this dimension (removing control-flow constructs alters failure behavior). Self-assess HIGH and let the Calibrator confirm.
```

---

## Agent 7 — Legacy / Fallback (LF)

```
{COMMON PREAMBLE}

**Primary focus:** Code that is referenced (i.e., not dead) but should be removed — superseded implementations, deprecated shims, v1-alongside-v2 patterns, "// old" or "// legacy" flags.

**What you look for:**
- Functions/classes named `*_v1`, `*_old`, `*_legacy`, `*_deprecated`, or with comments indicating they're superseded
- Two functions that do the same thing with "old" and "new" implementations, where the new one has full coverage
- Feature flags that have been on for X months and should be removed (code behind always-on flag should be inlined)
- Migration shims (e.g., "readCompat" / "readLegacy") that are supposed to be temporary
- Code paths that handle data shapes that no longer exist in production
- `@deprecated` annotations where all callers have migrated

**What you do NOT consider:**
- Truly unreachable code (that's Dead Code agent)
- Code that is ugly but current (that's Duplication or other dimensions)

**Critical verification rule:** "Should be removed" is a judgment call. For each legacy candidate, verify:
1. Is there a current replacement? Identify it by name.
2. Are all callers on the new version? List remaining old-version callers.
3. Is there external API stability that forbids removal? Check for public-API markers.

If any caller is still on the old version, your finding is: "migrate remaining callers, then remove" — two-step, not a direct removal.

**Your workflow:**
1. Grep for legacy markers (`legacy`, `deprecated`, `_v1`, `_old`, `TODO: remove`, `XXX`, `HACK`)
2. For each marker region, trace callers and replacements
3. For feature-flag-wrapped code, check the flag's status (if you can find it in config or code)
4. Propose concrete removals with migration steps if needed

Blast radius varies — a feature flag always-on is LOW, an API removal with external callers is HIGH.
```

---

## Agent 8 — Comment / Slop Cleanup (CS)

```
{COMMON PREAMBLE}

**Primary focus:** Comments that should be removed or replaced — AI slop, in-motion narration, stating-the-obvious, stale TODOs, commented-out code.

**What you look for:**
- Obvious-statement comments: `# increment the counter` above `counter += 1`, `// parse the JSON` above `JSON.parse(raw)`
- In-motion narration: comments describing work-in-progress, migrations, or "replaces X" references ("// replaced the old method here", "# TODO: we need to fix this later")
- AI-assistant slop: "Enhanced function to...", "Added a robust check for...", "This function handles the case where..." — restates the code or narrates the AI's work
- Commented-out code blocks (should be deleted; git has history)
- Stale TODOs older than 6 months without context
- Redundant docstrings that restate the function name ("fetches the user" above `def fetch_user`)
- Section banners that add no info (`# ========== HELPERS ==========` above a single helper)
- Divider comments that separate one function from another (language-aware editors do this)

**What you KEEP (or propose improving rather than deleting):**
- Comments explaining *why* (business logic rationale, constraints, workarounds)
- Comments warning about non-obvious gotchas ("this must run before X, else Y")
- Docstrings with parameter/return info, examples, or behavioral contracts
- Licensing headers, attribution
- Module-level explanations of purpose when non-obvious
- Links to tickets/RFCs that explain a decision

**Judgment call rubric:**
Ask: "Would a new developer reading this file understand the code better with this comment, or without it?" If without — remove. If better with — keep.

For slop comments that describe work done, replace with a useful comment (explain why, not what) if there's a useful why to articulate. Otherwise delete.

**Important:** Be careful not to flag:
- `cleanup-sweep-skip` markers (those are skill metadata)
- Type-checking ignore comments with rationales (`# type: ignore[reason]`)
- Linter-ignore comments with rationales (`// eslint-disable-next-line no-unused-vars -- used by X`)

Blast radius is almost always LOW for this dimension (comments don't affect runtime behavior). Self-assess LOW and let the Calibrator confirm.
```

---

## Launching the 8 Agents

Use subagents on the flagship-tier model (Sol-class) with `reasoning_effort: "high"` for each. Launch all 8 in one parallel batch. Example pattern:

```
spawn_agent(agent_type="default", model="<flagship>", reasoning_effort="high", message="<Agent 1 prompt with substitutions>")
spawn_agent(agent_type="default", model="<flagship>", reasoning_effort="high", message="<Agent 2 prompt>")
... (all 8 in one message)
```

While agents run, the main thread:
- Updates `status.md` to `Phase: analyze, Step: awaiting-8-dimension-agents`
- Does not duplicate work (no parallel main-thread grep for findings)

## Post-Analysis Consolidation

After all 8 agents complete:

1. Verify each agent produced its findings file. If any is missing or clearly inadequate, retry once with a more specific prompt addressing what went wrong. If second attempt fails, note in `status.md` and proceed with the other 7 (note the gap in the final report).

2. Count total findings per dimension. Update `status.md`:

```markdown
- Phase: analyze-complete
- Step: ready-to-calibrate
- Findings per dimension: DU=X, TC=Y, DC=Z, CD=A, WT=B, DF=C, LF=D, CS=E
- Total raw findings: (sum)
- Next action: launch Calibrator agent
```

3. Announce: *"Phase 2 complete. N raw findings across 8 dimensions. Entering Phase 3 (Calibrator)."* Read `references/phase-3-calibrate.md` before proceeding.
