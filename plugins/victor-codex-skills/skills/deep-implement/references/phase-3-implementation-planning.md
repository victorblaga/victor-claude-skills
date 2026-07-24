# Phase 3: Implementation Planning

The amended proposal describes *what* and *why*. This phase turns it into an executable plan.

## Phase 3.1: Create the Implementation Plan

Launch a **subagent with fresh context** (tier: DEEP — see Capability Tiers in SKILL.md) that receives:
- The amended proposal document path
- Access to the full codebase
- Access to project CI configuration (to understand what checks must pass)

The subagent analyzes the proposal against the codebase and produces an implementation plan.

Before planning, the subagent must read the project's software design guides if they exist (commonly under `docs/architecture/` — the language-agnostic guide plus the guide for the language being changed).

The plan must reflect these principles. In particular: new module boundaries should only be introduced where they hide significant complexity, internal steps should be plain classes/functions (not framework services), and the design should pull complexity downward rather than pushing it onto callers.

### Plan Structure

Write to `.scratch/docs/plans/<feature-name>/implementation-plan.md`:

```markdown
# Implementation Plan: <Feature Name>

## Overview
Brief summary of what's being implemented and the overall approach.

## CI Checks
List of CI checks that must pass (derived from reading CI config files):
- e.g., `ruff check src/ tests/`
- e.g., `pytest -m "not integration"`
- etc.

These checks will be run during implementation to catch issues early.

## Execution Strategy
Whether tasks run sequentially or in waves (parallel where possible).
Explain why this strategy was chosen based on task dependencies and complexity.
Note: this is a dependency/ordering strategy. The orchestrator assigns inline vs subagent
execution per task in Phase 4.0 — see suggested execution modes on each task below.

## Tasks

### Wave 1 (parallel / no dependencies)

#### Task 1: <Title>
**What**: Clear description of the change — specific enough that an agent with only
this task description and the codebase can implement it without ambiguity.
**Files affected**: List of files to create/modify/delete
**Approach**: How to implement this — key decisions, patterns to follow, gotchas to watch for
**Suggested execution**: inline / subagent — brief rationale (e.g., "inline — single file, straightforward")
**High-risk**: yes / no — if yes, note why (auth, migration, concurrency, public API, etc.)
**Verification**: How to confirm this task is done correctly
  - Tests to run
  - Behavior to check
  - CI checks to pass
**Dependencies**: None (Wave 1)

#### Task 2: <Title>
...

### Wave 2 (depends on Wave 1)

#### Task 3: <Title>
**Dependencies**: Task 1, Task 2
...

## Risk Notes
Anything the implementing agent should watch out for — fragile areas of the codebase,
non-obvious constraints, things that might look wrong but are intentional.
```

### Execution Strategy Decision

The planning agent decides the dependency/ordering strategy based on:

- **Sequential**: When tasks are small, tightly coupled, or there are only 2-3 of them. Good for small/medium changes.
- **Waves (parallel + sequential)**: When there are independent tasks that can run simultaneously, followed by tasks that depend on them. Good for larger changes.

For each task, the planner also suggests an execution mode (`inline` or `subagent`) and whether it is **high-risk** (needs independent verification — see Phase 4). These are recommendations only. The orchestrator makes the final assignment in Phase 4.0 based on live context — e.g., a task suggested as `subagent` may run inline if context is clean and the diff is small; conversely, inline may become subagent if the main thread is already heavy.

Default planner bias: suggest **`inline`** unless there is a concrete reason for `subagent` (large exploration surface, parallelizable independence, or DEEP-tier reasoning need).

The guiding principle is **efficiency over ceremony**: prefer batching related small tasks and inline execution; reserve subagents for work that genuinely benefits from fresh context or parallelization.

### Plan Quality Criteria

A good plan should:
- Cover everything in the proposal (nothing missing)
- Have no unnecessary tasks (no gold-plating or scope creep)
- Be at the right granularity — each task is a coherent unit of work that results in a working, committable state
- Have correct dependency ordering
- Include concrete verification criteria (not just "check it works")
- Be self-contained enough that an agent with no conversation history can execute it
- Follow the project's software design principles — new abstractions should be deep (not shallow wrappers), module boundaries should hide complexity, and internal steps should be plain classes/functions rather than framework services
- Tag each task with a suggested execution mode and high-risk flag to inform Phase 4.0 orchestration

Commit the implementation plan.
Update `status.md` to `Current phase: 3`, `Current step: 3.1-plan-complete`, and `Next action: Validate the implementation plan`.

## Phase 3.2: Validate the Plan

Launch another **subagent with fresh context** (tier: DEEP — see Capability Tiers in SKILL.md) to validate the plan against the proposal. It receives:
- The amended proposal
- The implementation plan
- Access to the codebase

The validator checks:
1. **Coverage**: Does the plan implement everything in the proposal? Anything missing?
2. **Unnecessary work**: Are there tasks that go beyond the proposal scope?
3. **Dependencies**: Are they correct? Could any sequential tasks be parallelized?
4. **Granularity**: Should any small tasks be merged into one? Should any large task be split?
5. **Verification**: Are the verification criteria actually testable and sufficient?
6. **Feasibility**: Are there technical issues the plan doesn't account for?
7. **Orchestration hints**: Are suggested execution modes reasonable? Are high-risk flags accurate (not over-flagged)?

If issues are found:
- **Straightforward fixes** (wrong dependency order, missing test, unclear description): Auto-fix by updating the plan directly
- **Complex/ambiguous issues** (scope questions, architectural trade-offs): Present to the user for a decision, similar to Phase 2.2 but typically briefer

Write validation findings to `.scratch/docs/plans/<feature-name>/plan-validation.md`. Update the implementation plan with any fixes. Commit both.
Update `status.md` to `Current phase: 3`, `Current step: 3.2-validation-complete`, and `Next action: Start implementation`.

Phase 3 is complete. Announce it and proceed to Phase 4.
