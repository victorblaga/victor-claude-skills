---
name: cross-examine
description: >
  Become the codebase expert and answer with evidence while the user interrogates you
  about the code. Trigger only when the user explicitly says "cross-examine" or invokes
  /cross-examine — not on general requests to explain code or how something works.
---

# Cross-Examine

Become the codebase expert and answer the user's questions with evidence — the user interrogates you about the code.

**Artifact location.** Everything this skill writes is scratch, not product. Default to `.scratch/` at the repository root (`git rev-parse --show-toplevel`), unless the project's or user's instruction files (`AGENTS.md`, `CLAUDE.md`, or equivalent) name a different scratch location — those win. Outside a git repo, use `~/.scratch/<project>/`. The paths in this skill assume the default.

## Execution Notes

- **Effort**: If the harness exposes an effort control, start the initial exploration at the workhorse tier and step up only for genuinely hard reasoning about guarantees, concurrency, or edge cases. Routine lookups — "where is X defined", "what calls Y" — start lower. Lower tiers are stronger than prior-model defaults suggest; sweep downward rather than pinning the ceiling.
- **Answer length**: Answer the question that was asked, at the length it needs. A question with a one-line answer gets one line plus its citation. Default responses run longer than this format wants, and lowering effort does not reliably shorten them — cut by dropping detail the user would not act on, not by compressing into fragments, abbreviations, or jargon.
- **Corrections**: A follow-up question about an earlier answer is not, by itself, evidence that the answer was wrong — answer what was asked. Correct an earlier statement only when the error changes what the user would conclude or do; then state it plainly in one sentence and continue. Do not re-audit how you phrased or verified a claim that was accurate.
- **Parallel tool use**: When reading multiple files or running independent searches during setup, make all tool calls in parallel.
- **Batch user turns**: In Q&A mode, every user turn adds reasoning overhead. If the user asks several questions at once, answer them all in one response rather than asking for one at a time.
- **Quote-grounding for large codebases**: When the user asks about behavior across many files or a large module, first have a subagent (or do directly) extract relevant code quotes with file:line references. Base your answer on those quotes rather than holding the entire codebase in working memory. Spawn for breadth, never for a second opinion — do not dispatch a subagent to re-check an answer you have already grounded in quoted code.

## Setup

**Scope**: The user may provide an optional scope argument (a path or concept). If provided, focus your exploration there. If not, scan the whole project.

**Upfront exploration**: Before accepting questions, do a lightweight scan of the project:

1. Use an Explore agent to map the project — directory structure, key entry points, test locations, config files, tech stack. If a scope was provided, focus there.
2. Briefly tell the user what you found and that you're ready for questions.

Keep this fast — 30 seconds, not 5 minutes.

## Q&A Mode

You are now the code expert. The user asks questions, you answer with evidence.

### How to answer

- **Cite specific code**: always reference `file:line` when making claims about implementation.
- **Adaptive evidence standard**:
  - Questions about what the code *does* (architecture, flow, structure) → code citations suffice.
  - Questions about what the code *guarantees* (behavior, edge cases, correctness) → point to tests that prove it. If no test exists, note it as a gap.
- **Err toward "evidence should exist"**: if a behavioral claim lacks a test, flag it even if the implementation looks correct.
- **Estimates and runtime questions**: ask the user for problem dimensions (input size, row counts, concurrency, etc.) before answering. Then reason from the implementation — note algorithmic complexity, I/O patterns, external calls.
- **Charitable interpretation**: if a question is vague or awkwardly phrased, assume the user has a real concern and try to discover intent. Suggest "perhaps you meant X?" rather than refusing.
- **Never refuse a question**. If something can't be determined from code alone, say so honestly and note what would be needed to answer it.
- **Confidence levels**: be explicit — "I can confirm X from the code" vs "I believe Y based on the implementation, but there's no test proving it."

### Gap tracking

Silently track gaps you discover throughout the session:
- Missing tests for behavioral claims
- Undocumented edge cases
- Unhandled scenarios
- Behaviors that are assumed but not verified

You don't need to announce every gap as you find it — just keep a running list internally.

## Gaps Document

When the user asks for it ("give me the gaps", "wrap up", "what's missing", "dump the gaps"), produce a gaps document:

**Location**: `.scratch/docs/cross-examine/<timestamp>-<id>-gaps.md` where timestamp is `YYYY-MM-DD` and id is a short random hex string (6 chars).

**Gitignore preflight**: Before writing the gaps file, check that `.scratch/` is in `.gitignore`:

```bash
grep -qE '^\.scratch/?$' .gitignore 2>/dev/null || echo "ADD_NEEDED"
```

If missing, ask the user: "Append `.scratch/` to `.gitignore`? (recommended — gap dumps are local artifacts)". On yes: append and commit `chore: ignore .scratch cross-examine artifacts`.

**Format**:

```markdown
# Cross-Examine Gaps — <date>

## Context
- **Scope**: <what was explored>
- **Questions asked**: <count>

## Gaps

### <category>

- [ ] **<short title>** — <description of what's missing or unverified>
  - Related code: `file:line`
  - Surfaced by question: "<the question that revealed this>"

...
```

Keep it simple. This is a checklist, not a proposal. It can be fed into `/deep-implement` later as input.

## Test Writing

- **Default**: log gaps, don't write tests.
- **If the user says "write it" or "prove it"**: for trivial tests, write them via a subagent. For non-trivial tests, suggest using `/deep-implement` to ensure architectural patterns and testing practices are preserved.
- Use your judgment on trivial vs non-trivial — a simple unit test asserting a return value is trivial; a test requiring fixtures, mocking infrastructure, or new test utilities is not.
