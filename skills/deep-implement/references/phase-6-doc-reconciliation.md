# Phase 6: Documentation & Knowledge Reconciliation

Implementation is validated. Before moving to PR creation, update any project documentation and local knowledge artifacts that the implementation made stale.

## Why this phase exists

Implementations change how systems work, but docs describing those systems do not update themselves. A Postgres-to-DynamoDB migration leaves architecture docs lying about the storage layer. A stack migration from Python plus Airflow to Scala plus Spark makes entire sections of docs describe a system that no longer exists. This phase closes that gap while the implementation context is fresh.

## What gets updated

1. **Architecture and project documentation** - any markdown files in the project that describe how the system works, its tech stack, design decisions, data flow, service boundaries, or operating assumptions.
2. **Local knowledge artifacts** - project-owned instruction or knowledge files that guide future work, for example `CLAUDE.md`, `AGENTS.md`, repo-local skill references, or tool-specific project memory directories if the team keeps them.

**Skip**: system or vendor-managed skill files, harness defaults, operational runbooks, deployment guides, and READMEs unless they contain architecture descriptions.

## Step 1: Discover project documentation

Do not assume fixed paths - each project organizes docs differently. Use a subagent (model: `opus`) to:

1. Search for documentation directories: scan for `docs/`, `documentation/`, `wiki/`, `architecture/`, or similar
2. Extract key concepts from the proposal that changed (technologies, patterns, data flows, service boundaries)
3. Grep across all markdown files in the project for those key concepts
4. Compile a list of files that reference things the implementation changed

Write the discovery result to:

```
.docs/plans/<feature-name>/doc-reconciliation.md
```

Start the file with:

```markdown
# Documentation Reconciliation: <Feature Name>

## Discovery
- Candidate documentation files:
- Candidate knowledge artifacts:
- Notes:
```

If **no documentation is found**:
- Tell the user: I found no architecture or project documentation that describes the areas this implementation changed. Want me to create a baseline architecture doc capturing the current state?
- If the user says yes, create a concise architecture doc based on the implementation and broader codebase understanding. Place it where the project's existing docs live, or `docs/architecture/` as a default.
- If the user says no, note this in the PR description as `No project docs found to update` and move on.
- In either case, record the decision in `doc-reconciliation.md`

## Step 2: Update documentation

Launch a subagent (model: `opus`) with:
- The proposal (`.docs/plans/<feature-name>/proposal.md`)
- The final validation (`.docs/plans/<feature-name>/final-validation.md`)
- The full diff (`git diff <base-branch>...HEAD`)
- The list of discovered doc files to review
- The project's working directory

The subagent should:

1. Read each discovered doc file
2. Identify sections that are now factually incorrect or incomplete due to the implementation
3. **Make edits proportional to the implementation scope:**
   - Small, targeted implementation change -> fix factual inaccuracies
   - Large architectural shift -> rewrite affected sections, update technology references, revise design rationale
   - Use the proposal as the guide for how much changed
4. Preserve the original author's voice and structure - correct the docs, do not rewrite them from scratch unless the change is so large that the original structure no longer makes sense
5. Append a summary of each changed file to `doc-reconciliation.md`
6. Leave the combined documentation and knowledge-artifact changes ready for one final Phase 6 commit

## Step 3: Reconcile local knowledge artifacts

Check for project-level knowledge artifacts outside source code. Good places to inspect:
- `CLAUDE.md`, `AGENTS.md`, and similar instruction files
- Repo-local skill or reference files
- Tool-specific project memory directories, if they exist and are clearly project-owned

For each artifact:

1. Read its content
2. Determine whether the implementation made any of its claims stale
3. If stale: **update** the artifact to reflect the new state
4. If obsolete (describes something removed entirely): **delete** it

Then consider whether the implementation introduced any **key architectural decisions** that do not have a durable home yet. If so, create the smallest durable artifact that fits the repository's existing conventions.

Append all knowledge-artifact changes and any newly created durable artifact to `doc-reconciliation.md`.

Do not edit global or system-managed skills, harness instructions, or vendor defaults unless the user explicitly asks.

## Step 4: Record in PR description

Track what was updated so PR reviewers can see it. The main thread should note:
- Which doc files were updated and a one-line summary of what changed in each
- Which knowledge artifacts were updated, created, or deleted

This list gets included in the PR description in Phase 7 under a `Documentation updates` section.
Commit `doc-reconciliation.md` along with any documentation or knowledge-artifact updates with a message like `Update docs and project knowledge for <feature-name>`, and update `status.md` to `Current phase: 6`, `Current step: phase-6-complete`, and `Next action: Create or update the PR`.
