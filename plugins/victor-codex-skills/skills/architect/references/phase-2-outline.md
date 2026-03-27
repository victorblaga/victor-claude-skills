# Phase 2: Outline

## Purpose

Produce the first structural outline of the codebase — the "table of contents." This is the top-level view that the user will iterate on before drilling deeper.

## Greenfield Kickoff

If there's no existing code to scan (greenfield mode), gather the essentials before producing the outline:

1. **Purpose** — "What does this thing do?" Get 1-3 sentences.
2. **Scope** — "What are the boundaries? What's in, what's out?"
3. **Key workflows** — "What are the main things it does? Walk me through the happy path."

Don't over-interview. Get enough to produce a first draft, then iterate. If the user has already described these (e.g. in the invocation arguments or prior conversation), skip the questions and draft immediately.

## Outline Document Structure

Write the outline to `docs/plans/<name>-<date>-<id>/plan.md`. Generate the `<id>` as a short random string (4-5 chars).

The document starts with these sections and grows as drill-down progresses:

```markdown
# <Name>

## Purpose

<1-2 paragraphs describing what this code does, who it serves, and why it exists>

## What This System Does (refactor/migrate only)

<Behavioral model (from Phase 1 synthesis): workflows, inputs/outputs, business rules, runtime characteristics, external interactions. NOT v1's module structure — what the system does, not how v1 organizes it.>

## Target State — Overview

<Mermaid diagram — bird's-eye view of the target system>

## Structure

<Structured markdown breakdown — one section per top-level component>

### <Component 1>

**Purpose:** <one sentence>
**Current location:** <file paths where this logic currently lives> (refactor/migrate only)

<description of what this component does and what it hides>

### <Component 2>
...

## Domain Entities

| Entity | Description |
|--------|-------------|
| <Name> | <one-line description> |

## Cross-Cutting Concerns

### <Concern 1: e.g. Logging>
**Pattern:** <how it's done or how it should be done>
**Used by:** <which components>

### <Concern 2>
...

## Findings (refactor/migrate only)

<Design principle violations and observations from Phase 1 exploration>

| Finding | Location | Principle Violated |
|---------|----------|--------------------|
| <description> | <file:line> | <e.g. shallow module, information leakage> |
```

## Mermaid Diagram

The diagram is the most important artifact at this phase. It establishes the shape of the system — everything else is commentary.

At the top level, use a **block diagram** or **flowchart** that shows containment and relationships between major components. Choose the diagram type that best communicates the structure:

- **Block diagram** — when the key insight is what contains what (packages, modules, layers)
- **Flowchart** — when the key insight is how things flow (data pipeline, request processing)
- **Graph (LR or TD)** — when relationships and dependencies matter most

Keep the top-level diagram simple — 5-10 nodes maximum. Detail comes in Phase 3 when drilling into individual nodes.

Use meaningful labels. Each node should be understandable without reading the surrounding text.

### Designing for loose coupling

When drawing the diagram, pay attention to the edges between components. Each edge represents a dependency — a reason for one component to know about another. Minimize these:

- Components should communicate through **narrow interfaces**, not shared state
- Where two components need data from each other, introduce a **shared data store** or **query interface** rather than direct coupling
- If a component exposes internal data structures to its consumers, redesign — expose **query methods** instead
- Ask: "Could these two components run in separate processes?" If not, explore why — the coupling may be unnecessary

## Component Sections

Each top-level component gets a section in the Structure part of the outline. At this level, keep descriptions brief:

- **Purpose** — one sentence, what does this component do
- **Current location** — where the code lives now (refactor/migrate only)
- **What it hides** — what complexity is internal to this component
- **Interface** — how other components interact with it (if known at this level)

Don't go deep yet. The goal is to get the top-level shape right before expanding any branch.

## Refactor/Migrate Mode

**The outline is a fresh design informed by v1's requirements, not a reorganization of v1's modules.**

The user is refactoring because something is wrong with v1 — tangled coupling, unclear boundaries, accumulated tech debt. Reproducing v1's structure with different names is not refactoring. The architect's job is to design the system the user *wishes* they had, using v1 only as evidence of what the system must do.

The process:

1. **Start from the behavioral model** (Phase 1 synthesis) — what does the system do? What are its workflows, inputs, outputs, business rules?
2. **Design from first principles** — given those requirements, how would you structure this system from scratch? Apply the design principles: deep modules, information hiding, loose coupling. Don't look at v1's file layout while doing this.
3. **Reality-check against v1** — now compare your clean design to v1. Are there business rules or invariants you missed? Edge cases the behavioral model didn't capture? Hidden requirements? Adjust the design to account for these, but don't adopt v1's structure to do it.
4. **Annotate with v1 anchors where helpful** — for each component, note which v1 files contain the logic that will inform the implementation. These are references for the engineer, not constraints on the design.
5. **Include the findings appendix** — the design principle violations from Phase 1. These explain *why* the new design differs from v1.

The outline represents the **target state** — how the code *should* be structured. v1's structure is a cautionary tale, not a starting point.

## Migration Mode

Migration has unique concerns beyond refactoring. The outline must track both the old and new worlds:

### Migration mapping

Include a mapping section that connects **new components to v1 logic they draw from** (not the reverse — the new design leads):

```markdown
## Migration Mapping

| New component | v1 reference | Notes |
|---|---|---|
| FuzzyMatchContext | `old_project/src/matching.py:30-120` | Reuse scoring algorithm, new query interface |
| LiveCache | `old_project/src/cache.py` | Reuse data loading, redesign as query object |
| IngestPhase | (no v1 equivalent) | New — v1 had no input validation |
```

### What to preserve vs. rewrite

For each component in the **new** design, be explicit about what v1 logic informs it:
- **Reuse algorithm** — the algorithm or business rule is correct, extract and adapt it to the new interface
- **Rewrite** — the requirement must be met, but v1's approach doesn't fit the new design
- **No v1 equivalent** — new component that doesn't exist in v1

Note the framing: the new design leads, and v1 logic adapts to fit it. Not the other way around. Don't list v1 modules and assign them destinations — list new components and note which v1 logic informs them.

### Constraints from the old code

Phase 1 exploration of the old codebase reveals hidden requirements — edge cases, invariants, non-obvious business rules. These must be captured in the outline, even if they aren't obvious from a clean-sheet design. Add them as annotations on the relevant components.

## Data Flow Audit

Before presenting the outline, audit every edge in the diagram — what data crosses each boundary?

For each arrow between components, name the type that flows across it. Not "data" or "result" — a specific named type. If you can't name it, the boundary is underspecified.

| From | To | What flows | Type |
|------|-----|-----------|------|
| Builder | Repository | A built snapshot | `Snapshot` |
| Repository | ModelScoring | Query results | `list[ModelSiteRow]` |

**Red flags during this audit:**
- **`dict` or `Any` crossing a boundary** — make it a dataclass. A `dict[str, Any]` crossing a module boundary is a bug waiting to happen.
- **Primitive obsession** — raw `str` where a domain type should exist (paths, IDs, timestamps, watermarks). If two strings have different semantics, they need different types.
- **Method signatures with >3 parameters** — the parameters likely want to be a single typed object.
- **Same data assembled from scratch in multiple places** — it should be constructed once and passed as a typed value.

Update the Domain Entities table with every type identified during this audit. These become the implementation's data types — the architect defines them, the engineer uses them.

## Design Principles Review

Before presenting the outline, review each component boundary against the Design Questions in `design-principles.md`:

- Does each component hide meaningful complexity behind a simple interface?
- Are components loosely coupled — could they run independently?
- Do consumers use query methods rather than accessing raw data structures?
- Is knowledge encapsulated — or leaked across multiple components?
- Are layers providing genuinely different abstractions, or just pass-through?

This review catches structural issues before the user invests time drilling deeper.

## Presenting to the User

After writing the outline to disk:

1. **Announce** where the file is: "I've written the initial outline to `docs/plans/<path>/plan.md`"
2. **Present a summary** in the conversation — the purpose statement and a text description of the top-level components (not the full document)
3. **Ask for feedback**: "Review the full outline in your editor. Happy with the top-level structure, or should I adjust before we drill deeper?"

The user may:
- Give structural feedback ("X should be split", "Y doesn't belong here", "merge A and B")
- Approve and pick a branch to drill into ("looks good, go deeper on component X")
- Ask questions ("why did you separate X from Y?")

Update the document on disk after each round of feedback. Present a summary of what changed.

## Checkpoint

Before proceeding to Phase 3 (drill-down), the user must explicitly approve the top-level structure. Don't drill into branches while the top-level shape is still uncertain — changes at the top cascade downward.
