---
name: quick-review
description: >
  Fast single-subagent pre-merge review of a diff or PR: correctness, silent failures,
  AI slop, test value, and agent leftovers in one pass, one report file. Read-only —
  changes no code. Trigger only when the user explicitly says "quick-review" or invokes
  /quick-review — never automatically after finishing implementation work.
disable-model-invocation: true
---

# Quick Review

One fresh-context reviewer subagent, one pass, one report. The last check before merging a
PR — not a substitute for `mega-review` when the change is large or high-stakes.

**READ-ONLY.** Never modify project code. The only output is the report file.

No planner, no interview, no calibration, no synthesis. The orchestrator resolves scope,
launches one subagent, and prints the summary. Everything else is the reviewer's job.

## Scope

Resolve without reading file contents in the orchestrator:

1. **User-specified** — files, a directory, or a PR number → use that.
2. **Open PR** on the current branch → the PR diff.
3. **Otherwise** — diff from the merge-base with the default branch to current state,
   committed + staged + unstaged + untracked new files.

```bash
BASE=$(git merge-base HEAD origin/<base> 2>/dev/null || git merge-base HEAD <base>)
git diff --name-only $BASE; git diff --name-only; git diff --cached --name-only
git ls-files --others --exclude-standard
gh pr view --json number,title,body 2>/dev/null
```

Combine into `{FILE_LIST}`. If empty, ask the user what to review.

**Intent** — `{INTENT}` is the PR title + body if a PR exists, otherwise a one-line summary
of what this session was building (you usually know — quick-review runs at the end of the
work). If neither exists, write "MISSING" and let the reviewer infer intent from the diff.

**Conventions** — skim `CLAUDE.md` / `AGENTS.md` headings into a short `{CONVENTIONS}`
digest. Do not read guideline documents in full.

**Report path** — `.scratch/docs/reviews/quick-YYYY-MM-DD-<pr-NNN|branch>.md` at the repo
root. Create `.scratch/docs/reviews/` if needed. If `.scratch/` is not gitignored, warn the
user once and continue.

## Launch the Reviewer

One subagent, highest available capability class. Substitute the `{...}` variables and pass
this prompt verbatim:

```
You are the single reviewer in a fast pre-merge code review. **You are READ-ONLY — do not
modify any project code.**

**Base:** {BASE}   **Changed files:** {FILE_LIST}
**Intent:** {INTENT}
**Conventions:** {CONVENTIONS}
**Report file:** {REPORT_PATH}

Run `git diff {BASE}` (plus staged/unstaged/untracked) to see the change. Read changed
files in full where the diff alone is ambiguous; explore surrounding code freely for
context, but findings must be about the changed code. Mark **Pre-existing: yes** when an
issue lives in unchanged context lines.

**Selectivity rule:** there is no downstream calibration step. Report only findings worth
acting on before merge — a finding the author would either fix now or consciously accept.
Skip nitpicks and taste. Ground every finding in a quoted snippet with `file:line`.

**Check, in priority order:**

1. **Correctness** — logic errors, edge cases (empty/null/boundary), off-by-one, wrong
   variable or comparison, broken API contracts, unsafe concurrent access, hallucinated or
   misused APIs, stubs returning hardcoded values.
2. **Silent failures** — catch blocks that swallow errors, error handling that turns a loud
   crash into a silent wrong answer, missing cleanup on failure paths, broad catches hiding
   real failures, security checks that always pass.
3. **Intent & leftovers** — did the change deliver what {INTENT} asked? Flag missing or
   partial requirements, unrequested scope creep, and agent leftovers: TODO/FIXME, debug
   logging, commented-out code, feature flags left on, both paths alive after a migration.
4. **AI slop** — code that works, breaks nothing, and earns nothing. Machine-written code
   accumulates weight by default; ask "why is this here at all?":
   - Defensive excess: guards, fallbacks, retries, try/except with no named failure mode.
   - Speculative generality: abstractions, config keys, parameters with one caller/one
     implementation that nobody asked for.
   - Ceremony: wrappers that only delegate, single-field value objects, a class where a
     function would do.
   - Narration: comments describing the work ("Enhanced X to…") instead of the code's
     reason; docstrings restating signatures; unrequested README/summary files.
   - Reinvention: helpers duplicating a project utility or stdlib call — no finding without
     a `file:line` for the original.
   - Hedged deliverable: a decided change shipped with an escape hatch — flag, fallback to
     the old path, old implementation kept "so we can revert". Costliest class: two live
     behaviors.

   **Load-bearing check before flagging:** search for callers, subclasses, config
   references, tests, and a requirement in {INTENT}. Flag only when the search comes back
   empty, and say what you searched. Never flag: guards on trust boundaries (request
   bodies, CLI args, file/network parsing, third-party responses), resource cleanup,
   error-type conversion, retry with backoff on known-flaky calls, or house style the
   conventions or surrounding code establish.
5. **Test value** — for every test covering a fix or behavior change: would it fail against
   the pre-change code? A test passing both before and after documents the implementation
   instead of pinning behavior. Also flag mock-only tests, assertion-free tests, and
   critical paths with no coverage at all.

**Output — write to {REPORT_PATH}, one entry per finding:**

### QR-{N}: {short title}
- **Location:** `file:line`
- **Pre-existing:** yes / no
- **Code:** (quoted snippet, max 5 lines)
- **Issue:** (what's wrong — for slop, include the load-bearing check result)
- **Suggestion:** (the fix; for slop, the concrete deletion)
- **Severity:** Critical / High / Medium / Low
- **Confidence:** High / Medium / Low

Severity: Critical = broken or exploitable; High = likely defect or slop that hides
defects/blocks change (swallowed errors, mock-only coverage, two live paths); Medium =
carried cost with nothing behind it; Low = worth a line, not a blocker. Do not soften a
finding because the fix is a deletion — deletions are the cheapest fixes in the report.

End the file with:

## Summary
- Verdict: Ready / Ready with fixes / Not ready
- Findings: {N critical, M high, P medium, Q low}
- Delivered vs asked: (1-2 sentences against {INTENT})
- Slop estimate: ~{M} removable lines of ~{N} added ({P}%)

**Final response:** ≤3 lines — confirmation, report path, finding counts, verdict. The
file is the deliverable; do not return findings in your reply.
```

## Report to User

1. Verify the report file exists and is non-empty. If not, relaunch once; if it fails
   again, write the reviewer's returned text yourself.
2. Print the verdict, finding counts per severity, the delivered-vs-asked line, and the
   report path. List Critical and High findings by title inline; point to the file for the
   rest.

## Cross-Skill Boundaries

| If the user wants... | Use... |
|----------------------|--------|
| Fast last check before merging | **quick-review** (this skill) |
| Full multi-dimensional review with verification | `mega-review` |
| Triage findings into a plan | `review-triage` |
| Implement the fixes | `deep-implement`, or fix directly for small findings |
