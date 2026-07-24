# Challenger Protocol

## Purpose
Independent validation of designs and implementations. The challenger is a FRESH-CONTEXT subagent — it has no investment in the work being reviewed, which makes it more honest than self-evaluation.

## When to Run the Challenger

1. **After design** — before user review. Check structural quality of the proposed architecture at this level.
2. **After implementation** — before presenting to user. Check that code matches the design and follows established patterns.
3. **At major milestones** — when enough work has accumulated that context drift is a real risk.

## Grading Criteria

The challenger evaluates against five criteria. Each finding must be CONCRETE — specific file, line, or component reference, not vague observations.

### 1. Abstraction Discipline
Does each component work at one granularity level?

- Orchestrators speak domain language only ("build snapshot", "publish", "notify")
- Infrastructure speaks I/O language only ("stream JSONL", "execute SQL", "batch insert")
- No mixing of levels in the same method

**FAIL examples:**
- SQL query inside a service method
- S3 operations inside an orchestrator
- Business logic inside an infrastructure stager

### 2. Single Responsibility (coordination counts)
Does each component do exactly one thing?

- Coordination is a valid single responsibility — "stage X, then resolve Y, then assemble Z" is ONE purpose (coordinate the pipeline)
- Responsibility sprawl is not — "parse messages AND stage data AND score results AND send notifications" is FOUR responsibilities

**Test:** Can you describe the component in one sentence? Multiple pipeline steps serving one coherent goal is fine. Unrelated concerns joined by "and" is not.

### 3. Typed Boundaries
Do domain types cross every module boundary?

- Named types, not primitives (`Snapshot`, not `str`)
- Dataclasses, not dicts (`SourceMarkers`, not `dict[str, str]`)
- Method signatures with ≤3 parameters (bundle into typed object if more)

**FAIL examples:**
- `dict[str, Any]` in a public interface
- Method with 6 string parameters that could be a single typed object
- Raw tuples crossing module boundaries

### 4. Narrative Readability
Does the code read top-down like a story?

- Each method tells a story: step follows step without jumps
- Domain methods read in domain language
- Infrastructure methods read in infrastructure language
- No mental context-switching required while reading a method

**FAIL examples:**
- Method that starts with business logic, jumps to SQL, back to business logic, then file I/O
- Steps that require reading another file to understand the flow

### 5. Exemplar Conformance
Does the code match established patterns from exemplar files?

- Same naming conventions
- Same layering patterns
- Same type usage patterns
- Same file organization

This criterion only applies when exemplars exist. If no exemplars yet, skip.

**FAIL examples:**
- Exemplar uses actors → services → infrastructure; new code puts SQL in the actor
- Exemplar uses frozen dataclasses for domain types; new code uses dicts
- Exemplar names stagers by source (CrmStager, RegistryStager); new code uses generic names (DataStager1, DataStager2)

## How to Prompt the Challenger

The challenger subagent receives:

```
You are a code structure reviewer. Your job is to find problems, not approve work.

BE SKEPTICAL. LLMs are naturally inclined to be generous toward LLM-generated code.
Fight this tendency. If something is mediocre, say so. If a design is "fine but could
be better," that's a finding, not a pass.

You are reviewing: [design / implementation] at [level N] of a forge construction.

Read these files:
- Plan: .scratch/docs/plans/<name>/plan.md (the target architecture)
- Design principles: [path to design-principles.md]
- Exemplars: .scratch/docs/plans/<name>/exemplars.md (if exists — user-validated reference code)
- Corrections log: .scratch/docs/plans/<name>/corrections.md (if exists — mistakes to avoid)

Then read the code/design being reviewed: [specific files or plan sections]

Evaluate against these criteria:
1. Abstraction discipline — is each component at one granularity level?
2. SRP — does each component do one thing? (coordination counts as one thing)
3. Typed boundaries — do domain types cross every module boundary?
4. Narrative readability — does code read like a story?
5. Exemplar conformance — does it match established patterns? (skip if no exemplars)

For each finding:
- WHAT: The specific problem
- WHERE: File, class, method, line range
- WHY IT MATTERS: Concrete cost (cognitive load, change amplification, type unsafety)
- FIX: Concrete suggestion, not vague ("introduce Snapshot dataclass to replace the 6-param method")

Rate each finding:
- CRITICAL: Will cause bugs or make the next feature significantly harder
- MAJOR: Significant structural improvement, reduces cognitive load meaningfully
- MINOR: Improves clarity but doesn't change structure

Do NOT:
- Approve work that has structural problems just because it "works"
- Use phrases like "overall this is good" — focus on what's wrong
- Suggest stylistic changes (formatting, comment style) — only structural issues
- Praise the code before listing findings — lead with the problems
```

## Output Format

The challenger produces a structured report:

```markdown
## Challenge Report — Level [N] [Design/Implementation]

### Critical
1. `BuildSnapshotService.build()` mixes domain logic with S3 upload at line 45
   → Split into `build()` (domain) + `publish()` (infrastructure)

### Major
2. `process_data()` takes 7 string parameters — introduce `ProcessingConfig` dataclass
3. No domain type for snapshot metadata — `dict[str, str]` crosses 3 module boundaries

### Minor
4. `_handle_result()` name is too generic — `_handle_publish_result()` is more specific

### Pass
- Abstraction discipline: Components at this level all operate at the same granularity ✓
- Narrative readability: Methods read top-down without jumps ✓
```

## Skepticism Tuning

The challenger's natural tendency is to be too lenient. Counter this with:

1. **Lead with problems, not praise.** The challenger report starts with findings, not "overall impressions."
2. **Grade against the standard, not the baseline.** "Better than typical AI-generated code" is not a pass. The standard is the exemplar files and design principles.
3. **Question "fine" assessments.** If the challenger finds nothing wrong, it should re-examine more carefully. Perfect scores are suspicious — there's almost always something to improve.
4. **Calibrate with corrections log.** The corrections log captures the USER's quality bar. If the user previously corrected something similar, a lenient pass is wrong.

## When to Skip the Challenger

- **Trivial scope**: One-file changes where the structure is obvious
- **Leaf implementations**: Pure infrastructure code (SQL queries, S3 operations) where the structure was already validated at the design level
- **User explicitly says skip**: "I'll review this myself, no need for the challenger"

When in doubt, run the challenger. The cost is a subagent call. The cost of missing a structural problem is a rewrite later.
