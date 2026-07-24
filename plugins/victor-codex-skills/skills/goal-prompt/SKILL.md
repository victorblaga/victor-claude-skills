---
name: goal-prompt
description: >
  Generate a copy-paste-ready /goal prompt for Claude Code or Codex goal loops — whether the
  goal is a software task or JIRA ticket, or non-development work such as research, writing,
  analysis, planning, data work, or operations in hosted tools. Trigger ONLY when the user
  explicitly says "goal-prompt", "generate a goal prompt", "goal-loop prompt", or invokes
  $goal-prompt. Do NOT trigger on general prompt-writing or "write me a prompt" requests.
---

# Goal Prompt

Create a single prompt the user can paste into a `/goal` loop. Do not implement the work yourself.

Default target is **Claude Code** unless the user asks for Codex. For Claude prompts, refer to `/workstream-implementer` and `/simplify`. For Codex prompts, refer to `$victor-codex-skills:workstream-implementer` and `$simplify`.

## Inputs

Extract:

- target runtime: Claude Code, Codex, or unspecified
- goal text, task description, or JIRA key
- repo, project, branch, PR, or deliverable-destination hints
- explicit quality gates: simplify, performance-critical, browser verification, CI, commit/PR preferences
- provenance signals: whether the work implements prior review findings (adversarial review, PR/Bugbot feedback)
- non-goals, constraints, and acceptance criteria

Ask for the missing goal only if there is no usable task, ticket, PR, or file context.

## Goal Classification Gate

Classify the goal BEFORE generating. Do not default to the dev workstream shape.

- **Dev-workstream goal** — changes code or repo-managed content, flows through branch/PR/CI, and could plausibly be ticket-backed. Use the Dev template.
- **General goal** — research, writing, analysis, planning, data work, personal organization, or operations in hosted tools (Confluence, Notion, spreadsheets, dashboards). No repo/PR/CI surface. Use the General template.
- **Unclear or mixed** — ask the user one question before generating: "Should this run as a dev workstream (repo, branch/PR/CI, optional JIRA) or as a general goal loop?" Do not guess.

Signals the goal is NOT dev work: no repo or codebase mentioned, the deliverable is a document/decision/analysis, the work lives in hosted tools, no ticket or team process in sight. A JIRA key or a named repo is a strong dev signal, but confirm when the deliverable itself is non-code.

The JIRA gate belongs to the Dev template. Add it to a General prompt only when the user explicitly mentions a ticket or tracker.

## Prompt Style Requirements

Generated prompts run under strong reasoning models (GPT-5.6-class Codex, Claude). Write them accordingly:

- **Outcome-first**: state the goal, success criteria, hard constraints, and stop rules. Do not prescribe step-by-step tool usage the agent can work out itself.
- **Each rule once**: never repeat an instruction for emphasis. These models follow prompt contracts closely — duplicated or contradictory rules destabilize behavior more than missing detail, and repeated "ask first" reminders cause needless approval pauses.
- **Absolutes only for invariants**: reserve ALWAYS/NEVER/must for true invariants (safety, destructive actions, required evidence). For judgment calls — when to search, ask, or keep iterating — give decision criteria instead.
- **One autonomy boundary**: state once that in-scope local work (reading, editing, running non-destructive verification) proceeds without asking, and that confirmation is required for destructive actions, external writes/publishing, material scope expansion, or material trade-offs.
- **Stop rules**: completion criteria double as stop rules — say when to retry, when to fall back, when to ask, and when the loop is done. Keep loops bounded (e.g. the 5-cycle review cap).
- **Progress cadence**: for long loops, require a one-to-two-sentence update at each phase change stating one concrete outcome and the next step — no narration of routine tool calls.
- **Verification before done**: name the most relevant validation available and require quoting its output; if validation cannot run, the prompt must require explaining why and naming the next best check.
- **Artifact location**: the loop's own working files — decision log, notes, scratch analysis — are scratch, not product. Tell it to default to `.scratch/` at the repository root, unless the project's or user's instruction files name a different scratch location, and to use `~/.scratch/<project>/` outside a git repo. Real deliverables go wherever the goal contract says.

## Dev Prompt Requirements

The generated prompt must require the goal-loop agent to:

1. Use `workstream-implementer` as the outer controller.
2. Start with a JIRA gate:
   - If a JIRA key is supplied, read and manage that ticket through MCP first, falling back to the REST API only if MCP is unavailable.
   - If no JIRA key is supplied, ask whether to search for a related ticket, create a ticket, create/link a subtask under a parent ticket, or proceed without JIRA.
   - Treat JIRA as optional unless the user chooses ticket-backed work, but make the decision explicit before implementation.
3. Work the task through implementation, verification, PR creation/update, CI, and JIRA review handoff according to `workstream-implementer`. If during contract refinement the task turns out not to be dev work, pause and ask the user instead of forcing the workflow.
4. Run an adversarial review loop after implementation:
   - Use a fresh reviewer on the flagship model tier at `high` reasoning effort (the workhorse setting). Escalate to `xhigh` only when the change is genuinely hard — architectural, concurrent, or security-sensitive. `max`-style settings only if the user explicitly asks.
   - Review the diff against the ticket/task contract, repo conventions, tests, verification evidence, and user constraints.
   - If Critical or Major findings remain, fix them and re-review.
   - Stop after a clean review or 5 review cycles, whichever comes first.
   - Ignore nits unless they reveal correctness, maintainability, security, or performance risk.
5. Run `simplify` when explicitly requested or when the change adds or substantially modifies non-trivial logic, spans multiple modules, or follows an adversarial review fix pass. Skip for trivial one-file changes.
6. Make performance-profile changes explicit when performance matters or the touched path is performance-sensitive.
   - Establish the relevant baseline before changing code when feasible; if not feasible, document why and use the best available comparison.
   - Capture a before/after profile appropriate to the change: latency, throughput, query count, query plan, Big O, memory use, storage footprint, batching/indexing, pipeline runtime, or operational cost.
   - Check for N+1 calls, missing indexes, unbounded reads, unnecessary materialization, poor batching, repeated scans, and algorithm/data-structure mismatches.
   - Surface trade-offs, not just regressions. Examples: "storage increases about 2x to reduce lookup latency", "memory rises for batching", "writes get slower so reads get faster".
   - Pause for explicit user acceptance when a material performance, storage, memory, cost, or complexity trade-off appears. Do not hide trade-offs in the final summary after the decision has already been made.
   - If no measurable performance surface exists, state why.
7. Maintain a decision log at `.scratch/docs/decision-logs/<branch-slug>.md` (or the project's named scratch location), appending each decision at the moment it is made: underspecification choices, deviations from the task contract, symptom-vs-root-cause calls, and trade-offs below the pause threshold in requirement 6. The final summary must include a Decisions section drawn from this log; a bare success claim is not acceptable completion.
8. Verify before declaring completion. Quote the relevant command output or browser evidence in the final summary.

## General Prompt Requirements

The generated prompt must require the goal-loop agent to:

1. Refine the goal contract before producing anything: deliverable, audience, destination, format, acceptance criteria, constraints, non-goals. Confirm the destination (file, doc platform, message) before publishing. If during refinement the goal turns out to be dev work after all, pause and ask the user whether to switch to the dev workstream shape.
2. Do the work with evidence appropriate to the deliverable: cite and date sources for factual claims, exercise flows end-to-end for how-to content, validate numbers with actual computation.
3. Run an adversarial review loop after a draft or result exists:
   - Use a fresh reviewer on the flagship model tier at `high` reasoning effort (the workhorse setting). Escalate to `xhigh` only when the change is genuinely hard — architectural, concurrent, or security-sensitive. `max`-style settings only if the user explicitly asks.
   - Review the deliverable against the goal contract, the evidence gathered, and user constraints.
   - If Critical or Major findings remain, fix them and re-review.
   - Stop after a clean review or 5 review cycles, whichever comes first.
   - Ignore nits unless they affect accuracy, completeness, or usability of the deliverable.
4. Skip code-only gates (simplify, performance profiling, PR/CI). If the work grows a code surface (a script, a pipeline, site config), apply the relevant Dev requirements to that code only.
5. Maintain a decision log at `.scratch/docs/decision-logs/<goal-slug>.md` (or the project's named scratch location), appending each decision at the moment it is made: underspecification choices, deviations from the goal contract, and trade-offs taken without asking. The final summary must include a Decisions section drawn from this log; a bare success claim is not acceptable completion.
6. Verify before declaring completion. Quote the concrete evidence — published URL, produced file path, command output — in the final summary.

## Output Format

Output only one fenced `text` block unless the user asks for explanation. Make the prompt self-contained and directly pasteable.

Dev template:

```text
/goal
You are working on: <task or ticket summary>

Use <workstream-implementer skill> as the outer controller for this work.

JIRA gate:
<ticket-specific or no-ticket instructions>

Autonomy and approvals:
<one boundary, stated once: in-scope local work — reading, editing, running non-destructive verification — proceeds without asking; destructive actions, external writes, material scope expansion, or material trade-offs require confirmation>

Execution:
1. Refine the task contract and acceptance criteria before implementation. If the task turns out not to be dev work, pause and ask.
2. Scope affected repos and check worktree state before branching.
3. Implement the task, keeping changes focused on the approved contract.
4. Run the relevant verification commands and browser checks.
5. Open or update PRs, monitor CI, and update JIRA when applicable.

Adversarial review loop:
<review-loop instructions>

Simplify gate:
<conditional instructions; omit only if user explicitly opts out>

Performance profile gate:
<conditional instructions>

Completion criteria / stop rules:
<what must be true before the loop ends, when to retry vs. fall back vs. ask, and final report requirements including quoted verification evidence and the Decisions section from the decision log>
```

General template:

```text
/goal
You are working on: <goal summary>

Goal contract:
<deliverable, audience, destination, acceptance criteria, constraints, non-goals; confirm destination before publishing. If this turns out to be dev work, pause and ask.>

Autonomy and approvals:
<one boundary, stated once: research, drafting, and local validation proceed without asking; publishing, external writes, and material scope changes require confirmation>

Execution:
<goal-specific steps, including the evidence standard for this deliverable>

Adversarial review loop:
<review-loop instructions scoped to the deliverable and goal contract>

Completion criteria / stop rules:
<what must be true before the loop ends, when to retry vs. fall back vs. ask, concrete verification evidence to quote in the final report, and the Decisions section from the decision log>
```

Collapse empty sections when the user explicitly says they do not apply. In the Dev template, keep the JIRA gate unless the user already explicitly declined JIRA. Do not add workstream-implementer, JIRA, PR, or CI scaffolding to a General prompt.
