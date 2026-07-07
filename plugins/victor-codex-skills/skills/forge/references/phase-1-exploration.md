# Phase 1: Exploration (Refactor/Refine Only)

## Purpose

Understand the existing system's behavior — workflows, business rules, I/O, invariants — without being anchored to its current module structure.

v1 is a requirements document, not a design document. The user is refactoring because something is wrong with v1's structure. Use v1 to learn WHAT the system does, then design fresh.

## Exploration Agents

Launch 4-6 parallel explorer subagents, each with a focused lens:

1. **Workflows agent**: What are the main workflows? Entry points, happy paths, error paths. What triggers what?
2. **Data flow agent**: What data enters the system? What comes out? What transformations happen? What are the intermediate representations?
3. **Business rules agent**: What domain logic exists? Validation rules, scoring algorithms, decision trees, edge cases. What invariants must be maintained?
4. **External interactions agent**: What does the system talk to? Databases, APIs, queues, file systems. What are the contracts?
5. **Runtime characteristics agent**: How does the system behave at runtime? Concurrency model, resource lifecycle, error handling patterns. (Overlaps with Phase 0 constraints — cross-reference.)
6. **Hidden requirements agent**: What non-obvious things does the code handle? Edge cases buried in conditionals, retry logic, fallback behavior, data cleaning, format normalization.

Each agent reads the code and produces a focused report. They do NOT propose a new structure — they only describe what exists.

## Synthesis

After all agents complete, synthesize their findings into a behavioral model in plan.md:

```markdown
## What This System Does

### Workflows
1. **Snapshot Build**: Triggered by cron or SQS command. Stages data from 3 sources
   (CRM, Registry, Billing), resolves studies via union-find, assembles SQLite
   snapshot, publishes to S3.
2. **Model Scoring**: Triggered after snapshot publish. Reads sites from snapshot,
   scores against model, publishes results to S3 + EventBridge.
...

### Business Rules
- Study resolution uses union-find on (member_study_id, registry_id) pairs
- Sites are deduplicated by golden_id within each source
- Acme studies are identified by sponsor name containing "acme" (case-insensitive)
...

### External Interactions
- S3: reads source data, writes snapshots and results
- PostgreSQL: reads Billing data, does NOT write
- SQS: receives commands, deletes processed messages
...

### Hidden Requirements
- CRM records with empty golden_id are silently skipped (not an error)
- NaN embeddings in scoring must be handled gracefully (v1 line 85)
...
```

## The Imprinting Trap

The biggest risk in Phase 1: deeply imprinting v1's module graph into context and unconsciously reproducing it in the design phase.

Guard against this:

- Report findings in terms of BEHAVIOR, not modules. "The system deduplicates sites by golden_id" not "SiteResolver in staging/sites.py deduplicates."
- Do NOT list v1 files and their purposes. List behaviors and note which files contain them (as references for later, not as structure to preserve).
- When synthesizing, ask: "If I described this system to someone who'd never seen the code, what would they need to know to design it from scratch?"

## Refine Mode Adaptation

For refine mode (improving existing working code), exploration is lighter:

- Focus on the specific target the user pointed at, not the whole system.
- Diagnose structural problems (the red-flags checklist in design-principles.md): primitive obsession, responsibility sprawl, mixed abstraction levels, leaky boundaries.
- Still extract the behavioral model for the target area, so you understand what it does before proposing structural changes.

## Completion

Phase 1 is complete when:

- All explorer agents have reported.
- Findings are synthesized into the behavioral model in plan.md.
- Constraints from Phase 0 are cross-referenced with runtime characteristics.
- The user has reviewed the behavioral model: "Does this capture everything your system does?"

Then proceed to the first horizontal slice.
