# Phase 5: Final Validation

All implementation tasks are complete and CI passes. Before creating the PR, verify that the implementation actually delivers everything the proposal promised.

## Why this phase exists

Phase 3.2 validates the **plan** against the proposal. Phase 4 runs quick local checks per task (lint + targeted tests) but deliberately avoids per-task independent verification subagents except for high-risk tasks. Neither catches drift between the proposal and the final implementation — tasks may have been adjusted mid-flight, edge cases may have been dropped, or test coverage may have shifted. **This phase is the primary independent verification gate** — a fresh, comprehensive audit before PR creation.

## Phase 5.1: Proposal Coverage Audit

Launch a **subagent with fresh context** (tier: DEEP — see Capability Tiers in SKILL.md; STANDARD for Small workflows) that receives:
- The amended proposal (`.scratch/docs/plans/<feature-name>/proposal.md`)
- The implementation plan (`.scratch/docs/plans/<feature-name>/implementation-plan.md`)
- The full diff from the base branch (`git diff <base-branch>...HEAD`)
- Access to the codebase (for reading test files and inspecting behavior)

The subagent performs a systematic audit:

### 1. Requirements Checklist

Extract every concrete requirement, behavior, and acceptance criterion from the proposal. For each one:

| Requirement | Implemented? | Tested? | Notes |
|-------------|:---:|:---:|-------|
| _requirement from proposal_ | Yes/No/Partial | Yes/No/Partial | _where in the diff, which test covers it, or what's missing_ |

"Implemented" means the behavior exists in the diff. "Tested" means there is at least one test that exercises and asserts on that behavior — not just that the code is called, but that the outcome is verified.

### 2. Gap Analysis

For any requirement marked No or Partial:
- **Missing implementation**: What specifically wasn't built?
- **Missing test coverage**: What behavior exists but has no test?
- **Partial implementation**: What subset was done, what remains?

### 3. Scope Check

Flag anything in the diff that goes **beyond** the proposal scope — gold-plating, unnecessary refactors, or changes that weren't part of the plan. These aren't necessarily wrong, but should be called out so the user can decide.

### 4. Verdict

One of:
- **PASS** — all proposal requirements are implemented and tested. Ready for PR.
- **PASS WITH NOTES** — all requirements covered, but there are minor observations (scope additions, alternative approaches taken). List them. Ready for PR unless the user objects.
- **GAPS FOUND** — concrete gaps exist. List them with severity (critical vs. nice-to-have).

Write findings to `.scratch/docs/plans/<feature-name>/final-validation.md`. Commit.
Alongside the verdict, the orchestrator reviews `decisions.md` (next to `status.md`, if present) and surfaces entries worth user attention with the validation results.
Update `status.md` to `Current phase: 5`, `Current step: 5.1-validation-complete`, and `Next action` based on the verdict.

## Phase 5.2: Address Gaps (if any)

If the validation subagent returns **GAPS FOUND**:

1. Present the gaps to the user with clear context:
   - What's missing
   - Estimated effort to fix
   - Whether each gap is critical (proposal requirement not met) or minor (test coverage could be stronger)
2. Let the user decide for each gap:
   - **Fix it** — implement the missing piece (spawn a subagent, same protocol as Phase 4 tasks)
   - **Accept as-is** — the user consciously decides to ship without it
   - **Descope** — remove from proposal scope (note this in the PR description)
3. After fixes, re-run CI checks
4. If fixes were substantial (not just adding a test), **re-run Phase 5.1** to verify the fixes didn't introduce new gaps. Cap at 2 validation rounds — if gaps persist after 2 rounds, present the remaining issues to the user and let them decide.
5. Update `status.md` after each gap decision and after each validation rerun

If the verdict was **PASS** or **PASS WITH NOTES**, proceed to Phase 6 so project documentation and local knowledge artifacts can be reconciled before PR creation.

## Subagent Prompt Template

The validation subagent should receive a prompt like:

> You are reviewing a completed implementation against its original proposal.
>
> **Proposal**: Read `.scratch/docs/plans/<feature-name>/proposal.md`
> **Implementation plan**: Read `.scratch/docs/plans/<feature-name>/implementation-plan.md`
> **Full diff**: Run `git diff <base-branch>...HEAD`
> **Codebase access**: Full read access to all files
>
> Your task:
> 1. Extract every requirement and acceptance criterion from the proposal
> 2. For each one, check: (a) is it implemented in the diff? (b) is it tested?
> 3. Flag anything in the diff that exceeds proposal scope
> 4. Write your findings to `.scratch/docs/plans/<feature-name>/final-validation.md` using the format described in the phase reference
> 5. End with a verdict: PASS, PASS WITH NOTES, or GAPS FOUND
>
> Be thorough but fair — minor naming differences or slightly different approaches that achieve the same outcome are fine. Focus on behavioral gaps, not stylistic ones.
