# Step 1: Frame the Question

## Purpose

The framed question is what every advisor and reviewer sees. It must include enough context that advisors give specific, grounded advice rather than generic takes. This step has two parts: scan the workspace for context, then frame.

## Part A: Workspace Context Scan

Before framing, quickly scan for context files that would improve council output. Use Glob and Read — spend no more than 30 seconds. Look for:

- `CLAUDE.md` or `claude.md` in the project root or workspace (business context, preferences, constraints)
- Any `memory/` folder (audience profiles, voice docs, business details, past decisions)
- Any files the user explicitly referenced or attached
- Recent council transcripts in the working directory (to avoid re-counciling the same ground)
- Any other files directly relevant to the specific question (pricing data, audience research, launch results, etc.)

You're looking for the 2-3 files that would give advisors the context they need.

## Part B: Frame the Question

Take the user's raw question + enriched context and reframe it as a clear, neutral prompt. Include:

1. The core decision or question
2. Key context from the user's message
3. Key context from workspace files (business stage, audience, constraints, past results, relevant numbers)
4. What's at stake — why this decision matters

Do not add your own opinion. Do not steer it toward an answer. Make the question specific enough that advisors can engage concretely.

**Save the framed question** — it will be passed to all advisors, reviewers, and the chairman.

## Clarifying Questions

If the question is too vague to frame (e.g., "council this: my business"), ask **one clarifying question only**, then proceed. Do not ask multiple questions. Do not ask for permission to proceed after framing.
