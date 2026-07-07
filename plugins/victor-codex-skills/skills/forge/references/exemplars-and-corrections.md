# Exemplars and Corrections

## Purpose
Two mechanisms that let the forge skill learn from user feedback:
1. **Exemplars**: Files the user has validated as reference implementations. "This is what good looks like."
2. **Corrections log**: Concrete patterns the user corrected. "Don't do X, do Y instead, because Z."

Together, they create a progressively richer calibration set that implementation agents use to match the user's standards.

## Exemplars

### What qualifies as an exemplar
A file becomes an exemplar when:
- The user actively reviewed and approved it
- It demonstrates a pattern that should be replicated (naming, layering, type usage, file structure)
- It covers one of the key structural layers (orchestration, coordination, infrastructure, domain types)

### When to mark exemplars
- **Early in the project (bootstrapping)**: After the user approves each component, ask: "Should I mark this as an exemplar for future components?"
- **Mid-project (pattern established)**: Stop asking — the exemplar set is stable. Only add new exemplars if the user explicitly validates a new pattern.
- **Never force it**: The user decides what's exemplary, not the skill.

### Exemplar file format

`.docs/plans/<name>/exemplars.md`:

```markdown
# Exemplars

Files the user has validated as reference implementations.
Implementation agents MUST read these before writing new code and match their patterns.

## Orchestration Pattern
- `src/workflows/snapshot/builder.py` — Actor wraps service, speaks domain language only

## Coordination Pattern
- `src/workflows/snapshot/build_service.py` — Service coordinates pipeline steps
- `src/workflows/snapshot/staging_assembler.py` — Assembler calls stagers in order

## Infrastructure Pattern
- `src/workflows/snapshot/internals/staging/crm.py` — Stager streams from source, batch-inserts

## Domain Types
- `src/types/snapshot.py` — Frozen dataclass conventions, typed boundaries
- `src/types/watermarks.py` — ABC with implementations for different comparison strategies
```

### How implementation agents use exemplars
Every implementation agent prompt includes:
```
Before writing any code, read these exemplar files:
[list of exemplar paths]

Match their patterns for:
- Naming conventions (method names, class names, file names)
- Layering (what goes in orchestration vs coordination vs infrastructure)
- Type usage (how domain types are defined and used)
- File organization (what goes in its own file vs stays together)
- Code style (how methods are structured, how errors are handled)
```

## Corrections Log

### What gets logged
Any correction the user makes that reveals a pattern:
- Renaming (generic verb → domain-specific verb)
- Restructuring (splitting a mixed-level method into layers)
- Type introduction (replacing primitives with domain types)
- File reorganization (splitting or merging files)
- Any change where the user's version differs structurally from the agent's version

### When to log corrections
After each user correction, ask: "I noticed you changed X to Y. Want me to log this as a pattern for future components? If so, what's the reason?"

**Early (bootstrapping)**: Ask after every correction. Corrections are frequent and establish the user's standards.
**Later (patterns established)**: Only ask for corrections that reveal NEW patterns not already covered.

### Corrections file format

`.docs/plans/<name>/corrections.md`:

```markdown
# Corrections Log

Concrete corrections applied during this project.
Implementation agents MUST read this before writing code.

## Naming
- CORRECTION: Agent named method `process_records()`
  → User changed to `stage_crm_sources()`
  LESSON: Use domain-specific verbs (stage, resolve, assemble, publish),
  not generic verbs (process, handle, manage, do).
  WHY: Domain verbs make the code self-documenting. "stage_crm_sources"
  tells you what data source and what operation; "process_records" tells
  you nothing.

## Abstraction Levels
- CORRECTION: Agent wrote SQL query inside `BuildSnapshotService.build()`
  → User extracted to `CrmStager.stage()`
  LESSON: Service layer speaks domain language only. SQL, S3 operations,
  file I/O belong in infrastructure components.
  WHY: When the data source changes (e.g., S3 → database), only the
  stager changes. The service doesn't know or care.

## Types
- CORRECTION: Agent used `dict[str, str]` for snapshot metadata
  → User introduced `SnapshotManifest` dataclass
  LESSON: All data crossing module boundaries must be a named, typed object.
  WHY: Dicts don't catch key errors at development time. A typo in a dict
  key silently produces None; a typo in a dataclass field is a syntax error.

## File Granularity
- CORRECTION: Agent put stager + resolver in same file
  → User split into `staging/crm.py` and `staging/studies.py`
  LESSON: One responsibility per file. If two classes have different
  reasons to change, they go in different files.
  WHY: Smaller files are easier to navigate, review, and test independently.

## Structure
- CORRECTION: Agent eagerly fixed downstream callers after changing an interface
  → User reverted the downstream changes
  LESSON: During horizontal slices, change ONLY the current level.
  Leave downstream breakages for the next level.
  WHY: The downstream design hasn't been decided yet. "Fixing" it now
  is guessing, and the guess will likely be wrong.
```

### The compound learning effect
- First component: User makes 8 corrections → all logged
- Second component: Agent reads corrections → user makes 2 corrections → added
- Third component: Agent reads rich log → user makes 0 corrections → skill has learned

### How implementation agents use the corrections log
Every implementation agent prompt includes:
```
Before writing any code, read the corrections log:
[path to corrections.md]

These are concrete patterns the user has corrected in this project.
Do NOT repeat these mistakes. Each correction includes the LESSON
and WHY — use these to apply judgment in similar situations, not
just to avoid the exact same mistake.
```

## Progressive Autonomy Gradient

The exemplar and corrections set drives the autonomy gradient:

### Bootstrapping (no exemplars, no corrections)
- User involvement: HEAVY
- Every design decision reviewed by user
- Every implementation reviewed by user
- Ask about exemplar marking after each approval
- Ask about correction logging after each change
- Skill behavior: "Here's my proposal for component X. What do you think?"

### Pattern Emerging (1-2 exemplars, corrections accumulating)
- User involvement: MEDIUM
- Propose designs referencing exemplars: "This follows the pattern from builder.py"
- Implement, then show for review
- Fewer correction logging prompts (patterns stabilizing)
- Skill behavior: "I've designed the ModelScoring internals following the SnapshotBuilder pattern. Review?"

### Pattern Established (exemplars cover all layers, corrections log rich)
- User involvement: LIGHT
- Implement autonomously, run challenger, present results
- Only flag items the challenger found concerning
- Skill behavior: "I've implemented ExportActor following established patterns. Challenger found one minor issue (naming). See the review?"

### Autopilot (user explicitly says "go")
- User involvement: MINIMAL
- Implement, challenge, fix, present at natural milestones
- User reviews completed work at their pace
- Skill behavior: "I've completed Level 3 (all infrastructure stagers). 6 components, challenger passed with 2 minor notes. Ready for your review whenever."

### Proposing the shift
The skill proposes increased autonomy when:
- Corrections have dried up (last 2-3 components had 0-1 corrections)
- Exemplars cover the three key layers (orchestration, coordination, infrastructure)
- Challenger findings are consistently minor

Propose explicitly: "We have exemplars covering all three layers and 12 logged corrections. The last two components needed zero corrections. Want me to implement the next batch more autonomously?"

**The user can always pull back**: "Actually, this area is tricky — stay close."
**The user can always push forward**: "Just go, show me when you're done."
