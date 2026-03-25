# Phase 1: Exploration

This phase applies to **refactor** and **migrate** modes. For greenfield, skip to Phase 2.

## Purpose

Build a comprehensive understanding of the existing codebase before proposing any structural changes. Use maximum parallelism — six specialized agents exploring simultaneously from different angles.

## Small Codebase Escape Hatch

For small codebases (~10 files or fewer), six parallel agents are overkill. Instead:

1. **Read the code directly** — it fits in context. No need for specialized agents.
2. **Combine the exploration** into a single pass: structure, interfaces, flow, dependencies, cross-cutting concerns, tests — all in one read-through.
3. **Proceed directly to synthesis** — produce the runtime architecture diagram and findings, then move to Phase 2.

The six-agent approach is for codebases too large to read in a single context window. Don't force the ceremony when the codebase is small enough to understand directly.

## Agents

Launch all six agents in parallel using the Agent tool. Each agent gets:
- The target directory path
- A clear, specific exploration brief (below)
- Instructions to write findings to a temporary file in the plan directory

### Agent 1: Structure

**Brief:** Map the physical organization of the codebase.

- File tree (directories, modules, packages)
- Module boundaries — what's exported from each module (e.g. `__init__.py` in Python, `mod.rs` in Rust, `index.ts` in TypeScript)
- Package organization — how code is grouped
- File sizes — which files are large (potential god modules)
- Entry points — where execution starts

**Output:** A tree view with annotations on each node (file count, rough purpose, export surface).

### Agent 2: Interface

**Brief:** Map the public API surface.

- Function and class signatures (names, parameters, return types)
- Type annotations — what's typed, what's `Any` or untyped
- What each module exposes vs. what it keeps internal
- Data types / dataclasses / models — the shape of data flowing through the system

**Output:** Per-module summary of public interface (signatures + one-line purpose).

### Agent 3: Flow

**Brief:** Trace how data and control move through the system.

- Entry points — what triggers execution (CLI, queue, cron, API)
- Call chains — who calls whom, how deep do the chains go
- Data flow — what data enters, how it transforms, where it exits
- Decision points — where does the code branch (routers, dispatchers, conditionals)
- Lifecycle — startup, main loop, shutdown, error recovery

**Output:** Narrative description of the main flows, with file:line references.

### Agent 4: Dependency

**Brief:** Map coupling between modules and external dependencies.

- Internal imports — which modules depend on which (build a dependency graph)
- External libraries — what's used where
- Tight coupling — modules that import heavily from each other
- Circular dependencies — any import cycles
- Isolated modules — modules with few dependencies (potential clean boundaries)

**Output:** Dependency summary per module (imports from, imported by, external deps).

### Agent 5: Cross-Cutting

**Brief:** Identify patterns that span multiple modules.

- Logging — how it's done, where, what framework
- Error handling — patterns, custom exceptions, bare excepts
- Configuration — how config is loaded and passed around
- Storage / I/O — how files, databases, queues are accessed
- Infrastructure mechanics — AWS SDK usage, HTTP clients, DB drivers
- State management — global state, singletons, shared mutable state

**Output:** Per-concern summary: what pattern is used, where it's consistent, where it deviates.

### Agent 6: Tests

**Brief:** Understand what the tests reveal about intended behavior.

- Test file organization — how tests map to source modules
- What's tested — which modules/functions have coverage
- What's NOT tested — gaps
- Test style — unit vs integration, mocks vs real services, factories
- Assertions — what outcomes are verified (behavior vs. implementation)
- Test helpers / fixtures — shared test infrastructure

**Output:** Test coverage map + notes on what the tests reveal about design intent.

## Synthesis

Once all six agents complete, synthesize their findings:

1. **Read all six agent outputs**
2. **Describe the runtime architecture first** — before any static/structural analysis, answer: how does this system actually run? What processes exist, how do they communicate, what is the main loop structure, where does data flow at runtime? Produce a **behavioral mermaid diagram** showing processes, communication channels (queues, filesystem, shared memory), and the main workflows. This is the mental model that makes everything else make sense — lead with it.
3. **Identify the main architectural units** — the top-level modules/components that the code naturally groups into
4. **Flag design principle violations** — using the red flags checklist from `design-principles.md`:
   - Shallow modules, pass-through chains
   - Information leakage across boundaries
   - Temporal decomposition
   - Infrastructure mechanics leaking into domain code
   - Giant utility modules
   - ABC hierarchies for sequential steps
5. **Write the findings appendix** — a section listing violations and observations, linked to specific files/lines
6. **Feed everything into Phase 2** — the outline generation

## Migration Mode

When migrating, run the same six agents against the **old/reference** codebase. The agents should also note:
- What logic needs to be preserved (business rules, algorithms, domain knowledge)
- What should be discarded (legacy patterns, deprecated approaches, tech debt)
- What constraints the old code reveals (edge cases, invariants, non-obvious requirements)

The outline in Phase 2 will target the **new** project structure, using the old code as reference.

## Agent Configuration

Prefer lightweight agent types for exploration — this is search and retrieval work, not deep judgment. Use the `Explore` subagent type for file discovery and code search. Use `general-purpose` when the agent needs to reason about what it finds (e.g., tracing call chains, identifying design patterns).

Keep each agent's prompt self-contained — include the target path, what to look for, and the output format. Agents have no access to the conversation history.

If an agent produces empty or unusable output (e.g., the codebase doesn't have tests, or there are no cross-cutting patterns worth noting), skip that finding rather than forcing it into the synthesis. Not every agent will produce useful output for every codebase.
