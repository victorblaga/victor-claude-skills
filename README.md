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
claude plugin marketplace add victorblaga/victor-skills-marketplace
claude plugin install victor-claude-skills
claude plugin update victor-claude-skills
```

## Codex Installation

Codex uses the plugin bundle under `plugins/victor-codex-skills/`. Add this repo as a local marketplace, then install the plugin through the Codex CLI:

```text
codex plugin marketplace add .
codex plugin add victor-codex-skills@victor-local-plugins
```

For ongoing updates after pulling this repo:

```text
codex plugin remove victor-codex-skills
codex plugin add victor-codex-skills@victor-local-plugins
```

If the marketplace was added from a Git source rather than this local checkout, refresh the marketplace first:

```text
codex plugin marketplace upgrade victor-local-plugins
```

The Codex plugin bundle manifest is at `plugins/victor-codex-skills/.codex-plugin/plugin.json`.
