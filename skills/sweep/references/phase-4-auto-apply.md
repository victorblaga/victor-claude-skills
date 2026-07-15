# Phase 4 — Auto-apply

Apply all LOW-blast findings in parallel via per-file Applier subagents. Each Applier has veto authority — it can kick a finding back to the triage queue if it sees subtlety the Calibrator missed. **Appliers edit but do not commit**; the orchestrator creates one commit per dimension after all Appliers finish. This yields a clean dimension-grouped history without any reset-and-reword machinery.

## Orchestrator Steps

### 1. Group LOW-blast findings by file

Read `calibration.md`. For each LOW-blast finding, extract `file_path`. Group all LOW-blast findings by file. Build a map:

```
src/foo.py: [DC-3, CS-7, WT-12]
src/bar.py: [DC-5, CS-1]
src/utils/retry.py: [DU-M-2, CS-4, WT-3]
...
```

### 2. Sanity-check the working tree

Run `git status --porcelain` scoped to the target. If in-scope tracked files changed since Phase 1 (user edited during analysis), stop and ask how to proceed. Do not re-run the test suite here — Phase 1's baseline still stands; the post-apply run in step 4 is the verification gate.

Record the current HEAD sha in `status.md` as `auto-apply-start: <sha>` (revert anchor).

### 3. Launch Applier subagents in parallel

For each file with ≥1 LOW-blast finding, launch an Applier agent (mid or small tier, low effort) in parallel. Bound concurrency at 8 parallel Appliers; if there are more files, batch them.

### 4. Commit per dimension, then re-run tests

After all Appliers finish:

1. For each dimension with ≥1 applied finding, stage only the files whose applied findings belong to that dimension (per `auto-apply.md` ledger) and commit. Order (safest first):
   1. `cleanup: remove AI slop and unhelpful comments (N files, M findings)`
   2. `cleanup: remove dead code (N files, M findings)`
   3. `cleanup: tighten weak types (N files, M findings)`
   4. `cleanup: consolidate duplicated logic (N files, M findings)` (if any reached LOW)
   5. `cleanup: consolidate type definitions (N files, M findings)` (if any reached LOW)
   6. `cleanup: remove legacy / fallback code (N files, M findings)` (if any reached LOW)
   7. `cleanup: break circular imports (N files, M findings)` (if any reached LOW)
   8. `cleanup: remove unnecessary defensive code (N files, M findings)` (rare; most DF are HIGH)
2. Files with findings from multiple dimensions appear in only ONE commit: choose the dimension with the most findings in that file; tie-break to the earlier (safer) dimension in the list.
3. Run the baseline test command. If newly red, see "Post-apply verification" below.

### 5. Update status and move to triage

Update `status.md`, announce, read `references/phase-5-triage.md`, proceed.

---

## Applier Agent Prompt

Launch at mid or small tier, low effort, per file. Substitute `{FILE}`, `{FINDING_IDS}`, `{FINDING_DETAILS}` (pull the full finding text for each ID from `calibration.md`), `{OUTPUT_DIR}`.

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

6. **Update ledger.** Append to `{OUTPUT_DIR}/auto-apply.md`:

```markdown
## {FILE}
- Applied: {list of IDs with their dimension prefixes}
- Vetoed: {list of IDs with reasons}
- Timestamp: ISO-8601
```

## Constraints

- **Do not modify any file other than {FILE}.**
- **Do not create new files** (extractions/consolidations are HIGH-blast by definition; they never reach you).
- **Do NOT commit** — the orchestrator commits per dimension after all Appliers finish.
- **Never force-add files or alter .gitignore.**

Report back: number applied, number vetoed, any anomalies.
```

---

## Post-apply Verification

Re-run the baseline test command from Phase 1 (step 4.3 above).

### Green

All good. Update `status.md`:

```markdown
- Phase: auto-apply-complete
- Step: ready-for-triage
- Applied: N findings across F files
- Vetoed (kicked to triage): V findings
- Commits: (list of dimension commit SHAs)
- Post-apply tests: GREEN
- Next action: Phase 5 triage
```

Announce, proceed to Phase 5.

### Newly red (was green at baseline)

Halt. Do NOT auto-revert in interactive mode — the user may want to investigate.

1. Identify the failing test(s) and the offending commit (dimension commits are small; test output usually links to changed files directly, else `git bisect` across them)
2. Interactive mode — present diagnostic to user:
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
   Do not proceed to Phase 5 until the user chooses.
3. Auto mode — apply option 2 autonomously: revert the offending commit, move its findings to `kicked-to-triage.md` with reason "auto-apply broke tests: <failing tests>", re-run tests. If still red after reverting all suspect commits, revert to `auto-apply-start` sha and proceed to Phase 5 with everything re-queued. Record all actions in `status.md`.

### Already red at baseline (Phase 1 recorded red)

Compare failing tests before vs. after: the set of failing tests must be the same (no new failures). If the set changed, treat as "newly red" above even if some were red before.

### No tests

If Phase 1 recorded no test command and the user accepted proceeding without verification, skip this check, update `status.md` with `Post-apply tests: SKIPPED (no test command)`, proceed to Phase 5.

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
- [ ] One commit per dimension with applied findings
- [ ] Baseline tests re-run: GREEN or user-accepted state (auto mode: reverted-and-requeued as needed)
- [ ] `auto-apply.md` ledger complete
- [ ] `kicked-to-triage.md` written if any vetoes
- [ ] `status.md` updated

Announce: *"Phase 4 complete. Applied A findings, V vetoed and kicked to triage. Entering Phase 5 with T total triage findings (HIGH-blast + kicked)."* Read `references/phase-5-triage.md` before proceeding.
