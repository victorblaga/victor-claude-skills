# Horizontal Slice: The Core Forge Loop

## The Pattern

For each abstraction level, the forge loop is:

1. **Design** all components at this level
2. **Challenge** the design with a fresh agent
3. **User reviews** — approves, corrects, or restructures
4. **Implement** all components at this level
5. **Mark exemplars**, log corrections
6. **Descend** to the next level

## Step 1: Design

### What to produce
For each component at the current level:
- **Purpose**: one sentence
- **Interface**: typed signatures (input types, output types). Not prose — actual type names.
- **Hides**: what complexity is internal
- **Diagram**: mermaid diagram showing components and their relationships at this level

### Typed interfaces are mandatory
Every interface must name its types. Not "takes site data" — `score(sites: list[StudySiteRow]) -> list[SiteScore]`. This catches primitive obsession early and forces you to define domain entities.

If you can't name a type, the component's responsibility is unclear. Stop and clarify.

### Data flow audit
For every arrow in the diagram, name the type that flows across it. If it's `dict`, `Any`, or unnamed, introduce a domain type. Update the Domain Entities table in plan.md.

### Design at the right level
The most common mistake: going concrete too soon. At the orchestration level, components should speak domain language:
- GOOD: "SnapshotBuilder coordinates: stage sources → resolve studies → assemble snapshot"
- BAD: "SnapshotBuilder opens SQLite connection, streams JSONL from S3, runs union-find algorithm"

The intermediate abstractions ("stage sources") are where the design value lives. They let the orchestrator think in business terms without knowing about databases.

## Step 2: Challenge

Launch a fresh challenger subagent. See `references/challenger-protocol.md` for the full protocol.

The challenger reads:
- The current design (from plan.md)
- Exemplar files (if any exist)
- Corrections log (if any exist)
- Design principles reference

It produces findings — concrete problems, not vague suggestions. Each finding has a specific location, what's wrong, and a proposed fix.

## Step 3: User Review

Present the design and challenger findings to the user. The user may:
- Approve the design as-is
- Request changes ("split X", "merge Y and Z", "this doesn't belong here")
- Disagree with challenger findings
- Ask questions
- Request a vertical dive on a specific component

Update plan.md after each round of feedback. Present a summary of changes.

**Do not descend until the user explicitly approves the current level.**

## Step 4: Implement

Launch a fresh implementer subagent for each component (or group of related components).

The implementer prompt must include:
- The component's section from plan.md (purpose, interface, hides)
- Paths to exemplar files: "Read these first. Match their patterns."
- The corrections log: "Read this. Do not repeat these mistakes."
- The horizontal discipline rule: "Implement ONLY at this level. Do NOT fix downstream breakages."
- Constraints from Phase 0

### Implementation at different levels

**Level 1 (top level)**: Create files with correct names, interfaces, and imports. Method bodies are high-level comments describing intent + `raise NotImplementedError`. The module graph must be real (importable).

**Level 2+**: Flesh out internals. Sub-components get their own files/classes. Still interfaces + intent comments at the next level down.

**Leaf level**: Write full implementations. This is where infrastructure code lives — SQL queries, S3 operations, file I/O, API calls.

### After implementation
Run the challenger agent again, this time against the implemented code (not just the design). The challenger checks:
- Does the implementation match the plan?
- Does it follow exemplar patterns?
- Are abstraction levels maintained?
- Any structural problems introduced?

## Step 5: Exemplars and Corrections

After the user reviews the implementation:

**Exemplar marking**: If the user approved a component (especially early on), ask: "Should I mark this as an exemplar for future components?" Add to `exemplars.md`.

**Correction logging**: If the user corrected something, log it: "I noticed you changed X to Y. Want me to log this as a pattern?" Add to `corrections.md` with the LESSON and WHY.

See `references/exemplars-and-corrections.md` for the full protocol.

## Step 6: Descend

Move to the next level of abstraction. The components designed at level N become the containers for level N+1 components.

Before descending, update `progress.md`:
- What was completed at this level
- Which components are exemplars
- Known breakages that will be resolved at the next level

## The Horizontal Discipline Rule

When working at level N:
- Change ONLY components at level N
- Do NOT chase downstream breakages
- Do NOT update callers, fix imports, or repair tests for lower levels
- Do NOT "make it compile" by modifying things outside the current level
- Note breakages in progress.md

The project WILL be un-compilable between horizontal slices. This is expected.

**Why agents violate this**: Agents have a strong instinct to leave the project working. During architectural reshaping, broken downstream code means the old shape no longer fits the new one. You'll fix it when you descend.

**Exception**: Trivial downstream fixes (rename an import) while already looking at the file. Never open a lower-level file just to fix breakages.

## Vertical Dives

Vertical dives are OPTIONAL and OPPORTUNISTIC. Use when:

1. **Performance implications**: "This processes 120M records — streaming vs batch affects the layer above"
2. **Interface uncertainty**: "I'm not sure this interface works — let me prove it with a real implementation"
3. **Constraint discovery**: "This component reveals a constraint we didn't know about"
4. **User request**: "Go deep on X before continuing"

After a vertical dive:
- Check if findings affect the current horizontal slice
- If yes: update the design at this level, re-challenge, user reviews
- If no: note the finding, rejoin the horizontal slice

Bias towards horizontal. Only dive vertical when there's a concrete reason.

## Greenfield vs Refactor Differences

**Greenfield (build mode)**: No existing code. Design from requirements and constraints. Clarifying questions if the structure isn't obvious.

**Refactor**: Existing code provides the behavioral model (from Phase 1). Design the new structure from first principles — do NOT reorganize v1's modules. v1 tells you WHAT to build, not HOW to organize it. Reference v1 files as notes for the engineer ("v1 reference: src/old_module.py:30-120 — scoring algorithm to extract"), not as structure to preserve.

**Refine**: Lighter touch. The code works; you're improving abstractions. Exploration focuses on the target area. Changes are more surgical — introduce types, split responsibilities, separate abstraction levels. But the horizontal slice discipline still applies: fix all components at this level before descending.

## Progress Tracking

Maintain `docs/plans/<name>/progress.md`:

```markdown
# Progress — <name>

## Current level
Level 2: Services — designing internal structure for all actors

## Completed
- [x] Phase 0: Constraints (data: 120M records, streaming mandatory)
- [x] Phase 1: Exploration (behavioral model extracted)
- [x] Level 1: Top-level actors (commit abc1234)
  - Exemplars: SnapshotBuilderActor, DataPrepActor
  - Corrections: 3 logged (see corrections.md)

## In progress
- [ ] Level 2a: SnapshotBuilder internals
- [ ] Level 2b: ModelScoring internals
- [ ] Level 2c: DataPrep internals

## Known breakages (will resolve at next level)
- SnapshotBuilderActor.build_snapshot() calls BuildSnapshotService which doesn't exist yet
- ModelScoringActor references ModelWorkflowService (not implemented)

## Next up
- Level 3: Infrastructure stagers (DQS, Sitetrove, SiteSentry)
```
