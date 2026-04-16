---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

## Agentic Execution Notes (Claude Opus 4.7)

- **Effort**: Use `xhigh` effort for this skill—Socratic questioning and design-tree traversal benefit from deep reasoning.
- **Batched turns**: Every user turn adds reasoning overhead. When following up, batch related questions rather than sending one at a time.
- **Parallel exploration**: If multiple branches of the design tree can be explored independently via codebase analysis, do so in parallel.

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

If a question can be answered by exploring the codebase, explore the codebase instead.
