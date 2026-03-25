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

## Overview

<Mermaid diagram — bird's-eye view of the system>

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

At the top level, use a **block diagram** or **flowchart** that shows containment and relationships between major components. Choose the diagram type that best communicates the structure:

- **Block diagram** — when the key insight is what contains what (packages, modules, layers)
- **Flowchart** — when the key insight is how things flow (data pipeline, request processing)
- **Graph (LR or TD)** — when relationships and dependencies matter most

Keep the top-level diagram simple — 5-10 nodes maximum. Detail comes in Phase 3 when drilling into individual nodes.

Use meaningful labels. Each node should be understandable without reading the surrounding text.

## Component Sections

Each top-level component gets a section in the Structure part of the outline. At this level, keep descriptions brief:

- **Purpose** — one sentence, what does this component do
- **Current location** — where the code lives now (refactor/migrate only)
- **What it hides** — what complexity is internal to this component
- **Interface** — how other components interact with it (if known at this level)

Don't go deep yet. The goal is to get the top-level shape right before expanding any branch.

## Refactor/Migrate Mode

In refactor and migrate modes, the outline is derived from the Phase 1 exploration findings:

1. Read the synthesis from Phase 1
2. Identify the natural architectural units
3. Map them to the outline structure
4. Annotate each component with current file locations
5. Include the findings appendix with design principle violations

The outline represents the **target state** — how the code should be structured. If the current structure has problems (identified in the findings), the outline should reflect the improved design, not mirror the existing mess.

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
