# Elicitation Categories

Walk every category, in order. For each, enumerate the decisions made during the audited
work — or write "none". These are probes for *enumeration*: list decisions whether or not
they feel risky.

## 1. Underspecification choices
The task didn't say; you chose. Defaults picked, interpretations settled, behaviors invented.
*Probe: where did the request/plan run out and your judgment take over?*

## 2. Deviations
Places where what you built differs from what was asked or planned — even improvements.
*Probe: if the requester diffed intent vs. outcome, what would surprise them?*

## 3. Symptom vs. root cause
Fixes that address the observed failure rather than the mechanism behind it.
*Probe: would the bug class recur with different inputs? Did you verify the mechanism or
just the case at hand?*

## 4. Coincidental generality
Solutions narrower than the problem — they work for the current case but not the general
one (magic constants, doubled buffers, special-cased paths).
*Probe: what inputs or scales would make this solution stop working?*

## 5. New abstractions, dependencies, files
Anything structural you introduced: layers, helpers, packages, config surface.
*Probe: what now exists that didn't before, and did anyone ask for it?*

## 6. Silent trade-offs
Performance, storage, memory, complexity, or API-shape costs accepted without surfacing
them.
*Probe: what got worse so something else could get better?*

## 7. Abandoned approaches
Things tried and dropped mid-way.
*Probe: why did the first approach fail, and does the final one actually escape that
failure — or just hide it?*

## 8. Test and verification shortcuts
What you verified vs. what you claimed. Skipped tests, narrowed assertions, unverified
paths.
*Probe: which claims in your summary have no evidence behind them?*

# Decision Schema

Record every enumerated decision as:

- **ID**: `D-{n}` (self-report) or `X-{n}` (cross-check)
- **Category**: one of the eight above
- **Location**: `file:line` (or module)
- **Decided**: what was chosen, in one sentence
- **Alternatives**: the plausible options not taken
- **Why**: the reason for the choice as best known
- **Confidence**: high / medium / low (self-report only)
- **Reversibility**: trivial / moderate / hard to undo later
- **Blast radius**: what breaks if this choice is wrong, and how visibly
