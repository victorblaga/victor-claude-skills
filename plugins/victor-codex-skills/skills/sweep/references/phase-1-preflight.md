# Phase 1 — Preflight

Preflight protects against losing work, sweeping the wrong branch, and producing an unverifiable sweep — without blocking on irrelevancies. Compute everything first, then present **one consolidated confirmation** (interactive mode) or announce decisions and proceed (auto mode).

The only hard block is uncommitted changes to tracked files inside the sweep scope. Everything else is a default the user can override in the single confirmation.

## Steps

### 1. Scope-aware git check

```bash
git status --porcelain
```

Classify each entry:

| Entry | Classification | Effect |
|-------|---------------|--------|
| Modified/staged **tracked file inside sweep scope** | Blocking | Must be resolved before Phase 2 |
| Modified/staged tracked file **outside scope** | Non-blocking | Note it; sweep won't touch it |
| Untracked file (any location — images, notes, scratch artifacts) | Non-blocking | Note it; sweep only edits tracked source files |

If blocking entries exist: show them and offer (a) stash, (b) commit to current branch, (c) abort. Do not proceed with blocking entries unresolved. In auto mode with blocking entries: stash with a named stash (`sweep-preflight-YYYY-MM-DD`) and announce it in `status.md` and the report.

Non-blocking entries: list them in the confirmation card ("N unrelated dirty files — untouched by sweep") and proceed.

### 2. PR-aware branch decision

Never default to the project's integration branch (`main`, `master`, `dev`, `staging`).

1. **Detect PR context** (in order):
   - `gh pr view --json number,state,baseRefName 2>/dev/null` — if it returns an OPEN PR for the current branch, this is a PR branch.
   - If `gh` is unavailable or not a GitHub remote, use the heuristic: current branch is not an integration branch, has upstream tracking, and is ahead of the merge-base with the integration branch → treat as a likely PR branch (announce it as inferred).
2. **On a PR branch** → continue on it. No prompt. Announce: *"Continuing on PR branch `<name>` (PR #123)."* Mention the PR in the scope summary so the user can narrow scope to the PR diff with one word.
3. **Not on a PR branch** (integration branch, detached HEAD, or no PR signal) → default to a **new branch from the current branch**: `cleanup/YYYY-MM-DD-<slug>` (`<slug>` = 5 random alphanumerics). Present this as the pre-selected default in the confirmation card; the user can rename it or choose to stay on the current branch. Branching from the integration base is available only if the user explicitly asks.
4. In auto mode: apply the same logic without prompting (PR branch → stay; otherwise → new `cleanup/...` branch from current).

If staying on an integration branch is the user's explicit choice, warn once and honor it.

### 3. `.scratch` gitignore check (silent)

```bash
grep -qE '^\.scratch/?$' .gitignore 2>/dev/null
```

If absent, append `.scratch/` to `.gitignore` and commit with `chore: ignore .scratch sweep session dir`. Note the action in the confirmation card — do not ask a standalone question.

### 4. Language detection

Detect languages present in the target scope:

```bash
# marker files
find . -maxdepth 3 \( -name "pyproject.toml" -o -name "setup.py" -o -name "requirements.txt" -o -name "package.json" -o -name "Cargo.toml" -o -name "go.mod" -o -name "build.sbt" -o -name "build.sc" \) -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null
```

Combine with file-extension counts via `find`/`wc` to rank languages by LoC. Record in `scope.md`.

### 5. Silent tool probe (no install prompts)

For each detected language, probe the tools in `references/tool-registry.md` with `command -v` / version checks. **Do not offer installs** — modern LLM-only analysis is an adequate fallback. Record availability in `scope.md`; each dimension agent notes gaps per the degradation policy. If the user explicitly asks for a tool install, honor it per the registry's install-scope rules.

Run available tools now and save output to `.scratch/docs/cleanup/<session>/tool-output/` per the registry's ingestion section (after session init in step 8; order the steps accordingly).

### 6. Baseline test run

Detect test command from project conventions:

| Marker | Likely test command |
|--------|---------------------|
| `pyproject.toml` with `[tool.pytest.ini_options]` | `pytest` |
| `package.json` with `"test"` script | `npm test` or `yarn test` |
| `Cargo.toml` | `cargo test` |
| `build.sbt` | `sbt test` |
| `go.mod` | `go test ./...` |

If detection is unambiguous, run it without asking; include the command in the confirmation card. Ask only when detection is ambiguous or fails. Record result:

- **Passing** → record baseline as green, proceed
- **Failing** → show failures. Interactive: ask *"Tests are red at baseline. Is this known? Proceed (we'll compare post-apply against this baseline) or abort?"* Auto mode: record the failing set to `baseline-test-failures.txt`, proceed with baseline-red comparison semantics.
- **No tests found** → warn loudly. Interactive: ask whether to proceed without post-apply verification. Auto mode: proceed, but Phase 5's Adjudicator must then defer **all** HIGH-blast findings (no verification safety net = nothing unsupervised gets accepted).

Record the baseline command and result in `scope.md`.

### 7. Sharding decision

Estimate scope size (`find <scope> -name '*.<ext>' | xargs wc -l` style, rough is fine).

- **≤ ~50k LoC in scope** → **dimension-sharded** (default): 4 agents, each owning 2-3 dimensions, whole-scope visibility (needed for cross-file duplication).
- **> ~50k LoC** → **area-sharded**: N agents by directory subtree, each running *all* dimension checklists on its area, so the codebase is read once in total instead of 4×. See Phase 2 for the variant.

Record the decision in `scope.md`. The user can override in the confirmation card.

### 8. Consolidated confirmation

Interactive mode — present ONE card and wait for go/adjust:

```
Sweep preflight summary:

  Branch:     continuing on PR branch `feature/x` (PR #123)          [or: new branch cleanup/2026-07-15-a3f9x from `feature/x`]
  Scope:      whole repo minus tests/generated/vendored/migrations   [PR detected — say "diff" to narrow to the PR diff]
  Mode:       interactive triage                                     [or: AUTO — subagent adjudication, accept/defer only]
  Sharding:   dimension-sharded, 4 agents                            [or: area-sharded, N agents (repo > 50k LoC)]
  Git state:  2 unrelated dirty files (untouched by sweep): photo.png, notes.md
  Languages:  Python (68%), TypeScript (32%)
  Tools:      vulture ✓ ruff ✓ mypy ✓ knip ✗ madge ✗ (missing → LLM-only fallback)
  Tests:      pytest — baseline GREEN
  .gitignore: added `.scratch/` (committed)

Proceed? (or adjust any line)
```

Auto mode — print the same card as an announcement and proceed.

### 9. Initialize session

1. Generate session slug: `YYYY-MM-DD-<5-random-alphanumerics>`
2. Create `.scratch/docs/cleanup/<slug>/` and subdirs
3. Write `scope.md` (target, exclusions, languages, tools, mode, sharding, baseline) and `status.md`:

```markdown
# Sweep Session <slug>

- Phase: preflight-complete
- Step: ready-to-analyze
- Next action: launch 4 dimension agents (or N area agents)
- Mode: interactive | auto
- Base branch: <branch-name>
- Target scope: <path>
- Sharding: dimension | area (N shards)
- Languages: <detected>
- Tools available: <list>
- Baseline tests: <green | red | none>
- Last updated: YYYY-MM-DD HH:MM TZ
```

### 10. Scan existing `cleanup-sweep-skip` markers

```bash
rg -n "cleanup-sweep-skip" <scope> -g '!.scratch/**' -g '!node_modules/**' -g '!.venv/**'
```

Record all markers + line numbers + ages (use `git blame` for age) in `scope.md` under "Known skip markers". Pass this list to all dimension agents in Phase 2 so they exclude marked regions from findings.

## Phase 1 Exit Criteria

All of the following must be true before entering Phase 2:

- [ ] No unresolved blocking git entries (in-scope tracked changes)
- [ ] Branch decision executed (PR-continue or cleanup branch)
- [ ] `.scratch` gitignore resolved
- [ ] Languages detected; sharding decided
- [ ] Tool probe complete (silent; gaps noted)
- [ ] Baseline test state recorded
- [ ] Consolidated confirmation accepted (interactive) or announced (auto)
- [ ] Session directory + status.md + scope.md written
- [ ] Existing skip markers catalogued

Announce: *"Phase 1 complete. Entering Phase 2: launching dimension agents."* Update `status.md`. Read `references/phase-2-analyze.md` before proceeding.
