# Phase 1 — Preflight

Preflight is strict by design. Cleanup mutates code; the safety envelope protects against losing work, running on a production branch, or producing a sweep report that can't be verified.

All preflight steps run in order. Do not proceed to Phase 2 until every step has a definitive outcome (completed, user-skipped, or soft-warned).

## Steps

### 1. Clean git state (strict)

```bash
git status --porcelain
```

If there is **any** output (untracked, unstaged, staged):

1. Show the user the current dirty state
2. Offer: (a) stash, (b) commit to current branch, (c) abort
3. Wait for choice
4. Do not proceed with a dirty working tree

### 2. Branch decision (interactive)

Ask the user, with default slug `cleanup/YYYY-MM-DD-<slug>` where `<slug>` is 5 random alphanumerics:

```
How should the sweep branch be set up?

1. Work on the CURRENT branch ({{current-branch}})
2. New branch from CURRENT ({{current-branch}}) — recommended
3. New branch from LATEST DEV — safest, isolates from local state
```

Behavior per choice:

| Choice | Actions |
|--------|---------|
| 1 (current) | Stay. If current is `dev` or `main`/`master`, warn strongly and reconfirm. |
| 2 (new from current) | Ask for name (default `cleanup/YYYY-MM-DD-<slug>`). `git checkout -b <name>`. |
| 3 (new from dev) | `git fetch origin`, `git checkout dev`, `git pull --ff-only`, then ask for name. `git checkout -b <name>`. Abort if `dev` doesn't exist locally or on origin. |

Never default without asking. The user opted into sweep for a reason; the branch choice signals *intent*.

### 3. `.docs` gitignore check

```bash
grep -qE '^\.docs/?$' .gitignore 2>/dev/null
```

If not present, present the user with:

```
Session artifacts go to .docs/cleanup/<session>/. This pattern is not in .gitignore.

Add `.docs` to .gitignore now? (recommended — session artifacts are ephemeral, not PR content)

[y / n / .docs is already handled elsewhere]
```

On yes: append `.docs/` to `.gitignore`, commit with message `chore: ignore .docs sweep session dir`.

### 4. Language detection

Detect languages present in the target scope:

```bash
# marker files
find . -maxdepth 3 \( -name "pyproject.toml" -o -name "setup.py" -o -name "requirements.txt" -o -name "package.json" -o -name "Cargo.toml" -o -name "go.mod" -o -name "build.sbt" -o -name "build.sc" \) -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null
```

Combine with file-extension counts via `find`/`wc` to rank languages by LoC. Record in `scope.md`:

```markdown
# Scope

Target: <path>
Exclusions: tests/, migrations/, generated/, vendored, lockfiles, build artifacts
Included languages (primary → secondary):
  - Python (68% of LoC, pyproject.toml detected)
  - TypeScript (32% of LoC, package.json detected)
```

### 5. Tool probe + install offers

For each detected language, probe the tools listed in `references/tool-registry.md` for each agent dimension. Classify each:

| Status | Meaning |
|--------|---------|
| `installed` | `command -v <tool>` succeeded, version reasonable |
| `missing` | Not installed; present install command; offer to install |
| `nightly-only` | E.g., `cargo-udeps` requires nightly Rust; flag explicitly |
| `needs-config` | E.g., `knip` works without config but is much better with one; offer to bootstrap |

Present the user with a summary:

```
Tool probe (Python + TypeScript):

Installed:
  ✓ vulture (dead code)
  ✓ ruff (dead code, linting)
  ✓ mypy (weak types)
  ✓ tsc (weak types)

Missing (offer install):
  ✗ pycycle (circular deps)         → pip install pycycle
  ✗ knip (dead code / deps)         → npm install -D knip  (needs config; can bootstrap)
  ✗ madge (circular deps)           → npm install -D madge

For each missing tool: [install / skip / skip-all]
```

Rules:
- **Project-scoped installs by default** — `npm install -D`, `uv add --dev` (or `pip install` inside project venv), `cargo install` is global but accept since there's no alternative
- **Never install without asking** — enumerate each, let user accept/skip
- Respect `skip-all` and stop prompting for the rest in this session

After installs, run any needed config bootstrap (e.g., `npx knip --init` or generate a minimal `knip.json`). Ask before writing config files.

### 6. Baseline test run (soft)

Detect test command from project conventions:

| Marker | Likely test command |
|--------|---------------------|
| `pyproject.toml` with `[tool.pytest.ini_options]` | `pytest` |
| `package.json` with `"test"` script | `npm test` or `yarn test` |
| `Cargo.toml` | `cargo test` |
| `build.sbt` | `sbt test` |
| `go.mod` | `go test ./...` |

Ask the user to confirm the detected command (or provide one). Run it. Record result:

- **Passing** → record baseline as green, proceed
- **Failing** → show failures, ask: *"Tests are red at baseline. Is this known? Proceed (we'll compare post-apply against this baseline) or abort?"*
- **No tests found** → warn loudly, ask: *"No test command detected. Proceed without post-apply verification? This reduces safety of auto-apply."*

Record the baseline command and result in `scope.md`.

### 7. Initialize session

1. Generate session slug: `YYYY-MM-DD-<5-random-alphanumerics>`
2. Create `.docs/cleanup/<slug>/` and subdirs
3. Write `status.md`:

```markdown
# Sweep Session <slug>

- Phase: preflight-complete
- Step: ready-to-analyze
- Next action: launch 8 dimension agents
- Base branch: <branch-name>
- Target scope: <path>
- Languages: <detected>
- Tools available: <list>
- Baseline tests: <green | red | none>
- Last updated: YYYY-MM-DD HH:MM TZ
```

4. Commit preflight artifacts (scope.md, status.md) if on a sweep-dedicated branch. If on current branch, leave uncommitted until Phase 2 starts.

### 8. Scan existing `cleanup-sweep-skip` markers

```bash
grep -rn "cleanup-sweep-skip" <scope> --include="*.{py,ts,tsx,js,jsx,rs,go,scala,java}" 2>/dev/null
```

Record all markers + line numbers + ages (use `git blame` for age) in `scope.md` under "Known skip markers". Pass this list to all dimension agents in Phase 2 so they exclude marked regions from findings.

## Phase 1 Exit Criteria

All of the following must be true before entering Phase 2:

- [ ] git is clean
- [ ] branch decision executed
- [ ] `.docs` gitignore resolved
- [ ] languages detected
- [ ] tool probe complete (missing tools installed or user-skipped)
- [ ] baseline test state recorded
- [ ] session directory + status.md + scope.md written
- [ ] existing skip markers catalogued

Announce: *"Phase 1 complete. Entering Phase 2: launching 8 dimension agents."* Update `status.md`. Read `references/phase-2-analyze.md` before proceeding.
