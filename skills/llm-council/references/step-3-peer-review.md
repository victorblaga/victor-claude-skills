# Step 3: Peer Review

## Purpose

This is the step that makes the council more than "ask 5 times." Each advisor reviews all responses anonymously, which surfaces blind spots no individual advisor would catch. This is the core of Karpathy's insight.

## Anonymization

Before spawning reviewers, anonymize the 5 advisor responses as **Response A through E**. Randomize which advisor maps to which letter — do not use the same mapping every time. This prevents positional bias and forces reviewers to evaluate on merit rather than deferring to familiar thinking styles.

Keep the mapping internally so you can de-anonymize in Step 4.

## The Three Review Questions

Each reviewer sees all 5 anonymized responses and answers:

1. Which response is the **strongest** and why? (pick one)
2. Which response has the **biggest blind spot** and what is it?
3. What did **ALL responses miss** that the council should consider?

## Reviewer Prompt Template

```
You are reviewing the outputs of an LLM Council. Five advisors independently answered this question:

---
[framed question]
---

Here are their anonymized responses:

**Response A:**
[response]

**Response B:**
[response]

**Response C:**
[response]

**Response D:**
[response]

**Response E:**
[response]

Answer these three questions. Be specific. Reference responses by letter.

1. Which response is the strongest? Why?
2. Which response has the biggest blind spot? What is it missing?
3. What did ALL five responses miss that the council should consider?

Keep your review under 200 words. Be direct.
```

## Execution

Spawn all 5 reviewers in a single parallel batch — one per advisor. Each reviewer sees the same set of anonymized responses. Collect all 5 reviews before proceeding to Step 4.
