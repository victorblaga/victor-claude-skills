# victor-claude-skills

Custom skills with Claude-first canon plus Codex-native variants.

## Canonical Source

The Claude skill definitions under `skills/` are the source of truth.

Codex-native variants live under `plugins/victor-codex-skills/skills/` and are derived from the canonical Claude prompts. When behavior diverges, update the Claude skill first and then port the change into the Codex variant.

## Skills

- **deep-implement** — End-to-end workflow for turning a problem statement into a validated proposal and implemented solution
- **mega-review** — Adaptive multi-dimensional code review for agent-written branches: planner subagent steers 10 dimensions (+ migration/API specialists), evidence pass, intent conformance, a dedicated AI-slop dimension with a load-bearing check, falsification verification, recurring-pattern rollup, and a verdict report — with token-lean orchestration
- **review-triage** — Interactive triage of mega-review findings (tensions, patterns, slop classes, IC/EV prefixes) into an implementation plan
- **cross-examine** — Become the codebase expert and answer the user's questions with evidence
- **forge** — Iterative top-down code construction (build, refactor, refine) with horizontal-slice design and challenger validation
- **long-form-article** — Collaborative workflow for substantial article drafting and revision
- **argument-structure** — Diagnose a draft or idea against the Minto Pyramid Principle and deliver a restructuring plan as a visual HTML artifact
- **sweep** — Whole-codebase hygiene sweep across duplication, dead code, weak types, defensive and speculative code, low-value tests, and comment slop; PR-branch-aware preflight, 4 paired dimension agents (area-sharded for large repos), and an optional auto mode with subagent adjudication of high-blast findings
- **workstream-implementer** — Project-aware implementation workflow from JIRA ticket or idea through multi-repo planning, PRs, CI, and review handoff
- **goal-prompt** — Generate copy-paste-ready `/goal` prompts for Claude Code or Codex goal loops, classifying each goal first: dev-workstream goals get workstream-implementer, JIRA, review and performance gates; general (non-dev) goals get a goal contract, evidence standard, and review loop
- **frontend-review** — Design-quality review of implemented FE surfaces against composition / craft / content / structure rubrics, with one-by-one fix triage
- **plan-codex-review** — Three-phase pipeline: Claude plans (relentless requirements interview + cheap explorers), Codex implements, fresh-context Claude reviews and produces a Codex-ready remediation plan. Claude Code only — requires the openai-codex plugin; deliberately has no Codex-native variant
- **decision-audit** — Post-implementation audit of the decisions a session made, not the diff: structured self-report by category, fresh-context cross-check against the diff, blindspot ranking, and one-by-one keep/revise/revert triage

## How These Fit Together

Every skill is explicit-invoke only: `/name` in Claude Code, `$name` in Codex. Names below are written bare.

### Starting a change

`deep-implement` is the default entry point for a change in an existing repo. Its triage sizes the work — trivial, small, medium, large — and confirms the depth before spending anything. Start elsewhere when:

| Situation | Start with | Why |
|---|---|---|
| The code area is unfamiliar | `cross-examine` | Interrogate the codebase until the answers hold up. Writes nothing, changes nothing. |
| The existing structure fights the change, or it is a new subsystem | `forge` | Designs a level at a time with approval at each. `deep-implement` assumes the current shape is roughly right. |
| A ticket owns the work, possibly across several repos | `workstream-implementer` | Refines the ticket into a contract, scopes the repos, then runs the change through a deep- or forge-shaped pass. |
| Codex should write the code | `plan-codex-review` | Claude plans and reviews, Codex implements the middle. Claude Code only. |
| The work should run unattended | `goal-prompt`, then paste into a goal loop | Follow up with `decision-audit` to inspect the choices the run made rather than its diff. |

Rule of thumb across the three heavy workflows: **`deep-implement`** when you know roughly where the code goes, **`forge`** when you do not or when where it currently goes is wrong, **`workstream-implementer`** when a ticket owns the work and a tracker needs updating.

### Reviewing a change

```text
mega-review                    → report.md; reads only, changes nothing
review-triage <report>         → accept / reject / defer per finding; ordered plan + persistent notes
deep-implement <report>        → implements the accepted findings on the same branch
```

`frontend-review` audits implemented UI against design rubrics — a complement to `mega-review` on the same diff, not a replacement. `sweep` is a periodic whole-codebase hygiene pass rather than a per-change step: run it after a large `forge`, not after every feature.

### Composition

`workstream-implementer` is the only outer controller. It owns the ticket contract, repo scope, branches, PRs, CI and tracker updates, and delegates the change itself to a deep- or forge-shaped pass.

The rest do not nest. `forge` and `deep-implement` are alternatives to each other, and `mega-review` runs after either — never inside one, since its value comes from reviewing a finished diff with no investment in how it was produced.

### The shared assumption

The implementation and review skills are built around one premise: coding models are trained against rewards that fire when tests pass, so nothing in that signal charges for the maintenance cost a change leaves behind. Passing tests are necessary and not sufficient. That is why `deep-implement` fixes exact signatures and the call path before any code is written, why regression tests must be seen to fail before the patch, why `mega-review` runs a dedicated AI-slop dimension, and why every PR body names what was *not* verified. The workflows do not remove the need to read the diff — they aim to make it cheap and fast to read.

## Claude Installation

```text
claude plugin marketplace add victorblaga/victor-skills-marketplace
claude plugin install victor-claude-skills
claude plugin update victor-claude-skills
```

## Codex Installation

Codex uses this Git repository as the marketplace source and installs the plugin through the Codex CLI:

```text
codex plugin marketplace add victorblaga/victor-claude-skills --ref master
codex plugin add victor-codex-skills@victor-skills-marketplace
```

For ongoing updates:

```text
codex plugin marketplace upgrade victor-skills-marketplace
codex plugin remove victor-codex-skills@victor-skills-marketplace
codex plugin add victor-codex-skills@victor-skills-marketplace
```

The root Codex plugin manifest is at `.codex-plugin/plugin.json`; it points Codex at the plugin skills under `plugins/victor-codex-skills/skills/`.

## Cursor Installation

Cursor reads the marketplace manifest at `.cursor-plugin/marketplace.json` and the plugin manifest at `.cursor-plugin/plugin.json`. Both point at the canonical skills under `skills/`.

### Marketplace (team or personal)

1. In Cursor, go to **Dashboard → Plugins → Add Marketplace → Import from Repo**.
2. Paste `https://github.com/victorblaga/victor-claude-skills`.
3. Install **victor-claude-skills** from **Customize**.
4. Optional: enable **Auto Refresh** and install the Cursor GitHub App on the repo so pushes re-index the marketplace.

### Local development

```text
ln -sfn /path/to/victor-claude-skills ~/.cursor/plugins/local/victor-claude-skills
```

Then reload Cursor. Changes in your checkout are picked up immediately via the symlink.
