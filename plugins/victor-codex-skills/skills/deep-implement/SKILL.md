---
name: deep-implement
description: >
  Heavyweight end-to-end workflow: problem statement through Socratic discovery, written
  proposal, independent validation, implementation plan, per-task commits and PR. Also
  accepts a mega-review report as input and implements the fixes on the current branch.
  Trigger only when the user explicitly says "deep-implement" or invokes $deep-implement —
  not on ordinary implementation requests.
---

# Deep Implement

A deliberate, multi-phase workflow that turns a problem statement into a validated, implemented solution.
The core insight: users often describe symptoms, not root causes. This skill digs deep before writing code.

**Artifact location.** Everything this skill writes is scratch, not product. Default to `.scratch/` at the repository root (`git rev-parse --show-toplevel`), unless the project's or user's instruction files (`AGENTS.md`, `CLAUDE.md`, or equivalent) name a different scratch location — those win. Outside a git repo, use `~/.scratch/<project>/`. Paths below assume the default.

## Resumption

Before starting, check for existing work:

1. Look for `.scratch/docs/plans/*/` directories in the project
2. If found, prefer `.scratch/docs/plans/<feature-name>/status.md` as the source of truth for the current phase and next action. This file should be updated whenever the workflow advances.
3. If `status.md` is missing, fall back to inference from which documents exist and their state:
   - Only `proposal.md` exists, no `review-findings.md` → Ready for Phase 2
   - `review-findings.md` exists with unresolved items → In Phase 2.2
   - `review-findings.md` has all items resolved → Ready for Phase 3
   - `implementation-plan.md` exists, no `plan-validation.md` → In Phase 3.2 (plan needs validation)
   - `plan-validation.md` exists, no implementation commits yet → Ready for Phase 4
   - `implementation-plan.md` exists and there are commits beyond the plan commit → Mid-Phase 4 (partial execution). Check git log to identify which tasks have been committed and which remain.
   - All implementation tasks committed, no `final-validation.md` → Ready for Phase 5
   - `final-validation.md` exists with GAPS FOUND → In Phase 5.2 (gaps need resolution)
   - `final-validation.md` exists with PASS or PASS WITH NOTES, no doc reconciliation recorded yet → Ready for Phase 6
   - Doc reconciliation complete → Ready for Phase 7
4. Check if the plan directory name starts with `review-` (e.g., `.scratch/docs/plans/review-2026-03-16-pr-42-x8k2f/`). If so, this is a **review-driven** session — the proposal was generated from a mega-review report. Look inside `proposal.md` for the original report path.
5. Present a summary: "I found in-progress work for `<feature-name>`. You're at [phase/step]. Continue?" For review-driven sessions: "I found in-progress review-driven work based on mega-review at `<path>`. You're at [phase/step]. Continue?"
6. If the user confirms, pick up from that phase. Read the relevant phase reference file before proceeding.

If no existing work is found, proceed with triage.

## Triage

Every request starts here. Assess the scope before committing to a workflow depth:

**Review-driven** (user provides a path to a mega-review report, e.g., `.scratch/docs/reviews/*/report.md`):
- Stay on the current branch — no new branch creation. The mega-review was run against this branch (typically an existing PR), so fixes belong here.
- Phase 1 becomes a **transformation step**: a subagent converts the review findings into a `proposal.md` (see the Phase 1 reference for details)
- All findings go into the proposal by default. Reprioritization or descoping is allowed only explicitly during validation, and the rationale must be recorded in the review findings and amended proposal.
- Phase 2 onward: full workflow (proposal validation, implementation planning, execution, final validation, documentation reconciliation, PR update/creation)
- Phase 7 adjusted: detect existing PR and push fix commits instead of creating a new PR
- Announce: "This is a review-driven implementation — I'll transform the mega-review findings into a proposal. Full workflow from Phase 2 onward."

**Trivial** (typo, one-line fix, obvious bug with clear fix):
- Skip all phases — no branch, no docs, no subagents
- Confirm with the user in 1-2 sentences: "This is a trivial fix — I'll just do it directly. OK?"
- Make the change, commit, push, done

**Small** (clear scope, single file or small change, no architectural decisions needed):
- Create a branch (same naming convention as full workflow)
- Phase 1 abbreviated: 1-2 rounds of clarifying questions, then write a short `proposal.md` (problem + solution + scope, skip the full template)
- Skip Phase 2 entirely
- Phase 3 streamlined: write a brief implementation plan inline in the conversation (no separate doc), then execute Phase 4 entirely inline (all tasks `inline` mode — skip Phase 4.0 formalities if obvious), run CI checks, and create the PR in Phase 7
- Still commit working docs and clean up before PR

**Medium/Large** (multiple files, architectural implications, unclear scope, cross-cutting concerns):
- Full workflow as described in the phase reference files

Announce your assessment: "This looks like a [trivial/small/medium/large/review-driven] change. I'll use [no/abbreviated/full/review-driven] workflow. Sound right?"

The user can always override. **When in doubt, go lighter.** A small workflow that produces working code in 30 minutes beats a medium workflow that produces a perfect proposal in 3 hours. You can always escalate if a Small turns out to need design work; you cannot recover time spent on phases that weren't needed.

Prefer **Trivial → Small → Medium → Large**, in that order, and only escalate when clear need emerges.

## Phase Overview

| Phase | Purpose | Output |
|-------|---------|--------|
| **1 — Discovery** | Understand the real problem through conversation | `proposal.md` |
| **2 — Proposal Validation** | Independent review + structured discussion | Amended `proposal.md` |
| **3 — Implementation Planning** | Plan and validate the plan | `implementation-plan.md`, `plan-validation.md` |
| **4 — Implementation** | Execute the validated plan | Working code |
| **5 — Final Validation** | Verify implementation covers all proposal requirements | `final-validation.md` |
| **6 — Documentation Reconciliation** | Update project docs and local knowledge artifacts made stale by the implementation | Updated docs + knowledge artifacts |
| **7 — PR Creation** | Clean up, rebase, push, open PR | PR URL |

All artifacts go in `.scratch/docs/plans/<feature-name>/`. The feature name is auto-generated from the problem statement. If the user mentions a JIRA ticket (e.g., CEN-123), incorporate it.

**Phase transitions**: When completing a phase, explicitly announce it ("Phase 1 complete.") and then read the next phase's reference file before proceeding. Don't rely on memory — always load the reference. Update `.scratch/docs/plans/<feature-name>/status.md` at the same time so resumption does not depend on fragile heuristics.

## Execution Notes

- **Model/effort selection**: Every subagent spawn is a cost decision. Pick the cheapest capability tier that is plausibly adequate (see Capability Tiers in the Subagent Protocol) and escalate only on evidence. Do not default to the strongest model or maximum effort out of caution.
- **Parallel subagents**: Spawn multiple subagents in the same turn when the orchestration plan assigns independent tasks to subagents (e.g., parallel implementation, parallel file exploration). Do not spawn a subagent for work you can complete directly in a single response.
- **Parallel tool calls**: When reading multiple files or running independent searches, make all tool calls in parallel.
- **Literal scope**: Be explicit about where instructions apply (e.g., "Apply this pattern to *every* new module, not just the first one").
- **Minimalism guardrail**: Avoid adding unnecessary abstractions, extra files, or defensive boilerplate. Keep solutions simple and focused: only add helpers/abstractions that hide meaningful complexity; don't add error handling for impossible scenarios; don't create extra config or utilities "just in case."
- **Task packaging**: In the first turn, provide the full problem statement, intent, constraints, acceptance criteria, and relevant file locations. Avoid dribbling requirements across turns—each user turn adds reasoning overhead.
- **Context hygiene**: Use subagents for codebase exploration and for implementation tasks that genuinely need fresh context or parallelization (per the Phase 4.0 orchestration plan). Default to inline implementation. The main thread orchestrates; heavy tool output should live in subagent contexts when offloaded.
- **Subagent mental test**: Before spawning a subagent, ask "Will I need this tool output again, or just the conclusion?" If only the conclusion matters, have the subagent return a concise summary and keep the raw tool noise in its own context. If you'll need to reference detailed output repeatedly, write it to disk and pass the file path forward.
- **Subagent prompt structure**: When feeding large documents (proposals, plans, design guides) to subagents, put the longform documents near the top of the prompt and the specific task/query at the end.
- **Subagent prompt hygiene**: state the outcome, success criteria, constraints, and stop conditions once. Strong reasoning models follow prompt contracts closely — do not repeat rules for emphasis; duplicated or contradictory rules destabilize behavior more than missing detail.
- **Proactive checkpointing**: If a phase involves extensive exploration or many tool calls, save progress to `status.md` or the relevant artifact mid-phase. Do not wait until the phase is complete to checkpoint. This prevents loss of state if context compacts or the session is interrupted.

### Status File

Maintain this file for every non-trivial session:

```
.scratch/docs/plans/<feature-name>/status.md
```

Suggested structure:

```markdown
# Workflow Status: <Feature Name>

- Mode: standard / review-driven
- Current phase: 1 / 2 / 3 / 4 / 5 / 6 / 7
- Current step: short label such as `2.2-discussing-finding-3`
- Base branch: `<base branch>`
- Next action: one sentence
- Last updated: YYYY-MM-DD HH:MM TZ
```

Update it whenever the workflow advances, when a task starts or completes, and whenever the next action changes materially.

Create it as soon as a non-trivial session has a plan directory. Treat it as workflow state, not as an optional note.

## Git Workflow

### Standard mode (trivial/small/medium/large)

At the start of Phase 1 (after triage confirms non-trivial work):

1. Identify the base branch from repository instructions or git history (commonly `dev` or `main`)
2. Ask if this relates to a JIRA ticket
3. Create a branch with appropriate prefix:
   - `feature/<ticket>-<description>` for new features
   - `bugfix/<ticket>-<description>` for bug fixes
   - `refactor/<description>`, `infra/<description>`, `chore/<description>` as appropriate
4. Commit working documents as they're produced (so nothing is lost if the session dies)
5. During Phase 4 execution: one commit per completed task
6. During Phase 5: commit validation findings
7. Before PR creation: rebase onto the latest base branch. If conflicts arise, resolve straightforward ones and escalate complex ones to the user
8. Decide whether working docs should stay in the PR or remain local-only based on repository norms and user preference. If they should stay local-only, remove them from git tracking (`git rm --cached`) before PR creation; otherwise keep them in the branch.
9. If CI fails after PR creation: enter a fix cycle (max 3 attempts — see CI Fix Cycle below)

### Review-driven mode

Stay on the current branch — no branch creation. The mega-review was run against this branch (typically an existing PR), so fixes belong here.

1. Commit working documents as they're produced
2. During Phase 4 execution: one commit per completed task
3. During Phase 5: commit validation findings
4. Phase 7: detect existing PR (`gh pr view`). If a PR exists, push fix commits and optionally update the PR description. If no PR exists, create one as normal.
5. If CI fails: same fix cycle as standard mode

### CI Fix Cycle

When CI fails (after PR creation or during local checks):
1. Read the CI output and diagnose the failure
2. Fix the issue and push
3. If it fails again, try a different approach
4. **After 3 failed fix attempts, stop.** Present the full diagnostic to the user: what failed, what you tried, why it didn't work, and your best guess at the root cause. Let the user decide how to proceed.

## Subagent Protocol

This skill relies heavily on subagents to keep work in fresh contexts. Here's how to use them:

### Capability tiers

Model and effort selection is deliberately harness-agnostic. Harnesses typically expose two levers — a **model tier** (frontier / mid / fast model families) and a **reasoning effort** (thinking budget: e.g. xhigh/high/medium/low). Provider lineups and parameter names change over time; what stays constant is the *relative* capability ladder. This skill uses three abstract tiers — map each to whatever your harness currently offers, using either lever or both:

- **DEEP** — the strongest reasoning you can get: frontier-tier model and/or maximum thinking effort. For open-ended synthesis, root-cause analysis, architectural decisions, and high-stakes audits where a missed insight costs far more than the tokens.
- **STANDARD** — a capable general model at moderate effort. For well-framed judgment: implementing from an explicit spec, applying agreed decisions, updating docs.
- **LIGHT** — the cheapest/fastest adequate option: a small model and/or minimal effort. For search and retrieval, mechanical verification against explicit criteria, and structured git/PR operations.

Illustrative mappings (**snapshots only — likely outdated; always map to the current lineup, not these names**): on OpenAI/Codex-style lineups (GPT-5.6-era: Sol/Terra/Luna tiers × low/medium/high/xhigh/max efforts): DEEP ≈ the flagship tier (Sol-class) at `high` — the workhorse setting — escalating to `xhigh` only when a step genuinely needs deep thought; STANDARD ≈ flagship at `medium` or mid tier (Terra-class, roughly previous-flagship-competitive at lower cost) at `high`; LIGHT ≈ mid tier at low/medium, or the smallest tier (Luna-class, nano-equivalent) for genuinely trivial retrieval and mechanical steps. `max`-style settings are never a default at any tier — use only on explicit user request or as a single retry after a demonstrated `xhigh` failure. On Anthropic-style lineups, DEEP ≈ Opus/Fable-class or a frontier model at high thinking, STANDARD ≈ Sonnet-class, LIGHT ≈ Haiku-class. When a new generation ships with new tier names, apply the same relative mapping.

**Selection discipline** — before every spawn:

1. Pick the cheapest tier plausibly adequate for the task, using the defaults table below as a starting point.
2. State the choice in one line when spawning ("STANDARD — task spec is explicit, no design decisions left").
3. Escalate one tier on evidence: ambiguity discovered mid-task, a failed or inadequate attempt, or high blast radius (auth, data migrations, public API contracts, concurrency). Never retry a failed subagent at the same tier with the same prompt.
4. Condition on triage size: the defaults below assume a Medium/Large workflow. For **Small** workflows, drop judgment tasks one tier (DEEP → STANDARD). Trivial workflows use no subagents at all.

| Task type | Default tier | Rationale |
|-----------|--------------|-----------|
| **Phase 1**: Discovery / proposal writing | DEEP | Root-cause analysis and proposal synthesis drive the rest of the workflow |
| **Phase 2.1**: Proposal review | DEEP | Independent critical evaluation should be as sharp as possible |
| **Phase 2.2**: Resolving review findings | DEEP | Structured judgment and trade-off analysis |
| **Phase 2.3**: Amending the proposal | STANDARD | Applying already-agreed decisions to a document |
| **Phase 3.1**: Implementation planning | DEEP | Architectural decisions and task decomposition benefit from maximum reasoning depth |
| **Phase 3.2**: Plan validation | DEEP | Catching plan gaps early is high leverage |
| **Phase 4**: Task implementation (subagent mode only) | STANDARD | Inline is the default — no subagent tier applies. When a task is assigned to a subagent: plan is explicit, so execution rarely needs more. Well-specified, low-risk tasks can drop to LIGHT; use DEEP only for tasks the plan flags as tricky (architectural, concurrency, performance-critical) |
| **Phase 4**: Per-task verification | — (inline) | Local lint + targeted tests run inline by whoever implemented the task. Independent verification subagent (STANDARD) only for plan-flagged high-risk tasks |
| **Phase 5.1**: Final validation audit | DEEP | Proposal-to-implementation coverage review is a high-stakes audit |
| **Phase 6**: Doc discovery | LIGHT | Search and grep for docs referencing what changed |
| **Phase 6**: Doc reconciliation | STANDARD | Framed judgment: the proposal and diff define what changed; the task is mapping that onto existing docs |
| **Phase 7**: PR creation, cleanup | LIGHT | Structured git and PR operations |
| Codebase exploration | LIGHT | Search and retrieval, not judgment |

**The principle:** the economics of this workflow are expensive-planning, cheap-execution. Spend DEEP where a missed insight compounds downstream (discovery, planning, validation, audit); everything else starts as cheap as plausible and earns an upgrade only by demonstrated need.

### When to spawn a subagent
- Phase 2.1: proposal review
- Phase 3.1: implementation planning
- Phase 3.2: plan validation
- Phase 4: only per the Phase 4.0 orchestration plan — subagent mode for tasks that need fresh context, parallelization, or DEEP-tier reasoning; independent verification subagent only for plan-flagged high-risk tasks
- Phase 5.1: final validation (proposal coverage audit — primary independent verification gate)
- Any time you need codebase exploration without bloating the main conversation

**Default for Phase 4 is inline.** Do not spawn an implementation subagent unless the orchestration plan assigns one with a stated reason.

### How to spawn
Spawn a subagent with a clear, self-contained prompt. The subagent has no access to your conversation history — everything it needs must be in the prompt. Include:
- The model/effort parameters set according to the tier chosen via the Capability Tiers section above (state the tier and the one-line justification)
- The specific task and expected output format
- Paths to relevant documents (proposal, plan, etc.)
- The project's working directory
- Any constraints or conventions from the repository instruction files (`AGENTS.md`, `CLAUDE.md`, or similar)

If the harness does not support subagents, perform the same phase locally in the main thread and preserve the same artifacts and review boundaries.

### Waiting and progress policy
- Once a subagent owns a substantive task, do not duplicate that task in the main thread just because the result is taking time.
- Prefer to use the waiting time for non-overlapping orchestration work: status updates, reading the next phase reference, preparing commit messages, or gathering adjacent context that does not redo the delegated task.
- If you are blocked on the result, use `wait_agent` generously before escalating:
  - DEEP planning, review, and audit tasks: expect long runtimes; wait in roughly 10-15 minute windows
  - STANDARD implementation, proposal amendment, and doc-reconciliation tasks: wait in roughly 5-10 minute windows
  - LIGHT verification, exploration, and cleanup tasks: wait in roughly 3-5 minute windows
- A `wait_agent` timeout is not a failure signal. Treat it as "still in progress" unless you have explicit evidence of failure.
- Do not infer idleness from silence. In the current harness, completion is observable, but true heartbeat-style progress reporting may not be available.
- If a task is materially overdue and you genuinely need clarification, you may send one short non-interrupting follow-up with `send_input`. Do not spam status pings; routine polling is worse than waiting.
- Only interrupt, re-prompt, or take the task back locally when one of these is true:
  - the subagent returned an explicit error
  - the subagent completed with unusable output
  - the delegated task became invalid because the plan or user decision changed
  - the user explicitly asks you to stop waiting and proceed differently

### Agent lifecycle and cleanup
- Close one-shot agents with `close_agent` after their result has been integrated or deliberately discarded. This includes proposal transformation, proposal review, proposal amendment, implementation planning, plan validation, final validation, doc discovery, doc updates, and verification-only agents.
- Keep implementation agents open only while there is a concrete expectation of immediate follow-up on the same task. If the task is committed and no direct follow-up is pending, close the agent.
- If you retry a failed delegated task, close the failed agent before spawning the replacement unless you still need its logs for immediate diagnosis.
- Do not accumulate completed idle agents. Cleanup is part of orchestration, not optional polish.

### Failure handling
- If a wait window expires and the subagent has not finished, keep waiting or do adjacent work. Do not treat elapsed time alone as grounds to redo the task yourself.
- If a subagent returns clearly inadequate output (empty, off-topic, incomplete), **retry once** with a more specific prompt that addresses what went wrong
- If it fails again, do the work yourself in the main thread and move on
- If a subagent returns partial work or a broken patch, discard that result before retrying or escalating
- Close failed or discarded agents once you've decided not to use their output
- Always tell the user when a subagent has failed: "The review subagent didn't produce useful results — I'll do the review myself."

### Verification
- **Per task (Phase 4)**: run local checks inline — linter + tests from the task's Verification section. No verification subagent by default.
- **High-risk tasks only**: spawn an independent verification subagent when the plan flags a task as high-risk (auth, migrations, concurrency, public API contracts).
- **End of Phase 4**: full CI-equivalent suite.
- **Phase 5**: fresh DEEP subagent performs the proposal coverage audit — the comprehensive independent check before PR creation.

## Cancellation

If the user wants to stop at any point ("stop", "abandon this", "let's not do this"):
1. Commit any useful work that's been done (don't lose progress)
2. Tell the user what's on the branch and in `.scratch/docs/plans/<feature-name>/`
3. Ask: "Want me to clean up (delete branch + docs) or leave everything in case you want to resume later?"
4. Act on their choice

## Phase Details

Each phase has detailed instructions in `references/`:

- **Phase 1**: Read `references/phase-1-discovery.md` when entering Phase 1
- **Phase 2**: Read `references/phase-2-validation.md` when entering Phase 2
- **Phase 3**: Read `references/phase-3-implementation-planning.md` when entering Phase 3
- **Phase 4**: Read `references/phase-4-implementation.md` when entering Phase 4
- **Phase 5**: Read `references/phase-5-final-validation.md` when entering Phase 5
- **Phase 6**: Read `references/phase-6-doc-reconciliation.md` when entering Phase 6
- **Phase 7**: Read `references/phase-7-pr-creation.md` when entering Phase 7

Read only the phase you're entering — avoid loading all references upfront.

## Cross-Phase Principles

### Fresh Context Pattern
Planning, validation, and audit steps use **subagents with fresh context** (see Subagent Protocol above). Phase 4 implementation defaults to **inline** in the main thread; subagents are assigned only via the Phase 4.0 orchestration plan when fresh context or parallelization genuinely helps. The main conversation thread acts as the orchestrator — it plans execution, implements inline tasks directly, delegates only what earns a spawn, tracks state, waits patiently, manages transitions, closes completed agents, and holds the discussion with the user.

### Software Design Principles

All implementation work must follow the project's software design guides, if it has any. The defaults below are rooted in Ousterhout's *A Philosophy of Software Design*.

**At the start of every implementation session**, check for design guides in the project (commonly under `docs/architecture/` — e.g. a language-agnostic `software-design-guide.md` plus language-specific guides). If they exist, read the language-agnostic guide and the guide for the language being changed before Phase 3 planning. Include them in subagent prompts for planning (Phase 3.1) and implementation (Phase 4) — these agents must apply the principles, not just know about them.

**Key principles to enforce during implementation:**
- **Deep modules**: every new module boundary must hide significant complexity. Don't create classes/services/traits for individual processing steps — only for genuine module boundaries.
- **Information hiding**: internal types, storage paths, infrastructure mechanics stay behind the interface. Don't leak implementation details into public signatures.
- **Pull complexity downward**: push complexity into the module, not onto callers.
- **Define errors out of existence**: design interfaces so expected conditions (empty results, optional data) are normal return values, not exceptions.
- **Strategic over tactical**: every change should leave the design at least slightly better. Don't take shortcuts that compound complexity. **But: small, isolated tactical fixes are not the same as compounding shortcuts.** A one-line bugfix that doesn't touch the surrounding design is fine. Strategic effort is reserved for places where the design is actively in your way.
- **Integration-first testing**: prefer real dependencies (containers, local emulators) over mocks where the project supports it. Assert on outcomes, not call chains.
- **Minimalism / anti-overengineering**: do not create helpers, utilities, or abstractions for one-time operations. Don't add error handling for scenarios that can't happen. Don't design for hypothetical future requirements. The right amount of complexity is the minimum needed for the current task.

During Phase 2 (validation) and Phase 3.2 (plan validation), reviewers should check that the proposed design follows these principles. Flag violations as review findings.

### Documentation and Context Gathering
At the start, look for:
- Project-level instruction files such as `AGENTS.md`, `CLAUDE.md`, or equivalent for conventions, architecture pointers, and tooling
- Architecture docs referenced in the project (especially `docs/architecture/`)
- project knowledge base or notes system (if available) - search for prior decisions about the project
- Ask the user: "Are there any architectural docs, design decisions, or other references I should consider?"

### CI Mimicking
Before considering any implementation task complete, figure out what the project's CI does by reading its CI configuration if available (GitHub Actions, other CI systems, or repo scripts) and encode those checks into the implementation plan.

Validation cadence:
- After every task, run the task-local checks listed in that task's verification section
- After each wave, run a broader CI subset if the wave touched shared infrastructure, core abstractions, or multiple modules
- Always run the full CI-equivalent suite once at the end of Phase 4, and again after any substantial Phase 5.2 gap-fix work

If no CI config is found, ask the user what checks should pass. At minimum, run the project's linter and test suite if they exist.
