# Phase 4c: Documentation & Memory Reconciliation

Implementation is validated. Before moving to PR creation, update any project documentation and Claude memory that the implementation has made stale.

## Why this phase exists

Implementations change how systems work, but docs describing those systems don't update themselves. A Postgres-to-DynamoDB migration leaves architecture docs lying about the storage layer. A stack migration from Python+Airflow to Scala+Spark makes entire sections of docs describe a system that no longer exists. This phase closes that gap while the implementation context is fresh.

## What gets updated

1. **Architecture and project documentation** — any markdown files in the project that describe how the system works, its tech stack, design decisions, data flow, etc.
2. **Claude memory** — project-type memories in the project's memory directory that describe aspects of the system that changed.

**Skip**: `CLAUDE.md` (tooling config, not project knowledge), READMEs (unless they contain architecture descriptions), operational runbooks, deployment guides.

## Step 1: Discover project documentation

Don't assume fixed paths — each project organizes docs differently. Use a subagent (opus) to:

1. Search for documentation directories: scan for `docs/`, `documentation/`, `wiki/`, `architecture/`, or similar
2. Extract key concepts from the proposal that changed (technologies, patterns, data flows, service boundaries)
3. Grep across all markdown files in the project for those key concepts
4. Compile a list of files that reference things the implementation changed

If **no documentation is found**:
- Tell the user: "I found no architecture or project documentation that describes the areas this implementation changed. Want me to create a baseline architecture doc capturing the current state?"
- If the user says yes, create a concise architecture doc based on the implementation and broader codebase understanding. Place it where the project's existing docs live, or `docs/architecture/` as a default.
- If the user says no, note this in the PR description ("No project docs found to update") and move on.

## Step 2: Update documentation

Launch an **opus subagent** with:
- The proposal (`docs/plans/<feature-name>/proposal.md`)
- The final validation (`docs/plans/<feature-name>/final-validation.md`)
- The full diff (`git diff <base-branch>...HEAD`)
- The list of discovered doc files to review
- The project's working directory

The subagent should:

1. Read each discovered doc file
2. Identify sections that are now factually incorrect or incomplete due to the implementation
3. **Make edits proportional to the implementation scope:**
   - Small, targeted implementation change → fix factual inaccuracies (e.g., "PostgreSQL" → "DynamoDB")
   - Large architectural shift → rewrite affected sections, update technology references, revise design rationale
   - Use the proposal as the guide for how much changed
4. Preserve the original author's voice and structure — correct the docs, don't rewrite them from scratch (unless the change is so large that the original structure no longer makes sense)
5. Commit doc updates with a message like: "Update project docs to reflect <feature-name> changes"

## Step 3: Reconcile Claude memory

Check the project's memory directory for existing memories. For each memory file:

1. Read its content
2. Determine if the implementation made any of its claims stale
3. If stale: **update** the memory to reflect the new state
4. If obsolete (describes something that was removed entirely): **delete** it

Then consider whether the implementation introduced any **key architectural decisions** that don't have a memory yet. If so, create new `project`-type memories. Good candidates:
- Technology migrations (what changed, why)
- New architectural patterns introduced
- Significant design decisions and their rationale

Don't create memories for routine implementation details — only decisions that would meaningfully inform future work.

## Step 4: Record in PR description

Track what was updated so PR reviewers can see it. The main thread should note:
- Which doc files were updated and a one-line summary of what changed in each
- Which memories were updated/created/deleted

This list gets included in the PR description in Phase 5 (under a "Documentation updates" section).
