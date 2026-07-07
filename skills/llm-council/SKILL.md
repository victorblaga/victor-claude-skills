---
name: llm-council
description: >
  Run any question, idea, or decision through a council of 5 AI advisors who independently
  analyze it, peer-review each other anonymously, and synthesize a final verdict. Based on
  Karpathy's LLM Council methodology.
  MANDATORY TRIGGERS: "council this", "run the council", "war room this", "pressure-test this",
  "stress-test this", "debate this".
  STRONG TRIGGERS (use when combined with a real decision or tradeoff): "should I X or Y",
  "which option", "what would you do", "is this the right move", "validate this",
  "get multiple perspectives", "I can't decide", "I'm torn between".
  Do NOT trigger on simple yes/no questions, factual lookups, or casual "should I" without a
  meaningful tradeoff. DO trigger when the user presents a genuine decision with stakes,
  multiple options, and context that suggests they want it pressure-tested from multiple angles.
---

# LLM Council

You ask one AI a question, you get one answer. The council fixes this: it runs your question through 5 independent advisors with fundamentally different thinking lenses, has them peer-review each other anonymously, then a chairman synthesizes everything into a final recommendation. Based on Andrej Karpathy's LLM Council methodology.

## When to Use

**Good questions:** Genuine decisions with stakes, multiple options, meaningful tradeoffs — product direction, pricing, positioning, hiring, pivots.

**Not council questions:** Factual lookups, creation tasks, summarization, casual "should I" without real tradeoffs.

## Execution Notes

- **Effort**: If the harness exposes an effort control, run all advisors and the chairman at the highest tier. Multi-perspective analysis and synthesis are judgment-heavy.
- **Parallel subagents**: Launch all 5 advisors simultaneously in a single turn. Run peer-review subagents in parallel as well — explicitly fan out.
- **Task packaging**: Frame the full question, context, and constraints in the first turn. Avoid progressive revelation across multiple turns; each turn adds reasoning overhead.
- **Literal scope**: Be explicit if a constraint applies broadly (e.g., "Consider this constraint for *all* options, not just the first one").

## The Five Advisors

| Advisor | Angle |
|---------|-------|
| **The Contrarian** | Finds what's wrong, missing, or fatal. Assumes a flaw exists and hunts for it. |
| **The First Principles Thinker** | Ignores the surface question, strips assumptions, rebuilds from ground up. |
| **The Expansionist** | Looks for upside and adjacent opportunity everyone else is missing. |
| **The Outsider** | Zero context. Responds purely to what's in front of them. Catches the curse of knowledge. |
| **The Executor** | Only cares about: can this be done, and what's the fastest path? What do you do Monday morning? |

## Workflow

Read only the step you're entering — do not preload all references upfront.

| Step | What happens | Reference |
|------|-------------|-----------|
| 1 | Frame the question (scan workspace for context, enrich, neutralize) | Read `references/step-1-framing.md` |
| 2 | Convene the council (5 advisors in parallel) | Read `references/step-2-advisors.md` |
| 3 | Peer review (5 reviewers see anonymized responses in parallel) | Read `references/step-3-peer-review.md` |
| 4 | Chairman synthesis (final verdict) | Read `references/step-4-synthesis.md` |
| 5 | Generate HTML report + markdown transcript | Read `references/step-5-output.md` |

## Important Notes

- **Always spawn all advisors in parallel.** Sequential spawning wastes time and lets responses bleed into each other.
- **Always anonymize for peer review.** Reviewers evaluate on merit, not on which thinking style wrote it.
- **The chairman can dissent from the majority.** If the 1 dissenter has the strongest reasoning, side with them.
- **Don't council trivial questions.** If there's one right answer, just answer it.
