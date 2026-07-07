---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding and resolving each branch of the decision tree. Use when the user wants to stress-test a plan, get grilled on a design, or mentions grill me.
---

# Grill Me

Interview the user relentlessly about every aspect of the plan until you reach shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one by one. For each question, provide your recommended answer.

If a question can be answered by exploring the codebase, explore the codebase instead of asking it.

## Execution Notes

- **Effort**: Use a high reasoning effort — Socratic questioning and design-tree traversal benefit from deep reasoning.
- **Batched turns**: Every user turn adds reasoning overhead. When following up, batch related questions rather than sending one at a time.
- **Parallel exploration**: If multiple branches of the design tree can be explored independently via codebase analysis, do so in parallel.
