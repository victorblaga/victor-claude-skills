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
- **architect** — Top-down system design, refactoring, and migration planning
- **engineer** — Implement a completed architecture plan top-down
- **surgeon** — Structural refinement of existing working code
- **long-form-article** — Collaborative workflow for substantial article drafting and revision
- **llm-council** — Run decisions through 5 AI advisors who analyze, peer-review, and synthesize a final verdict
- **sweep** — Whole-codebase hygiene sweep across duplication, dead code, weak types, defensive code, and comment slop

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
