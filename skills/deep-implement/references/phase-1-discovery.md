# Phase 1: Discovery

The goal is to understand what the user **really** needs, not just what they initially asked for. Users often describe symptoms — your job is to find the root cause and the right scope of change.

## Starting the Conversation

Begin by understanding the problem statement. Then dig deeper:

- **What triggered this?** What happened that made the user think about this change?
- **What's the impact?** Who is affected? How severe is it? Is there urgency?
- **What has been tried?** Has anyone attempted to solve this before? What happened?
- **What are the constraints?** Time, backward compatibility, dependencies on other teams?
- **What does success look like?** How will the user know this is done correctly?

Don't ask all of these at once — have a natural conversation. Follow the threads that seem most productive.

## Exploration

You're not limited to just asking the user questions. Use subagents to:

- Explore the codebase — understand the current implementation, find related code
- Check git history — what changed recently? Who changed it? Why?
- Run tests — does the current test suite reveal anything about the problem?
- Check dependencies — are there version constraints or conflicts?
- Search online — if the problem involves external libraries or services, look up docs
- Search the project's knowledge base or notes system, if available, for prior decisions

Share your findings with the user as you go. "I looked at the code and found X — this makes me think the issue might actually be Y. What do you think?"

## Checkpoints

Every 3 rounds of back-and-forth, pause and assess:

1. Summarize your current understanding of the problem and proposed solution
2. Evaluate whether you have enough information to write a solid proposal
3. If yes: "I think I have a good understanding now. Ready to write the proposal?"
4. If no: "I'd like to dig into [specific area] a bit more before we proceed. Here's why..."

The user can always say "enough discussion, write it up" to skip ahead, or "keep going" to continue exploring.

## Context Gathering

Before writing the proposal, make sure you've considered:

- Architectural docs referenced in CLAUDE.md or the project
- Relevant entries in the project's knowledge base or notes system, if available
- Ask the user directly: "Are there any design docs, past decisions, or other context I should factor in?"

## Writing the Proposal

When it's time to write (either the user says so or you've reached natural completion), create:

```
docs/plans/<feature-name>/proposal.md
```

Also create or update:

```
docs/plans/<feature-name>/status.md
```

The feature name should be a short, descriptive slug derived from the problem (e.g., `refactor-matching-pipeline`, `fix-geocoder-timeout`). If there's a JIRA ticket, include it (e.g., `CEN-123-refactor-matching-pipeline`).

### Proposal Structure

```markdown
# <Title>

## Problem Statement
What's wrong or what needs to change, and why it matters.
Include the root cause if it differs from the initial symptom.

## Context
- Current state of the codebase relevant to this change
- Prior decisions or constraints that affect the approach
- Links to relevant docs, tickets, or conversations

## Proposed Solution
What will change and how. Be specific enough that someone unfamiliar with the
conversation could understand the approach, but don't go to implementation-level
detail — that's Phase 3's job.

### Approach
High-level description of the approach.

### Scope
What's in scope and — equally important — what's explicitly out of scope.

### Key Decisions
Any significant design decisions made during discovery, with rationale.

## Impact
- Files/modules affected (approximate)
- Risk areas
- Backward compatibility considerations
- Testing implications

## Open Questions
Anything that came up during discovery that wasn't fully resolved.
These will be picked up during Phase 2 validation.
```

After writing the proposal, commit it to the branch and tell the user Phase 1 is complete.
Set `Current phase` to `1`, `Current step` to `1-complete`, and `Next action` to `Start Phase 2.1 review`.

## Review-Driven Mode (alternate Phase 1)

When triage identifies a **review-driven** request (user provides a mega-review report path), Phase 1 skips Socratic discovery and instead transforms the review findings into a proposal.

### Input

The mega-review `report.md` — contains findings across 8 dimensions, calibration results, architectural tensions, and dimension summaries.

### Transformation

Launch a **subagent with fresh context** (model: `opus`) that receives:
- The mega-review report path
- Access to the full codebase
- Project conventions from CLAUDE.md

This is a one-shot artifact-producing agent. Expect it to take time; do not replace it locally because it's running long.

The subagent reads the report and the relevant code, then produces `docs/plans/<name>/proposal.md` in the standard proposal format:

- **Problem Statement** — synthesized from the executive summary and architectural tensions. Write a narrative ("The codebase has X structural issues that manifest as Y problems"), not a list of findings.
- **Context** — pulled from the review's scope, dimension summaries, and the code itself.
- **Proposed Solution** — derived from the findings' suggestions and tension resolutions. Organized by theme, not by finding ID. Cross-reference back to finding IDs (e.g., `[CQ-3]`, `[AR-1]`, `[T-1]`) for traceability.
- **Scope** — all findings from the report. Explicitly state: "All N findings from mega-review report at `<path>`."
- **Key Decisions** — any non-obvious choices the subagent made when synthesizing (e.g., grouping related findings, choosing one suggestion over another when findings had conflicting recommendations).
- **Impact** — files/modules affected, risk areas.
- **Open Questions** — cases where findings had conflicting suggestions, or where the fix approach isn't clear from the review alone.

Add a metadata line at the top of the proposal:

```markdown
> **Source:** Review-driven — generated from mega-review report at `<report-path>`
```

### Plan directory naming

Use `review-` prefix followed by the review directory name:
```
docs/plans/review-2026-03-16-pr-42-x8k2f/proposal.md
```

### After transformation

Present the proposal to the user for review and approval, same as standard Phase 1. The user may adjust priorities or approach before proceeding to Phase 2, but all findings remain in scope by default. Any descoping must happen explicitly during validation with rationale recorded in `review-findings.md` and the amended proposal.

Commit the proposal and announce Phase 1 complete.
Update `status.md` for the review-driven session the same way as standard Phase 1.
