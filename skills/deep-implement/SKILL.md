---
name: deep-implement
description: >
  End-to-end workflow for turning a problem statement into a validated proposal and implemented solution.
  Covers discovery (Socratic questioning to uncover root causes), proposal writing, independent validation
  with structured review, implementation planning, and execution with per-task commits and PR creation.
  Also supports review-driven mode: accepts a mega-review report as input, transforms findings into a
  proposal, and implements fixes on the current branch.
  Trigger ONLY when the user explicitly says "deep-implement", "deep implement", or invokes via
  /deep-implement. Do not trigger on general implementation requests — this is a deliberate, heavyweight
  workflow that the user opts into by name.
---

# Deep Implement

A deliberate, multi-phase workflow that turns a problem statement into a validated, implemented solution.
The core insight: users often describe symptoms, not root causes. This skill digs deep before writing code.

## Resumption

Before starting, check for existing work:

1. Look for `docs/plans/*/` directories in the project
2. If found, infer the current phase from which documents exist and their state:
   - Only `proposal.md` exists, no `review-findings.md` → Ready for Phase 2
   - `review-findings.md` exists with unresolved items → In Phase 2b
   - `review-findings.md` has all items resolved → Ready for Phase 2c
   - `implementation-plan.md` exists, no `plan-validation.md` → In Phase 3b (plan needs validation)
   - `plan-validation.md` exists → In Phase 3c (ready to execute)
   - `implementation-plan.md` exists and there are commits beyond the plan commit → Mid-Phase 3c (partial execution). Check git log to identify which tasks have been committed and which remain.
   - All implementation tasks committed, no `final-validation.md` → Ready for Phase 4
   - `final-validation.md` exists with GAPS FOUND → In Phase 4b (gaps need resolution)
   - `final-validation.md` exists with PASS or PASS WITH NOTES, no doc update commits yet → Ready for Phase 4c
   - Doc update commits exist after final-validation → Ready for Phase 5
3. Check if the plan directory name starts with `review-` (e.g., `docs/plans/review-2026-03-16-pr-42-x8k2f/`). If so, this is a **review-driven** session — the proposal was generated from a mega-review report. Look inside `proposal.md` for the original report path.
4. Present a summary: "I found in-progress work for `<feature-name>`. You're at [phase/step]. Continue?" For review-driven sessions: "I found in-progress review-driven work based on mega-review at `<path>`. You're at [phase/step]. Continue?"
5. If the user confirms, pick up from that phase. Read the relevant phase reference file before proceeding.

If no existing work is found, proceed with triage.

## Triage

Every request starts here. Assess the scope before committing to a workflow depth:

**Review-driven** (user provides a path to a mega-review report, e.g., `docs/reviews/*/report.md`):
- Stay on the current branch — no new branch creation. The mega-review was run against this branch (typically an existing PR), so fixes belong here.
- Phase 1 becomes a **transformation step**: a subagent converts the review findings into a `proposal.md` (see Phase 1 reference for details)
- All findings go into the proposal — no scope negotiation, no deferring
- Phase 2 onward: full workflow (validation, implementation planning, execution)
- Phase 5 adjusted: detect existing PR and push fix commits instead of creating a new PR
- Announce: "This is a review-driven implementation — I'll transform the mega-review findings into a proposal. Full workflow from Phase 2 onward."

**Trivial** (typo, one-line fix, obvious bug with clear fix):
- Skip all phases — no branch, no docs, no subagents
- Confirm with the user in 1-2 sentences: "This is a trivial fix — I'll just do it directly. OK?"
- Make the change, commit, push, done

**Small** (clear scope, single file or small change, no architectural decisions needed):
- Create a branch (same naming convention as full workflow)
- Phase 1 abbreviated: 1-2 rounds of clarifying questions, then write a short `proposal.md` (problem + solution + scope, skip the full template)
- Skip Phase 2 entirely
- Phase 3 streamlined: write a brief implementation plan inline in the conversation (no separate doc), execute sequentially in the main thread (no subagents needed), run CI checks, create PR
- Still commit working docs and clean up before PR

**Medium/Large** (multiple files, architectural implications, unclear scope, cross-cutting concerns):
- Full 3-phase workflow as described in the phase reference files

Announce your assessment: "This looks like a [trivial/small/medium/large/review-driven] change. I'll use [no/abbreviated/full/review-driven] workflow. Sound right?"

The user can always override. When in doubt, go deeper — it's cheaper to skip phases than to redo work.

## Phase Overview

| Phase | Purpose | Output |
|-------|---------|--------|
| **1 — Discovery** | Understand the real problem through conversation | `proposal.md` |
| **2 — Validation** | Independent review + structured discussion | Amended `proposal.md` |
| **3 — Implementation** | Plan, validate plan, execute | Working code |
| **4 — Final Validation** | Verify implementation covers all proposal requirements | `final-validation.md` |
| **4c — Doc Reconciliation** | Update project docs and Claude memory made stale by the implementation | Updated docs + memories |
| **5 — PR Creation** | Clean up, rebase, push, open PR | PR URL |

All artifacts go in `docs/plans/<feature-name>/`. The feature name is auto-generated from the problem statement. If the user mentions a JIRA ticket (e.g., CEN-123), incorporate it.

**Phase transitions**: When completing a phase, explicitly announce it ("Phase 1 complete.") and then read the next phase's reference file before proceeding. Don't rely on memory — always load the reference.

## Git Workflow

### Standard mode (trivial/small/medium/large)

At the start of Phase 1 (after triage confirms non-trivial work):

1. Pull latest from the base branch (typically `dev` or `main` — check the project)
2. Ask if this relates to a JIRA ticket
3. Create a branch with appropriate prefix:
   - `feature/<ticket>-<description>` for new features
   - `bugfix/<ticket>-<description>` for bug fixes
   - `refactor/<description>`, `infra/<description>`, `chore/<description>` as appropriate
4. Commit working documents as they're produced (so nothing is lost if the session dies)
5. During Phase 3 execution: one commit per completed task
6. During Phase 4: commit validation findings
7. Before PR creation: rebase onto the latest base branch. If conflicts arise, resolve straightforward ones and escalate complex ones to the user
8. Remove working docs from git tracking (`git rm --cached`), keep local copies, then create PR
9. If CI fails after PR creation: enter a fix cycle (max 3 attempts — see CI Fix Cycle below)

### Review-driven mode

Stay on the current branch — no branch creation. The mega-review was run against this branch (typically an existing PR), so fixes belong here.

1. Commit working documents as they're produced
2. During Phase 3 execution: one commit per completed task
3. During Phase 4: commit validation findings
4. Phase 5: detect existing PR (`gh pr view`). If a PR exists, push fix commits and optionally update the PR description. If no PR exists, create one as normal.
5. If CI fails: same fix cycle as standard mode

### CI Fix Cycle

When CI fails (after PR creation or during local checks):
1. Read the CI output and diagnose the failure
2. Fix the issue and push
3. If it fails again, try a different approach
4. **After 3 failed fix attempts, stop.** Present the full diagnostic to the user: what failed, what you tried, why it didn't work, and your best guess at the root cause. Let the user decide how to proceed.

## Subagent Protocol

This skill relies heavily on subagents (via the Agent tool) to keep work in fresh contexts. Here's how to use them:

### Model tiers for subagents

Match the model to the cognitive demand of the task. Use the `model` parameter on the Agent tool:

| Task type | Model | Rationale |
|-----------|-------|-----------|
| **Phase 1**: Discovery / proposal writing | `opus` | Requires deep analysis and synthesis |
| **Phase 2a**: Proposal review | `opus` | Independent critical evaluation |
| **Phase 2b**: Resolving review findings | `opus` | Requires judgment and design thinking |
| **Phase 3a**: Implementation planning | `opus` | Architectural decisions, task decomposition |
| **Phase 3b**: Plan validation | `opus` | Independent critical evaluation of a plan |
| **Phase 3c**: Task implementation | `opus` | Performance-aware implementation requires experienced-dev judgment — see `references/implementation-agent-protocol.md` |
| **Phase 3c**: Task verification | `sonnet` | Checking implementation against plan — mechanical |
| **Phase 4a**: Final validation (coverage audit) | `opus` | Independent critical evaluation |
| **Phase 4c**: Doc discovery + reconciliation | `opus` | Judgment-heavy: what to update, how much to change |
| **Phase 5**: PR creation, cleanup | `sonnet` | Mechanical git/PR operations |
| Codebase exploration | `sonnet` | Search and retrieval, not judgment |

**The principle:** coming up with a plan, validating a plan, or writing performance-aware implementation requires high brainpower (opus). Mechanical tasks like verification, exploration, and PR creation use sonnet.

### When to spawn a subagent
- Phase 2a: proposal review
- Phase 3a: implementation planning
- Phase 3b: plan validation
- Phase 3c: task implementation and task verification
- Phase 4a: final validation (proposal coverage audit)
- Any time you need codebase exploration without bloating the main conversation

### How to spawn
Use the **Agent tool** with a clear, self-contained prompt. The subagent has no access to your conversation history — everything it needs must be in the prompt. Include:
- The `model` parameter set according to the model tiers table above
- The specific task and expected output format
- Paths to relevant documents (proposal, plan, etc.)
- The project's working directory
- Any constraints or conventions from CLAUDE.md

### Failure handling
- If a subagent returns clearly inadequate output (empty, off-topic, incomplete), **retry once** with a more specific prompt that addresses what went wrong
- If it fails again, do the work yourself in the main thread and move on
- If a subagent's work leaves the codebase in a dirty state (partial changes, broken tests), revert its changes before retrying or escalating
- Always tell the user when a subagent has failed: "The review subagent didn't produce useful results — I'll do the review myself."

### Verification subagents
Per-task verification with a fresh agent is valuable for complex tasks (multi-file changes, architectural modifications, tricky logic). For simple tasks (single-file, small diff, straightforward logic), skip the verification subagent — the CI checks are sufficient.

## Cancellation

If the user wants to stop at any point ("stop", "abandon this", "let's not do this"):
1. Commit any useful work that's been done (don't lose progress)
2. Tell the user what's on the branch and in `docs/plans/<feature-name>/`
3. Ask: "Want me to clean up (delete branch + docs) or leave everything in case you want to resume later?"
4. Act on their choice

## Phase Details

Each phase has detailed instructions in `references/`:

- **Phase 1**: Read `references/phase-1-discovery.md` when entering Phase 1
- **Phase 2**: Read `references/phase-2-validation.md` when entering Phase 2
- **Phase 3**: Read `references/phase-3-implementation.md` when entering Phase 3
- **Phase 4**: Read `references/phase-4-final-validation.md` when entering Phase 4
- **Phase 4c**: Read `references/phase-4c-doc-reconciliation.md` when entering Phase 4c
- **Phase 5**: Read `references/phase-5-pr-creation.md` when entering Phase 5

Read only the phase you're entering — avoid loading all references upfront.

## Cross-Phase Principles

### Fresh Context Pattern
Validation, verification, and implementation tasks use **subagents with fresh context** (see Subagent Protocol above). The main conversation thread acts as the orchestrator — it tracks state, manages transitions, and holds the discussion with the user. Subagents do the heavy lifting and report back.

### Software Design Principles

All implementation work must follow the project's software design guides. These guides are rooted in Ousterhout's *A Philosophy of Software Design* and define how we want code to be structured.

**At the start of every implementation session**, check for design guides in the project:
- `docs/architecture/software-design-guide.md` — language-agnostic principles (deep modules, information hiding, define errors out of existence, strategic vs tactical)
- `docs/architecture/scala-zio-design-guide.md` — ZIO-specific application (when ZLayer is justified, environment type leaks, streams in interfaces)
- `docs/architecture/python-design-guide.md` — Python pipeline application (functions over class hierarchies, integration-first testing)

If these files exist, read the language-agnostic guide and the relevant language-specific guide before Phase 3 planning. Include them in subagent prompts for planning (Phase 3a) and implementation (Phase 3c) — these agents must apply the principles, not just know about them.

**Key principles to enforce during implementation:**
- **Deep modules**: every new module boundary must hide significant complexity. Don't create traits/classes/services for individual pipeline steps — only for genuine module boundaries.
- **Information hiding**: internal types, storage paths, AWS mechanics stay behind the interface. Don't leak implementation details into public signatures.
- **Pull complexity downward**: push complexity into the module, not onto callers.
- **Define errors out of existence**: design interfaces so expected conditions (empty results, optional data) are normal return values, not exceptions.
- **Strategic over tactical**: every change should leave the design at least slightly better. Don't take shortcuts that compound complexity.
- **Integration-first testing**: prefer Testcontainers/LocalStack over mocks. Assert on outcomes, not call chains.

During Phase 2 (validation) and Phase 3b (plan validation), reviewers should check that the proposed design follows these principles. Flag violations as review findings.

### Documentation and Context Gathering
At the start, look for:
- Project-level `CLAUDE.md` for conventions, architecture pointers, and tooling
- Architecture docs referenced in the project (especially `docs/architecture/`)
- Obsidian vault via qmd MCP (if available) — search for prior decisions about the project
- Ask the user: "Are there any architectural docs, design decisions, or other references I should consider?"

### CI Mimicking
Before considering any implementation task complete, figure out what the project's CI does (read CI config files — GitHub Actions, etc.) and run those same checks locally. If no CI config is found, ask the user what checks should pass. At minimum, run the project's linter and test suite if they exist. Do this after every implementation task, not just at the end.
