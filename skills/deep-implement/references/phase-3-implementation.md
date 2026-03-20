# Phase 3: Implementation

The amended proposal describes *what* and *why*. This phase turns it into *how* and then *does it*.

## Phase 3a: Create the Implementation Plan

Launch a **subagent with fresh context** that receives:
- The amended proposal document path
- Access to the full codebase
- Access to project CI configuration (to understand what checks must pass)

The subagent analyzes the proposal against the codebase and produces an implementation plan.

Before planning, the subagent must read the project's software design guides (if they exist):
- `docs/architecture/software-design-guide.md` — core principles
- The language-specific guide (Scala ZIO or Python) relevant to the change

The plan must reflect these principles. In particular: new module boundaries should only be introduced where they hide significant complexity, internal steps should be plain classes/functions (not framework services), and the design should pull complexity downward rather than pushing it onto callers.

### Plan Structure

Write to `docs/plans/<feature-name>/implementation-plan.md`:

```markdown
# Implementation Plan: <Feature Name>

## Overview
Brief summary of what's being implemented and the overall approach.

## CI Checks
List of CI checks that must pass (derived from reading CI config files):
- e.g., `ruff check src/ tests/`
- e.g., `pytest -m "not integration"`
- etc.

These checks will be run after every task to catch issues early.

## Execution Strategy
Whether tasks run sequentially (single agent) or in waves (parallel where possible).
Explain why this strategy was chosen based on task dependencies and complexity.

## Tasks

### Wave 1 (parallel / no dependencies)

#### Task 1: <Title>
**What**: Clear description of the change — specific enough that an agent with only
this task description and the codebase can implement it without ambiguity.
**Files affected**: List of files to create/modify/delete
**Approach**: How to implement this — key decisions, patterns to follow, gotchas to watch for
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

The planning agent decides the strategy based on:

- **Sequential (single agent)**: When tasks are small, tightly coupled, or there are only 2-3 of them. One agent works through them in order. Good for small/medium changes.
- **Waves (parallel + sequential)**: When there are independent tasks that can run simultaneously, followed by tasks that depend on them. Good for larger changes. Each parallel task gets its own agent with fresh context.

The guiding principle is **context bloat**: an agent should only carry the context it needs. If one agent can handle 5 minor related tasks without context issues, let it. For bigger tasks, dedicate a fresh agent that reads only what it needs.

### Plan Quality Criteria

A good plan should:
- Cover everything in the proposal (nothing missing)
- Have no unnecessary tasks (no gold-plating or scope creep)
- Be at the right granularity — each task is a coherent unit of work that results in a working, committable state
- Have correct dependency ordering
- Include concrete verification criteria (not just "check it works")
- Be self-contained enough that an agent with no conversation history can execute it
- Follow the project's software design principles — new abstractions should be deep (not shallow wrappers), module boundaries should hide complexity, and internal steps should be plain classes/functions rather than framework services

Commit the implementation plan.

## Phase 3b: Validate the Plan

Launch another **subagent with fresh context** to validate the plan against the proposal. It receives:
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

If issues are found:
- **Straightforward fixes** (wrong dependency order, missing test, unclear description): Auto-fix by updating the plan directly
- **Complex/ambiguous issues** (scope questions, architectural trade-offs): Present to the user for a decision, similar to Phase 2b but typically briefer

Write validation findings to `docs/plans/<feature-name>/plan-validation.md`. Update the implementation plan with any fixes. Commit both.

## Phase 3c: Execute

Now we build. The execution follows the strategy defined in the plan.

### For each task (or wave of parallel tasks):

1. **Spawn a subagent** with fresh context. Provide it with:
   - The specific task description from the implementation plan
   - The overall plan context (so it understands how its task fits)
   - Access to the codebase
   - The CI checks list from the plan
   - A directive to read and follow the project's software design guides (`docs/architecture/software-design-guide.md` and the relevant language-specific guide) — the implementing agent must apply the design principles, not just the task spec

2. **The implementing agent**:
   - Reads the relevant parts of the codebase
   - Implements the change
   - Runs the linter and the tests specified in the task's **Verification** section (not the full suite — that runs once after all tasks)
   - Fixes any issues found
   - Reports back: what was done, what files were changed, any concerns

3. **Verify** — the level of verification depends on task complexity:
   - **Complex tasks** (multi-file changes, architectural modifications, tricky logic): Spawn a **fresh verification subagent** that independently reviews the implementation — does it match the task spec? Do verification criteria pass? Any obvious issues?
   - **Simple tasks** (single-file, small diff, straightforward logic): CI checks from step 2 are sufficient. Skip the verification subagent.

4. **Commit** the task's changes with a clear commit message describing what was done

5. **If something goes wrong** (tests fail, the approach doesn't work, unexpected complications):
   - The agent stops and reports the issue
   - Present it to the user with: what happened, why, and suggested options for how to proceed
   - Wait for user direction before continuing

### After all tasks are complete:

1. Run the full CI check suite one final time
2. If anything fails, enter a fix cycle (max 3 attempts):
   - Diagnose the failure
   - Fix it
   - Re-run checks
   - After 3 failed attempts, stop and present the full diagnostic to the user

Phase 3 is complete. Announce it and proceed to Phase 4.
