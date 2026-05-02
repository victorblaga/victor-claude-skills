# Phase 4 — Auto-apply

Apply all LOW-blast findings in parallel via per-file Applier subagents. Each Applier has veto authority — it can kick a finding back to the triage queue if it sees subtlety the Calibrator missed.

## Orchestrator Steps

### 1. Group LOW-blast findings by file

Read `calibration.md`. For each LOW-blast finding, extract `file_path`. Group all LOW-blast findings by file. Build a map:

```
src/foo.py: [DC-3, CS-7, WT-12]
src/bar.py: [DC-5, CS-1]
src/utils/retry.py: [DU-M-2, CS-4, WT-3]
...
```

### 2. Ensure baseline tests are still green (safety check)

Re-run the baseline test command from Phase 1. If red, abort auto-apply — something changed between Phase 1 and Phase 4 (rare, but possible if the user edited files during analysis). Report and ask user how to proceed.

### 3. Launch Applier subagents in parallel

For each file with ≥1 LOW-blast finding, launch a subagent on the latest available Codex model with `reasoning_effort: low` in parallel. Bound concurrency at 8 parallel Appliers; if there are more files, batch them.

### 4. Reword commits after all Appliers finish

After all per-file commits exist, rebase-reword to dimension-grouped commits (see "Commit Reword" below).

### 5. Re-run tests after auto-apply

Run baseline test command again. If newly red, halt — see "Post-apply verification" below.

### 6. Update status and move to triage

Update `status.md`, announce, read `references/phase-5-triage.md`, proceed.

---

## Applier Agent Prompt

Launch on the latest available Codex model with `reasoning_effort: "low"` per file. Substitute `{FILE}`, `{FINDING_IDS}`, `{FINDING_DETAILS}` (pull the full finding text for each ID from `calibration.md`), `{OUTPUT_DIR}`.

```
You are a sweep Applier. You apply pre-analyzed, pre-calibrated LOW-blast findings to a single file. You have veto authority to reject individual findings back to triage if you see subtlety the Calibrator missed.

**File to modify:** {FILE}
**Findings to apply:** {FINDING_IDS}

**Full finding details:**
{FINDING_DETAILS}

**Output ledger:** {OUTPUT_DIR}/auto-apply.md (append your per-file block; do NOT overwrite)

## Workflow

1. **Read the file in full.** Understand surrounding context before touching anything.

2. **Read each finding.** For each one, locate the exact code described, verify the Calibrator's diagnosis matches what you see.

3. **Veto check.** Before applying, for each finding ask:
   - Does this fix actually apply cleanly here, or has the surrounding code shifted?
   - Does the proposed fix have a subtle dependency I see that the Calibrator missed?
   - Will this fix compile / parse / not break imports?
   - If I'm unsure — VETO.
   
   For any vetoed finding: add to the `kicked-to-triage.md` file at `{OUTPUT_DIR}/kicked-to-triage.md` with ID, location, and reason for veto. Do not apply it.

4. **Apply non-vetoed findings.** Order within the file: apply from the bottom of the file upward (so line numbers for upper findings don't shift). If two findings affect the same line range, apply them as a single coordinated edit.

5. **Verify the file still parses / type-checks locally** (if a cheap check is available — `python -c "import ast; ast.parse(open('{FILE}').read())"` for Python, `tsc --noEmit {FILE}` for TS). If broken, revert your file edits and veto the problem finding.

6. **Commit** with message: `cleanup/{FILE}: N findings applied ({comma-separated IDs})`

7. **Update ledger.** Append to `{OUTPUT_DIR}/auto-apply.md`:

```markdown
## {FILE}
- Applied: {list of IDs}
- Vetoed: {list of IDs with reasons}
- Commit: {commit sha}
- Timestamp: ISO-8601
```

## Constraints

- **Do not modify any file other than {FILE}.**
- **Do not create new files** (extractions/consolidations are HIGH-blast by definition; they never reach you).
- **Never force-add files or alter .gitignore.**
- **If git is dirty with unrelated changes at the start of your run, abort and report.**
- **Commit only your own changes.**

Report back: number applied, number vetoed, commit sha, any anomalies.
```

---

## Commit Reword (after all Appliers finish)

Per-file commits are a noisy git history. Squash into one commit per dimension for a clean PR review surface.

### Steps

1. Count commits to reword:
   ```bash
   git log --oneline <start-commit>..HEAD
   ```
   where `<start-commit>` is the HEAD at the start of Phase 4 (record this in `status.md` before launching Appliers).

2. For each finding dimension, compute:
   - Total findings applied from that dimension
   - List of files touched
   
   Use `auto-apply.md` as the source of truth.

3. Perform a soft reset + split-commit:
   ```bash
   git reset --soft <start-commit>
   ```
   All changes are now staged.

4. Create dimension-grouped commits. For each dimension with ≥1 applied finding, stage only files touched by that dimension, then commit:
   ```bash
   # For Dead Code dimension — files from auto-apply.md where DC findings were applied
   git reset HEAD  # unstage all
   git add <files-touched-by-DC>
   git commit -m "cleanup: remove dead code (N files, M findings)"
   ```
   
5. Repeat for each dimension. Commit order suggestion (low-risk → high-risk within LOW-blast pool):
   1. `cleanup: remove AI slop and unhelpful comments (N files, M findings)` — safest first
   2. `cleanup: remove dead code (N files, M findings)`
   3. `cleanup: tighten weak types (N files, M findings)`
   4. `cleanup: consolidate duplicated logic (N files, M findings)` (if any reached LOW)
   5. `cleanup: consolidate type definitions (N files, M findings)` (if any reached LOW)
   6. `cleanup: remove legacy / fallback code (N files, M findings)` (if any reached LOW)
   7. `cleanup: break circular imports (N files, M findings)` (if any reached LOW)
   8. `cleanup: remove unnecessary defensive code (N files, M findings)` (if any reached LOW — rare; most DF are HIGH)

6. Handle files with findings from multiple dimensions: the file appears in only ONE commit. Choose the dimension with the most findings in that file, or the earliest dimension in the list above (tie-break to safer).

### Caveat

Reset-and-recommit is a power move. If anything goes wrong (merge conflicts from mid-sweep user edits, hook failures), abort the reword, keep the per-file commits, document in `status.md`. A clean per-file history is still acceptable.

---

## Post-apply Verification

Re-run the baseline test command from Phase 1.

### Green

All good. Update `status.md`:

```markdown
- Phase: auto-apply-complete
- Step: ready-for-triage
- Applied: N findings across F files
- Vetoed (kicked to triage): V findings
- Commits: (list of reworded commit SHAs)
- Post-apply tests: GREEN
- Next action: Phase 5 triage
```

Announce, proceed to Phase 5.

### Newly red (was green at baseline)

Halt. Do NOT auto-revert — the user may want to investigate.

1. Identify the failing test(s) and the offending commit via `git bisect` across the reworded commits (or just by test output linking back to changed files)
2. Present diagnostic to user:
   ```
   Post-apply tests went red. This is unexpected.
   
   Failing tests: <list>
   Offending commit: <sha> <message>
   Files changed in that commit: <list>
   Findings in that commit: <IDs>
   
   Options:
   1. Investigate with me interactively — I can read failing tests and trace the failure
   2. Revert the offending commit and re-queue those findings to triage
   3. Revert the entire auto-apply batch and proceed to triage only
   4. Abort the sweep here
   ```

3. Do not proceed to Phase 5 until the user chooses.

### Already red at baseline (Phase 1 recorded red)

Compare failing tests before vs. after: the set of failing tests must be the same (no new failures). If the set changed, treat as "newly red" above even if some were red before.

### No tests

If Phase 1 recorded no test command and user accepted proceeding without verification, skip this check, update `status.md` with `Post-apply tests: SKIPPED (no test command)`, proceed to Phase 5.

---

## Kicked-to-Triage File

If any Applier vetoes findings, they write to `{OUTPUT_DIR}/kicked-to-triage.md`:

```markdown
# Findings kicked from auto-apply to triage

## DC-M-4 — (kicked by Applier on src/foo.py)
- **Location:** src/foo.py:142
- **Original Calibrator verdict:** LOW
- **Applier veto reason:** The "unused" function `_cleanup` is referenced dynamically via `getattr(module, fname)` in src/plugin_loader.py:33. Removing it would break plugin loading.

## CS-19 — (kicked by Applier on src/bar.py)
- ...
```

In Phase 5, prepend these kicked findings to the triage queue (they're HIGH-blast by virtue of being vetoed — the Applier saw something the Calibrator didn't).

---

## Phase 4 Exit Criteria

- [ ] All LOW-blast findings processed (applied or vetoed)
- [ ] Commit reword complete (or per-file commits accepted as fallback)
- [ ] Baseline tests re-run: GREEN or user-accepted state
- [ ] `auto-apply.md` ledger complete
- [ ] `kicked-to-triage.md` written if any vetoes
- [ ] `status.md` updated

Announce: *"Phase 4 complete. Applied A findings, V vetoed and kicked to triage. Entering Phase 5 with T total triage findings (HIGH-blast + kicked)."* Read `references/phase-5-triage.md` before proceeding.
