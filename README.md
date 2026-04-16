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

Use `.agents/plugins/marketplace.json` in this repo as the template for your local `~/.agents/plugins/marketplace.json`, then install or sync the whole plugin bundle from `plugins/victor-codex-skills/`.

If you already use the local helper command `victor-codex-skills sync`, that is the preferred refresh path. It pulls the latest plugin bundle from GitHub, refreshes the installed/runtime copies, and prunes legacy Victor skill symlinks from `~/.codex/skills` so the skills surface only once.

The Codex plugin bundle manifest is at `plugins/victor-codex-skills/.codex-plugin/plugin.json`.
