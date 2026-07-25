---
name: plan-codex-review
description: >
  Three-phase pipeline: Claude plans in forced plan mode with a relentless requirements
  interview and cheap exploration subagents, Codex implements via the openai-codex plugin,
  then a fresh-context Claude review produces a Codex-ready remediation plan. Claude Code
  only — requires the Agent tool and the codex plugin. Trigger only when the user explicitly
  says "plan-codex-review" or invokes /plan-codex-review.
---

# Plan / Codex / Review

A three-phase pipeline for substantial coding tasks:

1. **Plan** — Claude (session model, deep thinking) switches into plan mode, explores the codebase via cheap subagents, interviews the user relentlessly until shared understanding, and presents an implementation plan following plan-mode conventions. User approves via the plan-mode gate before any code is written.
2. **Implement** — Codex executes the approved plan (`gpt-5.6`, `high` effort, write-capable).
3. **Review** — a fresh-context Claude (Fable, max thinking) subagent judges the diff against the plan and produces severity-ranked findings plus a Codex-ready remediation plan. The user then chooses: stop, remediate (`gpt-5.6`, `xhigh` effort), or remediate and re-review (loop).

The division of labor is deliberate: Claude does the judgment-heavy ends (planning, reviewing), Codex does the implementation middle, and exploration is pushed to cheap models so top-tier tokens are spent only on reasoning.

## Execution Notes

- **Response length**: The interview is the value here, not commentary around it. Questions come batched with your recommended answer; the Phase 2 return is a one-paragraph summary; the Phase 3 gate is the findings summary and nothing more. Written output runs longer than these formats want by default, and lowering reasoning effort does not reliably shorten it.
- **Scope and completion**: The approved plan is the contract. Do not add work Codex was not asked to do, and do not quietly drop plan items. Report a phase complete only when it actually is — if Codex produced a partial diff, say which plan items are unimplemented rather than summarizing around the gap.
- **Delegation**: Exploration subagents are the only spawns this skill makes outside its three named phases. Do not improvise extra reviewers — Phase 3 is the review mechanism. Keep concurrent explorers in single digits.
- **Corrections**: Only flag an earlier statement when the error changes the plan, the diff, or a decision the user already made. State it plainly and continue — a review finding against your own plan is expected and needs no commentary beyond the remediation entry.

## Prerequisites (check before Phase 1)

1. **Task description.** If the user invoked the skill without one, ask what to build. Do not proceed on a guess.
2. **Codex plugin availability.** Verify the codex companion is functional — the `codex:codex-rescue` subagent must exist and the Codex CLI must be authenticated. If a Codex invocation later reports the CLI is missing or unauthenticated, stop and tell the user to run `/codex:setup`. Do not silently fall back to implementing in the main thread.
3. **Git state.** Record the baseline: `git rev-parse HEAD` and `git status --porcelain`. The review phase is diff-based, so a dirty working tree contaminates it. If the tree is dirty, warn the user and recommend committing or stashing first. If they choose to proceed anyway, record the pre-existing dirty paths and instruct the reviewer to ignore them.
4. **Not a git repo?** Warn that the review will be plan-scoped (reading the files the plan names) instead of diff-based, and confirm the user wants to continue.

## Artifacts

**The implementation plan is not written to disk.** It follows plan-mode conventions: presented for approval via the plan-mode gate and kept in-conversation. Phase 2 inlines its full contents into the Codex prompt, so no file is needed. (Exception: if the user explicitly asks for a persisted copy, write it to a location of their choosing after plan approval.)

**Artifact location.** This skill writes scratch, not product. Everything goes under `.scratch/` at the repo root (`~/.scratch/<project>/` outside one); a scratch path named in `AGENTS.md` / `CLAUDE.md` wins. Paths below assume the default.

Review artifacts live in `.scratch/docs/plan/` inside the current working directory, named from a short kebab-case slug of the task plus the date:

| Artifact | Path |
|----------|------|
| Review + remediation plan (round 1) | `.scratch/docs/plan/YYYY-MM-DD-<slug>-review.md` |
| Review + remediation plan (round N) | `.scratch/docs/plan/YYYY-MM-DD-<slug>-review-N.md` |

Overrides: if the user names a different location, use it. If the user says they don't want persistent files, skip the review file writes and present the review inline only.

**Git scope: working tree only.** This skill never commits, branches, or pushes. Code changes and `.scratch/docs/plan/` artifacts are left for the user to commit (or ignore) themselves.

## Phase 1 — Plan (Claude, main thread, deep thinking)

Runs in the main conversation thread. Think hard throughout this phase — planning quality drives everything downstream.

1. **Force plan mode ON.** If not already in plan mode, switch it on yourself via the `EnterPlanMode` tool (load its schema via ToolSearch first if it is deferred). If the tool is unavailable or the call fails, **stop** and tell the user to enable plan mode manually (Shift+Tab) — wait for confirmation; do not plan outside plan mode.
2. **Explore via cheap subagents.** Fan out `Explore` subagents at the mid tier to map the relevant parts of the codebase (architecture, conventions, the files the task will touch, existing tests, CI checks). Spawn them in parallel when the questions are independent. Escalate an individual exploration one tier only when it requires real judgment (e.g., "which of these three abstractions should the change hook into"), not for search and retrieval. Never use the top tier for exploration subagents.
3. **Interview relentlessly.** Before writing the plan, interrogate the user about every aspect of the task until you reach shared understanding — walk down each branch of the decision tree, resolving dependencies between decisions one by one. Rules:
   - For every question, provide your recommended answer.
   - Batch related questions in one turn rather than dribbling them out; keep unrelated decision branches in separate turns.
   - If a question can be answered by exploring the codebase, dispatch a sonnet explorer instead of asking the user.
   - Keep grilling until there are no unresolved decisions that would change the plan. Ambiguity that survives the interview becomes a Codex hallucination later — resolve it now.
4. **Synthesize the plan.** The plan must contain:
   - **Context** — what exists today, in enough detail that Codex needs no further discovery
   - **Approach** — the chosen design and why (alternatives rejected, in one line each)
   - **Changes** — file-level change list: each file, what changes, and why
   - **Verification** — exact commands Codex must run and have pass (tests, linter, type-checker, build), derived from the project's CI config where available
   - **Out of scope** — explicit non-goals, so neither Codex nor the reviewer invents extra work
5. **Gate: plan-mode approval.** Present the plan through the plan-mode approval flow (`ExitPlanMode`) — do not write it to a file. Iterate on feedback until the user approves. Do not start Phase 2 without explicit approval.

## Phase 2 — Implement (Codex, gpt-5.6, high effort)

1. Invoke the `codex:codex-rescue` subagent via the **Agent tool** (`subagent_type: "codex:codex-rescue"`). That subagent parses runtime flags out of the prompt text itself, so the flags below are written literally into the prompt, not passed as Agent tool parameters. The prompt must contain:
   - The flags, as literal text: `--model gpt-5.6 --effort high --write --fresh` (`--fresh` means "start a new Codex thread, don't resume a prior one"; if the runtime rejects the model name, surface the error to the user rather than picking a substitute)
   - The full plan contents inlined — the plan lives in-conversation (plan-mode convention), so Codex must receive it verbatim and must not depend on any plan file existing
   - An instruction to implement exactly what the plan specifies, run the plan's verification commands, and report what was changed and what the verification output was
2. **Foreground by default.** Run in the background (the Agent tool's `run_in_background: true`) only if the user asks for it or the plan is clearly long-running (many files, large refactor).
3. **Sanity check on return.** When Codex finishes: confirm a diff exists (`git status`), confirm it touches roughly the planned files, and read Codex's verification report. Show the user a one-paragraph summary of what changed. If Codex reports failure or produced no diff, surface that verbatim and ask the user how to proceed — do not quietly re-implement in the main thread.
4. No user gate here — flow directly into Phase 3.

## Phase 3 — Review (fresh Fable subagent, max thinking)

1. Spawn a **fresh `general-purpose` subagent with `model: fable`**. The prompt must begin with the word **ultrathink** and include:
   - The original task description
   - The full plan contents (longform documents near the top of the prompt, task at the end)
   - The diff to review: `git diff <baseline-ref>` output plus the contents of any untracked files Codex created (or, in a non-git repo, the plan's file list to read directly)
   - Pre-existing dirty paths to ignore, if any were recorded
   - Permission to spawn its own `Explore` subagents at the mid tier for surrounding-context questions — and an instruction never to use a top-tier model for exploration
   - The required output format (below)
2. **The reviewer judges the diff against the plan**, with fresh eyes and no authorship bias: correctness, plan coverage (everything implemented? anything out-of-scope added?), integration with surrounding code, error handling, test adequacy, and whether verification commands actually passed.
3. **Required reviewer output** — two parts:
   - **Findings**, severity-ranked (Critical / Major / Minor / Nit), each with file:line evidence
   - **Remediation plan** — a self-contained, Codex-ready plan covering every Critical and Major finding (Minor/Nit included at the reviewer's discretion): same structure as a Phase 1 plan (context, changes, verification). It must be executable by Codex without access to the review conversation.
4. **Write the review file** to `.scratch/docs/plan/YYYY-MM-DD-<slug>-review.md` (subsequent rounds get `-review-2.md`, `-review-3.md`, …).
5. **A clean review** (no Critical or Major findings) ends the run: report it, mention any Minor/Nit items inline, and stop.

### Review gate

Present the findings summary (all severities, Critical/Major in full, Minor/Nit at least as a count with one-liners), then ask the user (AskUserQuestion) with exactly these choices:

- **Stop here** — leave the working tree and the remediation plan as-is; the user takes over.
- **Remediate** — run the remediation, then stop.
- **Remediate + re-review** — run the remediation, then loop back to a fresh Phase 3 review of the updated diff, followed by this gate again.

**Remediation** = `codex:codex-rescue` with `--model gpt-5.6 --effort xhigh --write --fresh`, fed the full remediation plan inlined, with the same sanity check as Phase 2 on return.

There is no hard iteration cap — every loop passes through this gate, so the user is the cap. If two consecutive reviews surface the same finding unresolved, say so explicitly and recommend stopping for manual intervention rather than looping again.

## Failure handling

- **Codex invocation fails** (CLI missing, unauthenticated, companion error): stop, show the error verbatim, point to `/codex:setup`. Never substitute main-thread implementation for a failed Codex run without asking.
- **Reviewer subagent returns inadequate output** (empty, no remediation plan, no file:line evidence): retry once with a more specific prompt. If it fails again, do the review in the main thread and tell the user the subagent failed.
- **Cancellation** ("stop", "abandon"): report what's in the working tree and `.scratch/docs/plan/`, and leave everything in place — this skill never deletes user work.

## Model summary

| Step | Who | Model / effort |
|------|-----|----------------|
| Planning | Main thread (plan mode forced on) | Session model, deep thinking |
| Exploration (plan + review) | `Explore` subagents | mid tier (one tier up only for judgment calls) |
| Implementation | `codex:codex-rescue` | `gpt-5.6`, `high`, `--write` |
| Review | `general-purpose` subagent | `fable`, ultrathink |
| Remediation | `codex:codex-rescue` | `gpt-5.6`, `xhigh`, `--write` |

Note: the planning phase's thinking depth rides on the session model — this skill cannot switch the main thread's model. The review phase is pinned to Fable regardless, via the subagent model override.
