# Phase 4: Implementation

The plan is validated. This phase executes it.

## Phase 4.1: Execute the Plan

Now we build. The execution follows the strategy defined in the plan.

### For each task (or wave of parallel tasks):

1. **Spawn a subagent** with fresh context. Provide it with:
   - The specific task description from the implementation plan
   - The overall plan context (so it understands how its task fits)
   - Access to the codebase
   - The CI checks list from the plan
   - A directive to read and follow the project's software design guides, if they exist (see Software Design Principles in SKILL.md) — the implementing agent must apply the design principles, not just the task spec
   - A directive to read `references/implementation-agent-protocol.md` before editing
   - A short mandatory checklist in the prompt:
     - assess whether the task is performance-sensitive
     - if it is, sketch the algorithm first and identify obvious I/O and complexity risks before implementing
     - justify any intentional exceptions to the protocol's batching or data-structure defaults
     - report any performance-sensitive decisions back in the task summary

2. **The implementing agent** (latest available Codex model, `reasoning_effort: low` — the plan is explicit; bump to `medium` only if the task spec turns out to be ambiguous):
   - Reads the relevant parts of the codebase
   - **Assesses whether the code is performance-sensitive** (per the implementation agent protocol)
   - If performance-sensitive: writes a pseudocode/comment sketch first, maps out Big O complexity and I/O calls, identifies and resolves bottlenecks, THEN implements
   - If not performance-sensitive: implements directly
   - Verifies against the performance checklist (no queries in loops, correct data structures, batched I/O, pre-built indices)
   - Runs the linter and the tests specified in the task's **Verification** section
   - Fixes any issues found
   - Reports back: what was done, what files were changed, any performance decisions made, any concerns

3. **Verify** — the level of verification depends on task complexity:
   - **Complex tasks** (multi-file changes, architectural modifications, tricky logic): Spawn a **fresh verification subagent** (latest available Codex model, `reasoning_effort: low`) that independently reviews the implementation — does it match the task spec? Do verification criteria pass? Any obvious issues?
   - **Simple tasks** (single-file, small diff, straightforward logic): CI checks from step 2 are sufficient. Skip the verification subagent.

4. **Commit** the task's changes with a clear commit message describing what was done
   - Update `status.md` with the current task or next task after each commit

5. **If something goes wrong** (tests fail, the approach doesn't work, unexpected complications):
   - The agent stops and reports the issue
   - Present it to the user with: what happened, why, and suggested options for how to proceed
   - Wait for user direction before continuing

### After each wave (for wave-based execution)

If the implementation plan uses waves, run a broader CI subset after each wave that touched shared infrastructure, core abstractions, or multiple modules. This is in addition to each task's local verification.

### After all tasks are complete:

1. Run the full CI check suite one final time
2. If anything fails, enter a fix cycle (max 3 attempts):
   - Diagnose the failure
   - Fix it
   - Re-run checks
   - After 3 failed attempts, stop and present the full diagnostic to the user

Phase 4 is complete. Announce it and proceed to Phase 5.
Update `status.md` to `Current phase: 4`, `Current step: 4-complete`, and `Next action: Run final validation`.
