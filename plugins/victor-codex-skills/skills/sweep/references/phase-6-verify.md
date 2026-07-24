# Phase 6 — Verify

Final correctness gate before declaring the sweep complete. Runs the full CI-equivalent check suite; if red, enters a bounded fix cycle; escalates to the user after 3 failed attempts.

## What "CI-equivalent" means

In Phase 1, the baseline test command was recorded. CI-equivalent extends that with any additional checks the project runs in CI. Inspect:

| Project signal | CI-equivalent additions |
|---------------|-------------------------|
| `.github/workflows/*.yml` | Parse each job; collect test + lint + type-check + build commands |
| `.gitlab-ci.yml` | Same |
| `Makefile` with `check` / `ci` / `test` targets | Use those |
| Python: `pre-commit-config.yaml` | Run `pre-commit run --all-files` |
| TypeScript: `package.json` scripts `test`, `lint`, `typecheck`, `build` | Run all present |
| Rust: `cargo test` + `cargo clippy` + `cargo fmt --check` | Run all present |

Announce the detected command list and run it — do not wait for confirmation. Ask only if detection is ambiguous (e.g., conflicting CI configs) or a command looks destructive/expensive (e.g., a deploy step in the workflow — skip those and say so).

```
Running CI-equivalent checks:
  1. pytest
  2. ruff check .
  3. mypy --strict .
  4. pre-commit run --all-files
(adjust with "skip N" / "add <cmd>" if needed)
```

## Run CI-equivalent

Execute the command list in order. Collect pass/fail per command, full output on failure.

### All pass

Announce: *"Phase 6 complete. All CI-equivalent checks pass. Entering Phase 7."*
Update `status.md`:
```markdown
- Phase: verify-complete
- Step: ready-for-final-report
- CI-equivalent: GREEN
- Next action: Phase 7 report
```

Read `references/phase-7-report.md`, proceed.

### Any command fails

Enter the CI Fix Cycle (interactive) or the Auto-Mode Fix Cycle (auto).

## Auto-Mode Fix Cycle

In auto mode, red CI resolves autonomously — the sweep must never end waiting on a human:

1. Identify the suspect finding-commit (Phase 5 accepts are one commit per finding, so `git bisect` or test-output-to-file mapping localizes quickly).
2. Revert it, mark the finding `⏸ deferred (reverted in Phase 6: <failing check>)` in `triage.md`, re-run the failing command.
3. Repeat up to 3 reverts. If still red, revert all remaining Phase 5 accept-commits (auto-apply commits from Phase 4 stay — they passed their own post-apply run) and re-run.
4. If red even then, the failure predates or is unrelated to Phase 5: record `Phase: verify-failed` with full diagnostics in `status.md` and the report, and stop. The branch retains whatever verified state was reached.

Every revert-and-defer is recorded in `triage.md` and surfaces in the report's "for human review" section.

## CI Fix Cycle (interactive)

Bounded at 3 attempts. Each attempt is a diagnose → fix → re-run loop.

### Attempt 1

1. Read the full failure output
2. Identify the root cause — which commit/finding most likely caused the failure?
3. Propose a fix: either (a) a small code change to resolve the failure, or (b) reverting a specific commit
4. Present to user:
   ```
   CI failure attempt 1:
   
   Failing command: <cmd>
   Root cause (best guess): <one sentence>
   Likely culprit commit: <sha> <message>
   
   Proposed fix:
   A. Apply this small change: <diff>
   B. Revert the culprit commit
   C. I want to investigate manually
   
   ```
5. Apply the user's chosen approach, re-run CI-equivalent

### Attempts 2 and 3

Same loop, but note "Attempt 2" / "Attempt 3" prominently in the announcement. Try a different angle from Attempt 1 if it didn't work.

### After 3 failed attempts — escalate

```
CI fix cycle exhausted after 3 attempts.

Full diagnostic:
- Failing commands: <list>
- Attempts tried:
  1. <what was tried, why it didn't work>
  2. <what was tried, why it didn't work>
  3. <what was tried, why it didn't work>
- Current state: <branch, last commit, list of findings applied>

The sweep is in a broken-tests state on branch <name>. Options:
- Investigate manually; you can resume Phase 6 by re-running the skill on this branch.
- Revert all sweep commits to dev and abandon: `git reset --hard <start-commit>`
- Keep the sweep commits and manually fix CI in a follow-up.

I will not take further action automatically.
```

Do NOT proceed to Phase 7 in a red state. Update `status.md` with `Phase: verify-failed, Step: ci-fix-cycle-exhausted` and stop.

## Known-red baseline handling

If Phase 1 recorded baseline tests as red (user accepted proceeding), the comparison is: was the set of failing tests the *same* at baseline as after the sweep? Use this command to compare:

```bash
# Phase 1 baseline captured: .scratch/docs/cleanup/<session>/baseline-test-failures.txt
diff <(sort .scratch/docs/cleanup/<session>/baseline-test-failures.txt) <(sort current-failures.txt)
```

If the diff is empty: treat as "all pass" for the purposes of declaring Phase 6 green.
If the diff shows new failures: enter CI Fix Cycle focused on the new failures only.
If the diff shows fewer failures: celebrate, but still the baseline failures are allowed.

## Skip when no tests

If Phase 1 recorded "no test command", Phase 6 is limited to whatever the CI config provides (lint, type-check, build). If the project has neither tests nor CI config, Phase 6 is a no-op — announce the skip:

```
Phase 6 skipped: no test command and no CI config detected. The sweep's correctness was not automatically verified. Recommend manual verification before merging.
```

Update `status.md` with `CI-equivalent: SKIPPED (no verification available)`. Proceed to Phase 7.

## Phase 6 Exit Criteria

- [ ] CI-equivalent commands detected and announced
- [ ] All commands pass OR user accepted a partial-pass state OR skip-without-verification accepted OR (auto mode) revert-and-defer restored green / recorded verify-failed
- [ ] `status.md` reflects outcome
- [ ] If CI Fix Cycle engaged: either resolved green or escalated (interactive) / recorded with diagnostics (auto)
