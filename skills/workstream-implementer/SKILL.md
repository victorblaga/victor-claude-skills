---
name: workstream-implementer
description: >
  Project-aware implementation workflow for taking a JIRA ticket or new project idea through
  stakeholder contract clarification, local project profile resolution, multi-repo planning,
  implementation, verification, PR creation, CI monitoring, and JIRA review updates. Use ONLY
  when the user explicitly invokes "workstream-implementer", "/workstream-implementer",
  "$workstream-implementer", or says to use workstream-implementer for a ticket or idea.
  Do not trigger on ordinary implementation requests.
---

# Workstream Implementer

## Overview

Coordinate implementation work that starts from a JIRA ticket or a new idea and may span multiple local repos. JIRA is the stakeholder contract. The local workbook under `~/.docs/workstream-implementer/` is the implementation state.

This skill is the outer controller. It may implement small fixes directly, but for substantial work it routes into existing implementation patterns:

- Use `deep-implement` style for normal nontrivial tickets.
- Use `forge` style for architecture-heavy builds, migrations, refactors, and subsystem reshaping.
- Use `mega-review` then `review-triage` after large or risky diffs.
- Use `agent-browser` for browser, dogfood, and end-to-end UI verification.

## Storage

Use this global, agent-agnostic layout:

```text
~/.docs/workstream-implementer/
  projects/
    <project>/
      project.json
      notes.md
      tickets/
        <JIRA-KEY>/
          status.md
          jira.md
          repos.md
          plan.md
          verification.md
          review.md
          decisions.md
          context.md
          workstreams/
            <repo>.md
```

Use the bundled scripts for deterministic setup:

```bash
python3 scripts/init_project.py <project>
python3 scripts/init_ticket.py <project> <JIRA-KEY>
python3 scripts/validate_project.py <project>
```

Read `references/project-profile-schema.md` when creating or updating a project profile. Read `references/ticket-workbook.md` when creating, resuming, or auditing ticket state.

## Startup

1. Parse the invocation. Accept either a JIRA key or a new idea.
2. Preflight required tools before doing work:
   - JIRA MCP or Atlassian tools for reading/updating tickets.
   - `git` and `gh` for branches, PRs, CI, and merges.
   - `agent-browser` only when browser verification is requested or needed.
3. Resolve the project profile:
   - Explicit user project wins.
   - Then use profile mappings from JIRA project keys, components, and labels.
   - Then infer from ticket text and repo hints.
   - Ask if still ambiguous.
4. If the project profile is missing, run interactive discovery:
   - Ask for root hints, such as `~/work/pfizer`.
   - Search candidate repos under those roots.
   - Classify candidates as `active`, `reference`, or `ignored`.
   - Present a normal-language summary and ask before saving `project.json`.
5. Validate the profile and repo paths.
6. Create or load the ticket workbook.
7. Check every candidate repo worktree before branching. If dirty, stop for that repo and ask how to handle the existing changes. Never overwrite user work.

## JIRA Contract

Use JIRA for externally visible contract and status only:

- original stakeholder request
- cleaned-up implementation contract
- acceptance criteria
- blockers and scope changes
- PR links
- verification summary
- review-ready or done status

Do not use JIRA for internal scratch notes, failed attempts, raw test logs, context summaries, or local workbook paths.

If the skill creates the ticket, write a clean full description. If a stakeholder-created ticket exists, preserve the original request and add a separate implementation contract section. Prefer direct description edits for stable contract updates and comments for events such as blockers, PR links, verification, and review handoff.

Move tickets to In Review or Review when implementation is ready. Never move a ticket to Done unless the user explicitly instructs that the work is approved or done.

Create JIRA subtasks only when they improve external coordination: different owner, visible milestone, separate repo PR, blocker, dependency, or stakeholder-visible progress. Default to one ticket and ask before creating subtasks.

## Project Profiles

`project.json` is local machine config. Store local repo paths, repo roles, branch policy, PR policy, JIRA mappings, and reusable playbooks. Use `~` in paths when possible. If a path is missing, rediscover rather than assuming another machine has the same layout.

Confirm profile updates conversationally. Show exact JSON only when the user asks or when changing risky behavior such as repo paths, base branches, merge settings, deploy commands, or destructive playbooks.

Store durable rationale and conventions in `notes.md`, not in JIRA. Examples:

- active data pipeline repo versus reference legacy repos
- base branch choices per repo
- squash merge policy
- reusable local test or browser test playbooks

When the user gives reusable operational instructions mid-ticket, ask whether to save them to the project profile.

## Repo Scope

Before implementation, propose the affected repo scope:

1. Read the JIRA ticket or idea.
2. Load the project profile.
3. Search active repos for ticket terms.
4. Use reference repos only when the ticket implies migration, parity, legacy behavior, or the user asks.
5. Present a short scope proposal:

```text
I think this affects:
- backend: API and persistence changes
- frontend: UI changes
- data-pipelines: no changes expected
- legacy-data-pipelines: reference only because migration parity is mentioned

Proceed with this repo scope?
```

For tiny obvious tickets, state the assumption and proceed only if the normal autonomy policy allows it.

## Work Modes

After repo scope is clear, choose a mode:

| Mode | Use When | Approval |
|------|----------|----------|
| Direct | Small clear fix, no architectural choices | Proceed after repo scope approval |
| Deep | Most nontrivial product or technical tickets | Show plan, then proceed after approval |
| Forge | Large refactor, migration, new subsystem, architecture-heavy work | Design checkpoints |
| Review | Large/risky diff needs comprehensive audit | Run review, triage, then implement accepted findings |
| Browser verification | UI or end-to-end behavior matters | Use project playbook and `agent-browser` |

Small tickets can run to PR after repo scope approval. Medium tickets need plan approval. Large/refactor/migration tickets need major design checkpoints. Merges and repo settings changes always require explicit user approval.

## Branches, PRs, CI, and Merge

Branch and PR policy comes from the project profile per repo. Default branch pattern:

```text
{type}/{ticket}/{slug}
```

Example:

```text
feature/PFE-123/source-details-action
```

For each affected repo:

1. Fetch the remote.
2. Checkout the configured base branch.
3. Pull or rebase to latest base.
4. Create a ticket branch from latest base.
5. Commit coherent work units automatically with human-style messages that include the JIRA key.
6. Push with upstream.
7. Open one PR per repo into the configured target branch.
8. Link PRs to JIRA and sibling PRs when relevant.
9. Monitor CI.
10. If CI fails, inspect logs, fix issues caused by this work, and retry up to 3 cycles. After 3 failed cycles, stop with diagnostics.

Use squash merge by default. Validate repository merge settings when possible. If squash merge is not enabled, ask before changing repo settings. Merge PRs only when the user explicitly instructs it.

Visible artifacts must not include AI boilerplate or attribution. Do not add `Generated by`, `Co-authored-by` for AI tools, Codex/Claude references, or similar text to commits, PRs, JIRA comments, or merge messages. Do not claim manual authorship; just keep artifacts normal and project-style.

## Verification

Use both project profile playbooks and repo-local instructions:

- Profile playbooks store repeated operational knowledge: start services, backend, frontend, local tests, browser checks.
- Repo instructions such as `AGENTS.md`, `CLAUDE.md`, README files, and local test docs still win when they conflict.
- If repo-local instructions reveal durable changes to the playbook, ask before saving them to the profile.

For browser verification:

1. Start long-running services in managed terminal sessions.
2. Wait for readiness checks.
3. Load `agent-browser` instructions and run the browser task.
4. Stop sessions at the end unless the user wants them left running.
5. Report any sessions left running.

Record detailed verification in `verification.md`. Put only stakeholder-safe proof in JIRA.

## Resumption

On each invocation, check for an existing ticket workbook. Treat `status.md` as the control file. It must record:

- project
- JIRA key
- phase and mode
- active repos
- branches
- PRs
- last completed action
- next action
- blockers
- last updated timestamp

Update `status.md` whenever phase, repo scope, branch, PR, blocker, or next action changes.

## Closeout

At the end of a ticket:

1. Ensure all affected repos are clean except expected branch state.
2. Ensure commits are pushed and PRs exist.
3. Monitor CI and record result.
4. Update JIRA with PR links and verification summary.
5. Move JIRA to Review/In Review, not Done, unless explicitly instructed.
6. Update `status.md`, `verification.md`, `review.md`, and `context.md`.
7. Stop or report long-running local sessions.
8. Ask whether durable new knowledge should be saved to the project profile or `notes.md`.

For substantial tickets, optionally run a fresh process-reflection subagent over the ticket workbook and project profile. It should recommend reusable profile updates, playbook changes, repeated friction, and possible improvements to this skill. It must not update JIRA or modify files directly.
