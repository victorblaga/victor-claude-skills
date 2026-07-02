---
name: goal-prompt
description: >
  Generate a copy-paste-ready /goal prompt for Claude Code or Codex implementation loops.
  Use when the user asks for a goal prompt, goal-loop prompt, Claude /goal prompt, Codex goal
  prompt, or wants to turn a JIRA ticket or software task into a durable implementation prompt
  with workstream-implementer, review loops, optional mega-review, and performance profiling.
---

# Goal Prompt

Create a single prompt the user can paste into a `/goal` loop. Do not implement the work yourself.

Default target is **Claude Code** unless the user asks for Codex. For Claude prompts, refer to `/workstream-implementer`, `/simplify`, and `/mega-review`. For Codex prompts, refer to `$victor-codex-skills:workstream-implementer`, `$simplify`, and `$victor-codex-skills:mega-review`.

## Inputs

Extract:

- target runtime: Claude Code, Codex, or unspecified
- task text or JIRA key
- repo, project, branch, or PR hints
- explicit quality gates: simplify, mega-review, performance-critical, browser verification, CI, commit/PR preferences
- non-goals, constraints, and acceptance criteria

Ask for the missing task only if there is no usable task, ticket, PR, or file context. If the user gives no JIRA key, do not block prompt generation; include the JIRA gate in the generated prompt.

## Prompt Requirements

The generated prompt must require the goal-loop agent to:

1. Use `workstream-implementer` as the outer controller.
2. Start with a JIRA gate:
   - If a JIRA key is supplied, read and manage that ticket through MCP first, falling back to the REST API only if MCP is unavailable.
   - If no JIRA key is supplied, ask whether to search for a related ticket, create a ticket, create/link a subtask under a parent ticket, or proceed without JIRA.
   - Treat JIRA as optional unless the user chooses ticket-backed work, but make the decision explicit before implementation.
3. Work the task through implementation, verification, PR creation/update, CI, and JIRA review handoff according to `workstream-implementer`.
4. Run an adversarial review loop after implementation:
   - Use the highest-reasoning reviewer available in the environment.
   - Review the diff against the ticket/task contract, repo conventions, tests, verification evidence, and user constraints.
   - If Critical or Major findings remain, fix them and re-review.
   - Stop after a clean review or 5 review cycles, whichever comes first.
   - Ignore nits unless they reveal correctness, maintainability, security, or performance risk.
5. Run `simplify` and `mega-review` when explicitly requested or when the task is complex/risky.
   - Complexity/risk triggers include multi-repo work, architecture changes, migrations, auth/security, data model changes, concurrency, performance-sensitive paths, large diffs, or unclear acceptance criteria.
   - Run `simplify` before `mega-review`.
   - Implement mega-review findings by criticality and leverage: Critical, High, and high-impact or easy Medium/Low findings. Ignore pure nits.
6. Make performance-profile changes explicit when performance matters or the touched path is performance-sensitive.
   - Establish the relevant baseline before changing code when feasible; if not feasible, document why and use the best available comparison.
   - Capture a before/after profile appropriate to the change: latency, throughput, query count, query plan, Big O, memory use, storage footprint, batching/indexing, pipeline runtime, or operational cost.
   - Check for N+1 calls, missing indexes, unbounded reads, unnecessary materialization, poor batching, repeated scans, and algorithm/data-structure mismatches.
   - Surface trade-offs, not just regressions. Examples: "storage increases about 2x to reduce lookup latency", "memory rises for batching", "writes get slower so reads get faster".
   - Pause for explicit user acceptance when a material performance, storage, memory, cost, or complexity trade-off appears. Do not hide trade-offs in the final summary after the decision has already been made.
   - If no measurable performance surface exists, state why.
7. Verify before declaring completion. Quote the relevant command output or browser evidence in the final summary.

## Output Format

Output only one fenced `text` block unless the user asks for explanation. Make the prompt self-contained and directly pasteable.

Use this structure:

```text
/goal
You are working on: <task or ticket summary>

Use <workstream-implementer skill> as the outer controller for this work.

JIRA gate:
<ticket-specific or no-ticket instructions>

Execution:
1. Refine the task contract and acceptance criteria before implementation.
2. Scope affected repos and check worktree state before branching.
3. Implement the task, keeping changes focused on the approved contract.
4. Run the relevant verification commands and browser checks.
5. Open or update PRs, monitor CI, and update JIRA when applicable.

Adversarial review loop:
<review-loop instructions>

Simplify and mega-review gate:
<conditional instructions>

Performance profile gate:
<conditional instructions>

Completion criteria:
<stop conditions and final report requirements>
```

Collapse empty sections when the user explicitly says they do not apply, but keep the JIRA gate unless the user already explicitly declined JIRA.
