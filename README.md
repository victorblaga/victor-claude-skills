# victor-claude-skills

Custom skills with Claude-first canon plus Codex-native variants.

## Canonical Source

The Claude skill definitions under `skills/` are the source of truth.

Codex-native variants live under `plugins/victor-codex-skills/skills/` and are derived from the canonical Claude prompts. When behavior diverges, update the Claude skill first and then port the change into the Codex variant.

## Skills

- **deep-implement** — End-to-end workflow for turning a problem statement into a validated proposal and implemented solution
- **mega-review** — Comprehensive multi-dimensional code review producing a structured markdown report
- **review-triage** — Interactive triage of mega-review findings into an implementation plan
- **grill-me** — Interview the user relentlessly about a plan or design until reaching shared understanding
- **cross-examine** — Become the codebase expert and answer the user's questions with evidence
- **forge** — Iterative top-down code construction (build, refactor, refine) with horizontal-slice design and challenger validation
- **long-form-article** — Collaborative workflow for substantial article drafting and revision
- **argument-structure** — Diagnose a draft or idea against the Minto Pyramid Principle and deliver a restructuring plan as a visual HTML artifact
- **llm-council** — Run decisions through 5 AI advisors who analyze, peer-review, and synthesize a final verdict
- **sweep** — Whole-codebase hygiene sweep across duplication, dead code, weak types, defensive code, and comment slop
- **workstream-implementer** — Project-aware implementation workflow from JIRA ticket or idea through multi-repo planning, PRs, CI, and review handoff
- **frontend-review** — Design-quality review of implemented FE surfaces against composition / craft / content / structure rubrics, with one-by-one fix triage

## Claude Installation

```text
/plugin marketplace add victorblaga/victor-skills-marketplace
/plugin install victor-claude-skills
/reload-plugins
```

## Codex Installation

Codex does not mirror Claude Code's hosted marketplace flow. The supported path is the plugin bundle under `plugins/victor-codex-skills/`.

Use `.agents/plugins/marketplace.json` in this repo as the template for your local `~/.agents/plugins/marketplace.json`.

For ongoing updates, use the tracked sync script in this repo:

```text
./bin/victor-skills-sync
```

If you prefer a global command, symlink it once:

```text
ln -sfn "$PWD/bin/victor-skills-sync" ~/.local/bin/victor-skills-sync
```

The sync script:

- pulls the latest repo state
- refreshes the runtime bundle at `~/plugins/victor-codex-skills`
- refreshes the Codex cache at `~/.codex/plugins/cache/victor-local-plugins/victor-codex-skills/<version>`
- copies the plugin contents flat into the version root so Codex can load `.codex-plugin/plugin.json`
- prunes legacy Victor skill symlinks from `~/.codex/skills` so the skills surface only once

The Codex plugin bundle manifest is at `plugins/victor-codex-skills/.codex-plugin/plugin.json`.
