# Phase 3: Drill-Down

## Purpose

Recursively expand branches of the outline until each leaf node represents a deep module — a unit with a clear interface that hides meaningful complexity. This is where the outline gains depth.

## How It Works

The user points at a component in the outline and says "go deeper on X." The skill then:

1. **Reads the current outline** from disk
2. **Explores the component** — in refactor/migrate mode, reads the existing code for that component. In greenfield mode, asks clarifying questions if needed.
3. **Expands the component's section** — adds sub-components, updates the mermaid diagram for that level, annotates with current code locations
4. **Writes the updated outline** to disk
5. **Presents a summary/diff** of what was added
6. **Asks**: "Want to go deeper on any of these, or move to another branch?"

## Depth Control

### When to stop (default — skill judges)

A node is a leaf when it represents a **deep module**:
- It can be described as "takes X, returns Y, hides Z"
- Its interface is simple enough to specify in a few lines
- The complexity it hides is meaningful but contained
- It maps naturally to a single function, class, or small module

### When to keep going (skill judges)

A node needs further expansion when:
- It contains multiple distinct responsibilities that could be separated
- Its interface is still vague or compound
- It hides heterogeneous complexity that would benefit from internal structure
- It's too large to be one implementation task

### User override

The user can always:
- **"Go deeper on X"** — force expansion of a node the skill considered a leaf
- **"That's enough detail"** — stop expansion of a node the skill would have expanded further
- **"This whole branch is fine"** — mark an entire subtree as done

## Expanding a Node

When expanding a component, add sub-components following the same format as the top-level structure:

```markdown
### <Component>

**Purpose:** <one sentence>
**Current location:** <file paths> (refactor/migrate only)
**Interface:** <inputs, outputs, what callers need to know>
**Hides:** <what complexity is internal>

#### <Sub-component 1>

**Purpose:** <one sentence>
**Current location:** <file paths> (refactor/migrate only)
**Interface:** <inputs, outputs>
**Hides:** <internal complexity>

#### <Sub-component 2>
...
```

For each expanded component, also add or update a **mermaid diagram** showing the internal structure. Use the diagram type that fits:
- **Flowchart** for data/control flow within a workflow
- **Sequence diagram** for interactions between sub-components
- **Block diagram** for containment relationships

## Cross-Cutting Concerns During Drill-Down

As you drill into branches, annotate each sub-component with which cross-cutting concerns it touches:

```markdown
#### <Sub-component>
**Purpose:** ...
**Cross-cutting:** logging, storage, error handling
```

If you discover new cross-cutting patterns during drill-down, update the Cross-Cutting Concerns section of the outline.

## Domain Entities During Drill-Down

As you drill deeper, you'll discover more about the domain entities. Update the Domain Entities table:
- Add new entities discovered at this level
- Refine descriptions of existing entities
- Note which components produce/consume each entity

## Refactor Mode: Current Code Anchors

For each sub-component, annotate where the corresponding logic currently lives:

```markdown
#### <Sub-component>
**Purpose:** Parse incoming SQS messages into domain commands
**Current location:** `src/pipeline/handler.py:45-89`, `src/pipeline/utils.py:12-34`
**Interface:** `parse(raw_message: dict) -> Command`
**Hides:** Message format parsing, validation, error recovery
```

These anchors are essential for the implementor — they show exactly what existing code maps to this node.

## Iteration

Each drill-down round follows the same pattern:
1. User picks a branch
2. Plugin expands it (reading code or asking questions)
3. **Plugin writes the expansion to the plan document on disk** — diagrams, sub-components, everything. Never present new structure only in conversation.
4. Plugin presents a brief summary of what was added
5. User gives feedback or picks the next branch

The user can also:
- Give feedback on expanded sections ("this should be structured differently")
- Ask the skill to re-expand a section with different decomposition
- Go back up and restructure a parent node (changes cascade — the skill updates children)

## Higher-level reorganization during drill-down

It is normal and expected that drilling into components reveals that the top-level structure needs to change. For example, zooming into a 10-phase pipeline might reveal it's better organized as 3 macro phases with parallel tracks.

When this happens:
1. **Embrace it** — this is the design process working correctly. The initial outline was a hypothesis; drill-down tests it.
2. **Update the top-level diagram and structure** to reflect the new understanding.
3. **Mark superseded sections** with a blockquote note rather than deleting them — they document the current code structure even if the target architecture has evolved. Use this format:
   ```markdown
   > **Note:** This section was written against the original <X> architecture. The target has since evolved to <Y>. Retained as reference for the current code structure.
   ```
4. **Don't fight it** — if the user proposes a reorganization, update the document to reflect it. The plan must always represent the current best understanding.

## Consistency reviews

As the document evolves through multiple drill-down rounds, diagrams and text can drift out of sync. Periodically (every 3-4 drill-down rounds, or when the user asks):

1. **Read the full document** end to end
2. **Flag inconsistencies** — text that references old diagram labels, stale component descriptions, contradictions between sections
3. **Fix them in one pass** — update the document on disk, then summarize what changed

Common drift patterns:
- Diagram labels updated but text descriptions still reference old names
- Component listed as "no changes" but later sections describe changes to it
- Domain entities table missing new entities introduced during drill-down
- Dead code section contradicting "modules with no changes" section

## Implementation sketches for complex components

When drilling into a component that involves non-obvious algorithms, data flow, or streaming patterns, include a **target implementation sketch** directly in the plan document. This is not pseudo-code — it's real, runnable code that validates the design is feasible.

Good candidates for implementation sketches:
- Streaming/pipeline compositions (generators, iterators)
- Algorithm outlines (union-find, graph construction, connected components)
- Query interface contracts (class with method signatures + docstrings)
- Complex state machines

Keep sketches focused — show the composition and data flow, not error handling or logging. The goal is to verify the design works, not to write production code.

## Completion

When all branches are expanded to leaf depth (or the user is satisfied), the skill announces:

"The outline is complete. All branches are at leaf depth. You can:
- Review the full outline in your editor at `<path>`
- Ask me to adjust any section
- Hand off to `/deep-implement` to plan and execute the implementation"

The skill suggests the `/deep-implement` handoff command but does not auto-invoke it.

## Greenfield Drill-Down

In greenfield mode, there's no code to read. When expanding a node:
1. Use the description from the parent level
2. Ask clarifying questions if the sub-structure isn't obvious from context
3. Propose a decomposition based on the design principles (deep modules, information hiding)
4. Let the user confirm or adjust

Keep questions minimal — propose first, adjust after feedback. Don't turn every expansion into an interview.
