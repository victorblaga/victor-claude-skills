# Phase 4: Implementation

The plan is validated. This phase executes it.

## Phase 4.0: Orchestration Plan

Before writing code, the **orchestrator** (main thread) reviews the validated implementation plan and assigns an execution mode to each task. The planner's suggestions (see Phase 3) are a starting point — the orchestrator makes the final call based on current context, dependencies, and what is already loaded.

### Execution modes

- **`inline`** (default) — the orchestrator implements the task directly in the main thread. Use for most tasks: small-to-medium diffs, sequential dependent chains, tasks touching files already in context, or anything you can complete without bloating the conversation.
- **`subagent`** — a dedicated fresh-context agent. Justify with a stated reason. Valid reasons:
  - Task needs DEEP-tier reasoning the orchestrator should not burn main-context budget on
  - Task is large or exploratory and would flood the main thread with tool noise
  - 2+ independent tasks can genuinely run in parallel (spawn in the same turn)
  - Main context is already heavy and needs offloading

**Batching**: one subagent may own several related tasks (e.g., "tasks 3+4, same module") rather than one agent per task.

**Guiding rule**: the null hypothesis is **inline**. Every spawn needs a one-line reason. Do not spawn agents for agents' sake.

### What to produce

1. State the assignment briefly to the user, e.g.: "Tasks 1, 2, 5 inline; task 3 → dedicated subagent (new subsystem, heavy exploration); tasks 4+6 batched to one subagent (independent of 3)."
2. Record the assignment in `status.md` under a short **Orchestration** section or in `Current step`, e.g. `4.0-orchestration-complete`.
3. Proceed to Phase 4.1.

If the plan has only 2–3 small, sequential tasks and context is clean, the orchestration plan may be a single sentence ("All tasks inline — small sequential change") without a formal table.

## Phase 4.1: Execute the Plan

Now we build. Execution follows the orchestration plan from Phase 4.0.

### For each task (or batched group / wave):

#### If mode is `inline`

The orchestrator implements directly:

1. Read the task description, affected files, and approach from the plan
2. Read and follow the project's software design guides if they exist (see Software Design Principles in SKILL.md)
3. Read `references/implementation-agent-protocol.md` before editing
4. Assess whether the task is performance-sensitive; if so, sketch the algorithm and I/O risks before implementing
5. Implement the change
6. Run the task's local verification (see **Per-task verification** below)
7. Commit with a clear message; update `status.md`

#### If mode is `subagent`

Spawn a subagent with fresh context. Provide it with:

- The specific task description(s) from the implementation plan
- The overall plan context (so it understands how its task fits)
- Access to the codebase
- The CI checks list from the plan
- A directive to read and follow the project's software design guides, if they exist (see Software Design Principles in SKILL.md)
- A directive to read `references/implementation-agent-protocol.md` before editing
- A short mandatory checklist in the prompt:
  - assess whether the task is performance-sensitive
  - if it is, sketch the algorithm first and identify obvious I/O and complexity risks before implementing
  - justify any intentional exceptions to the protocol's batching or data-structure defaults
  - report any performance-sensitive decisions, and any decisions made under underspecification, back in the task summary

**The implementing subagent** (tier: STANDARD — see Capability Tiers in SKILL.md; well-specified, low-risk tasks can drop to LIGHT; use DEEP only for tasks the plan flags as tricky — architectural, concurrency, performance-critical):

- Reads the relevant parts of the codebase
- Assesses whether the code is performance-sensitive (per the implementation agent protocol)
- If performance-sensitive: writes a pseudocode/comment sketch first, maps out Big O complexity and I/O calls, identifies and resolves bottlenecks, THEN implements
- If not performance-sensitive: implements directly
- Verifies against the performance checklist (no queries in loops, correct data structures, batched I/O, pre-built indices)
- Runs the task's local verification (see **Per-task verification** below)
- Reports back: what was done, what files were changed, any performance decisions made, any decisions made under underspecification, any concerns

The orchestrator reviews the result, commits with a clear message, and updates `status.md`. Do not spawn a separate verification subagent unless the task is flagged high-risk (below).

### Per-task verification

After each task — whether implemented inline or by a subagent — run only that task's **local checks** from the plan:

- Linter on affected files
- Tests listed in the task's **Verification** section
- Any task-specific behavior checks

Fix failures before committing. This is quick, mechanical confirmation that the task spec holds — not an independent audit.

**Independent verification subagent** (rare opt-in): spawn only when the plan explicitly flags a task as **high-risk** (auth, data migrations, concurrency, public API contract changes, or similar). Tier: STANDARD. The subagent independently reviews: does the implementation match the task spec? Do verification criteria pass? Any obvious issues? For all other tasks, local checks plus the end-of-phase CI run and Phase 5 audit are sufficient.

### After each task

1. **Commit** the task's changes with a clear commit message describing what was done
2. Append any reported decisions (underspecification or performance-sensitive) — whether the task ran inline or in a subagent — to `decisions.md` next to `status.md`; skip if there are none
3. Update `status.md` with the current task or next task

### If something goes wrong

(tests fail, the approach doesn't work, unexpected complications):

- Stop and report the issue
- Present it to the user with: what happened, why, and suggested options for how to proceed
- Wait for user direction before continuing
- Revisit the orchestration plan if the failure suggests inline was the wrong mode — escalate to a subagent or DEEP tier for retry

### After each wave (for wave-based execution)

If the implementation plan uses waves, run a broader CI subset after each wave that touched shared infrastructure, core abstractions, or multiple modules. This is in addition to each task's local verification.

### After all tasks are complete

1. Run the full CI check suite one final time
2. If anything fails, enter a fix cycle (max 3 attempts):
   - Diagnose the failure
   - Fix it
   - Re-run checks
   - After 3 failed attempts, stop and present the full diagnostic to the user

Phase 4 is complete. Announce it and proceed to Phase 5 — the primary independent verification gate (proposal coverage audit).
Update `status.md` to `Current phase: 4`, `Current step: 4-complete`, and `Next action: Run final validation`.
