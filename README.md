# victor-claude-skills

Custom skills with Claude-first canon plus Codex-native variants.

## Canonical Source

The Claude skill definitions under `skills/` are the source of truth.

Codex-native variants live under `plugins/victor-codex-skills/skills/` and are derived from the canonical Claude prompts. When behavior diverges, update the Claude skill first and then port the change into the Codex variant.

## Skills

- **deep-implement** — End-to-end workflow for turning a problem statement into a validated proposal and implemented solution
- **mega-review** — Adaptive multi-dimensional code review for agent-written branches: planner subagent steers 9 dimensions (+ migration/API specialists), evidence pass, intent conformance, LLM-slop checklists, falsification verification, recurring-pattern rollup, and a verdict report — with token-lean orchestration
- **review-triage** — Interactive triage of mega-review findings (tensions, patterns, IC/EV prefixes) into an implementation plan
- **cross-examine** — Become the codebase expert and answer the user's questions with evidence
- **forge** — Iterative top-down code construction (build, refactor, refine) with horizontal-slice design and challenger validation
- **long-form-article** — Collaborative workflow for substantial article drafting and revision
- **argument-structure** — Diagnose a draft or idea against the Minto Pyramid Principle and deliver a restructuring plan as a visual HTML artifact
- **sweep** — Whole-codebase hygiene sweep across duplication, dead code, weak types, defensive code, and comment slop
- **workstream-implementer** — Project-aware implementation workflow from JIRA ticket or idea through multi-repo planning, PRs, CI, and review handoff
- **goal-prompt** — Generate copy-paste-ready `/goal` prompts for Claude Code or Codex goal loops, classifying each goal first: dev-workstream goals get workstream-implementer, JIRA, review and performance gates; general (non-dev) goals get a goal contract, evidence standard, and review loop
- **frontend-review** — Design-quality review of implemented FE surfaces against composition / craft / content / structure rubrics, with one-by-one fix triage
- **plan-codex-review** — Three-phase pipeline: Claude plans (relentless requirements interview + cheap explorers), Codex implements, fresh-context Claude reviews and produces a Codex-ready remediation plan. Claude Code only — requires the openai-codex plugin; deliberately has no Codex-native variant

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
