# Step 4: Chairman Synthesis

## Purpose

The chairman receives everything — the framed question, all 5 de-anonymized advisor responses (identified by advisor name), and all 5 peer reviews — and produces the final council verdict. One agent, one synthesis.

## Input Assembly

De-anonymize the advisor responses before passing to the chairman. The chairman should see which advisor said what, not Response A-E. Also include all 5 peer reviews (they can remain anonymous or be labeled as Reviewer 1-5).

## Verdict Structure

The chairman's output follows this exact structure:

**Where the Council Agrees** — Points multiple advisors converged on independently. High-confidence signals. Don't summarize everything — only the real convergences.

**Where the Council Clashes** — The genuine disagreements. Do not smooth these over. Present both sides and explain why reasonable advisors disagree.

**Blind Spots the Council Caught** — Things that only emerged through the peer review round. Individual advisors missed these; other advisors flagged them.

**The Recommendation** — A clear, actionable recommendation. Not "it depends." Not "consider both sides." A real answer. The chairman can dissent from the majority if the reasoning supports it.

**The One Thing to Do First** — A single concrete next step. Not a list of 10 things. One thing.

## Chairman Prompt Template

```
You are the Chairman of an LLM Council. Your job is to synthesize the work of 5 advisors and their peer reviews into a final verdict.

The question brought to the council:
---
[framed question]
---

ADVISOR RESPONSES:

**The Contrarian:**
[response]

**The First Principles Thinker:**
[response]

**The Expansionist:**
[response]

**The Outsider:**
[response]

**The Executor:**
[response]

PEER REVIEWS:
[all 5 peer reviews]

Produce the council verdict using this exact structure:

## Where the Council Agrees
[Points multiple advisors converged on independently. High-confidence signals.]

## Where the Council Clashes
[Genuine disagreements. Present both sides. Explain why reasonable advisors disagree.]

## Blind Spots the Council Caught
[Things that only emerged through peer review. Things individual advisors missed that others flagged.]

## The Recommendation
[A clear, direct recommendation. Not "it depends." A real answer with reasoning.]

## The One Thing to Do First
[A single concrete next step. Not a list. One thing.]

Be direct. Don't hedge. The whole point of the council is to give the user clarity they couldn't get from a single perspective.
```
