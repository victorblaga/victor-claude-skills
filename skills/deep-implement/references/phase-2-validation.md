# Phase 2: Proposal Validation

The proposal from Phase 1 was written collaboratively — you and the user built it together, which means you share blind spots. Phase 2 brings independent eyes to catch what you both missed.

## Phase 2.1: Independent Review

Launch a **subagent with fresh context** (model: `opus`) to review the proposal. The subagent receives:
- The proposal document path
- Access to the full codebase
- Access to any architectural docs or knowledge base or notes references mentioned in the proposal

**For review-driven sessions:** The subagent also receives the original mega-review report path (found in the proposal's `Source:` metadata line). In addition to the checks below, it must verify that the proposal faithfully covers all findings from the original report — no findings dropped or misrepresented during transformation.

The subagent's job is to act as a critical reviewer. It should look for:

- **Gaps**: What does the proposal not address that it should? Missing edge cases, error handling, migration paths, rollback strategies?
- **Incorrect assumptions**: Does the proposal assume something about the codebase that isn't true? Are there constraints it doesn't account for?
- **Scope issues**: Is the scope too broad (trying to do too much)? Too narrow (will require immediate follow-up work)? Are there things explicitly out of scope that really should be in scope?
- **Technical risks**: Are there parts of the approach that are risky or uncertain? Dependencies that might not work as expected?
- **Contradictions**: Does the proposal contradict existing architecture decisions, conventions, or constraints?
- **Alternatives**: Are there simpler or better approaches that weren't considered?
- **Completeness**: Could a developer implement this from the proposal alone (plus the codebase), or is critical information missing?

The subagent writes its findings to:
```
docs/plans/<feature-name>/review-findings.md
```

### Review Findings Structure

```markdown
# Review Findings: <Feature Name>

## Critical
Items that would cause the implementation to fail or produce incorrect results.

### Finding 1: <Title>
**Evidence**: File paths, proposal sections, or code references that support the finding
**Issue**: What's wrong
**Impact**: What happens if not addressed
**Recommendation**: Suggested fix
**Status**: unresolved

## Significant
Items that wouldn't break things but would cause real problems (tech debt, poor UX, maintenance burden).

### Finding N: <Title>
...

## Minor
Small improvements, clarifications, or polish.

### Finding N: <Title>
...
```

Each finding gets a **Status** field: `unresolved` → `resolved` (after discussion).

For review-driven sessions, include a `**Source findings**:` field whenever the finding maps to specific mega-review finding IDs or tensions.

Commit the review findings document after creation.
Update `status.md` to `Current phase: 2`, `Current step: 2.1-review-complete`, and `Next action: Discuss review findings`.

## Phase 2.2: Structured Discussion

Present the findings to the user, grouped by severity. Work through them **one at a time**, starting with Critical, then Significant, then Minor.

For each finding:

1. **Present it clearly**: Explain the issue, why it matters, and what could go wrong
2. **Walk through scenarios**: Show concrete examples of how this finding would manifest
3. **Present the recommendation**: What the reviewer suggested, plus any alternatives you see
4. **Discuss trade-offs**: Effort to fix vs. risk of not fixing. Impact on scope and timeline
5. **Ask for a decision**: Does the user agree with the recommendation? Want a different approach? Or consciously accept the risk?

After each finding is discussed:
- Update its **Status** to `resolved` in `review-findings.md`
- Add a **Decision** field with what was decided and why
- Commit the updated document
- Update `status.md` to reflect the current finding being discussed or the next unresolved finding

For minor findings, the user will likely approve quickly — that's fine. Don't artificially extend the discussion, but do present each one so nothing is silently skipped.

### Batch-resolve shortcut

If the user says something like "I trust your judgment, resolve them all" or "handle the rest yourself":
- Work through remaining findings yourself, making reasonable decisions
- Update all statuses to `resolved` with your decisions
- Present a summary: "I resolved the remaining N findings. Here's what I decided: [brief list]"
- The user can still push back on any individual decision

### Fundamental change detected

If during discussion you discover something that changes the proposal fundamentally, flag it: "This finding might change our approach significantly. Should we revisit the proposal before continuing with the remaining findings?"

## Phase 2.3: Amend the Proposal

Once all findings are resolved, apply the decisions to the proposal:

1. Launch a subagent (model: `opus`, or do it yourself if the changes are straightforward) to update `proposal.md` incorporating all resolved findings
2. The changes should reflect the decisions made during Phase 2.2 discussion — not the raw findings, but the agreed-upon resolutions
3. Output a brief summary of what changed: "Updated proposal with: [list of key changes]"
4. Commit the amended proposal

The review findings document stays as-is — it's the historical record of the review process. The proposal is now the source of truth for Phase 3.

Tell the user Phase 2 is complete and the proposal has been amended.
Update `status.md` to `Current phase: 2`, `Current step: 2-complete`, and `Next action: Create the implementation plan`.
