# Ticket Workbook

Ticket workbooks live at:

```text
~/.docs/workstream-implementer/projects/<project>/tickets/<JIRA-KEY>/
```

The workbook is local implementation state. Do not link these paths in JIRA.

## Files

`status.md`
: Resumable control file. Update whenever phase, mode, repo scope, branch, PR, blocker, or next action changes.

`jira.md`
: Stakeholder contract mirror: original request, refined problem statement, users / actors, jobs to be done, current pain, desired outcome, acceptance criteria, technical side-goals and constraints, non-goals, open questions, stakeholder-safe updates.

`repos.md`
: Proposed and final repo scope. Separate active repos from reference repos.

`plan.md`
: Implementation plan. Keep it as detailed as needed for a fresh agent or developer to resume.

`verification.md`
: Commands run, results, browser checks, CI status, and proof notes.

`review.md`
: Self-review, adversarial review, mega-review links, triage decisions, and remaining risks.

`decisions.md`
: Ticket-specific decisions and rationale.

`context.md`
: Periodic context summary for long-running work.

`workstreams/<repo>.md`
: Per-repo task state, branch, PR, plan, verification, and blockers.

## Status Format

Use this shape:

```markdown
# Status: CEN-123

- Project: acme-app
- JIRA: CEN-123
- Summary: Add source details action
- Current phase: implementation
- Scope: medium
- Mode: deep
- Active repos: backend, frontend
- Branches:
  - backend: feature/CEN-123/source-details-action
  - frontend: feature/CEN-123/source-details-action
- PRs:
  - backend: https://github.com/org/repo/pull/1
  - frontend: pending
- Last completed: backend endpoint implemented and unit tests passing
- Next action: implement frontend integration
- Blockers: none
- Last updated: 2026-05-23T14:30:00+02:00
```

## Update Rules

- Write detailed internal notes here, not in JIRA.
- Keep JIRA updates sparse and stakeholder-safe.
- Preserve the original request in `jira.md`; add the refined contract separately after ticket refinement.
- Record failed attempts only if they matter for future implementation or risk.
- Record exact verification commands and outcomes.
- For multi-repo tickets, keep one workstream file per affected repo.
- At closeout, summarize reusable lessons and ask before promoting them to the project profile or `notes.md`.
