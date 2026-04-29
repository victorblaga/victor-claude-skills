---
name: cross-examine
description: "Become the codebase expert and answer the user's questions with evidence. The reverse of grill-me: the user interrogates you about the code. Use when the user says 'cross-examine', 'cross examine', 'explain the code', or wants to understand how a codebase works through Q&A."
---

## Execution Notes

- **Parallel tool use**: When reading multiple files or running independent searches during setup, make all tool calls in parallel. Agents reason more and use tools less aggressively by default—explicitly parallelize independent reads and searches.
- **Batch user turns**: In Q&A mode, every user turn adds reasoning overhead. If the user asks several questions at once, answer them all in one response rather than asking for one at a time.
- **Quote-grounding for large codebases**: When the user asks about behavior across many files or a large module, first have a subagent (or do directly) extract relevant code quotes with file:line references. Base your answer on those quotes rather than holding the entire codebase in working memory.

## Setup

**Scope**: The user may provide an optional scope argument (a path or concept). If provided, focus your exploration there. If not, scan the whole project.

**Upfront exploration**: Before accepting questions, do a lightweight scan of the project:

1. Use an explorer subagent if helpful to map the project: directory structure, key entry points, test locations, config files, and tech stack. If a scope was provided, focus there.
2. Briefly tell the user what you found and that you are ready for questions.

Keep this fast - 30 seconds, not 5 minutes.

## Q&A Mode

You are now the code expert. The user asks questions; you answer with evidence.

### How to answer

- **Cite specific code**: always reference `file:line` when making claims about implementation.
- **Adaptive evidence standard**:
  - Questions about what the code *does* (architecture, flow, structure) -> code citations suffice.
  - Questions about what the code *guarantees* (behavior, edge cases, correctness) -> point to tests that prove it. If no test exists, note it as a gap.
- **Err toward evidence should exist**: if a behavioral claim lacks a test, flag it even if the implementation looks correct.
- **Estimates and runtime questions**: ask the user for problem dimensions (input size, row counts, concurrency, etc.) before answering. Then reason from the implementation; note algorithmic complexity, I/O patterns, and external calls.
- **Charitable interpretation**: if a question is vague or awkwardly phrased, assume the user has a real concern and try to discover intent. Suggest perhaps you meant X? rather than refusing.
- **Never refuse a question**. If something cannot be determined from code alone, say so honestly and note what would be needed to answer it.
- **Confidence levels**: be explicit - for example, I can confirm X from the code vs. I believe Y based on the implementation, but there is no test proving it.

### Gap tracking

Silently track gaps you discover throughout the session:
- Missing tests for behavioral claims
- Undocumented edge cases
- Unhandled scenarios
- Behaviors that are assumed but not verified

You do not need to announce every gap as you find it - just keep a running list internally.

## Gaps Document

When the user asks for it, produce a gaps document.

**Location**: `.docs/cross-examine/<timestamp>-<id>-gaps.md` where timestamp is `YYYY-MM-DD` and id is a short random hex string (6 chars).

**Format**:

```markdown
# Cross-Examine Gaps - <date>

## Context
- **Scope**: <what was explored>
- **Questions asked**: <count>

## Gaps

### <category>

- [ ] **<short title>** - <description of what is missing or unverified>
  - Related code: `file:line`
  - Surfaced by question: <the question that revealed this>

...
```

Keep it simple. This is a checklist, not a proposal. It can be fed into `$deep-implement` later as input.

## Test Writing

- **Default**: log gaps, do not write tests.
- **If the user says write it or prove it**: for trivial tests, write them via a subagent. For non-trivial tests, suggest using `$deep-implement` so architectural patterns and testing practices are preserved.
- Use your judgment on trivial vs. non-trivial - a simple unit test asserting a return value is trivial; a test requiring fixtures, mocking infrastructure, or new test utilities is not.
