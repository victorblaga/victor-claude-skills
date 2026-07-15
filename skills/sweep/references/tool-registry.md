# Tool Registry

Per-language tool inventory for sweep's preflight probe. The probe is silent — availability is recorded in `scope.md`, no install prompts. Each agent dimension uses the tools listed below as seed evidence; missing tools fall back to LLM-only analysis with an explicit caveat in findings. Install commands below are used only when the user explicitly asks for a tool.

## Python

| Dimension | Tool | Probe | Install | Notes |
|-----------|------|-------|---------|-------|
| Dead code | `vulture` | `vulture --version` | `pip install vulture` or `uv add --dev vulture` | Strong default |
| Dead code | `ruff` | `ruff --version` | `pip install ruff` or `uv add --dev ruff` | Use `ruff check --select F401,F841` for unused imports/vars |
| Circular deps | `pycycle` | `pycycle --help` | `pip install pycycle` | Run from project root |
| Circular deps | `pydeps` | `pydeps --version` | `pip install pydeps` | Generates import graphs; use `--show-cycles` |
| Weak types | `mypy` | `mypy --version` | `pip install mypy` or project-level | Use `mypy --strict` for sweep |
| Weak types | `pyright` | `pyright --version` | `npm install -g pyright` or `pip install pyright` | Alternative to mypy |

## JavaScript / TypeScript

| Dimension | Tool | Probe | Install | Notes |
|-----------|------|-------|---------|-------|
| Dead code | `knip` | `npx knip --version` | `npm install -D knip` | Needs config file; bootstrap with `npx knip --init` |
| Dead code | `ts-prune` | `npx ts-prune --version` | `npm install -D ts-prune` | TS-only; deprecated but still useful |
| Circular deps | `madge` | `npx madge --version` | `npm install -D madge` | Use `madge --circular <entry>` |
| Circular deps | `dependency-cruiser` | `npx depcruise --version` | `npm install -D dependency-cruiser` | Needs `.dependency-cruiser.js` config; offer bootstrap |
| Weak types | `tsc` | `tsc --version` | Already present if TS project | Use `tsc --noEmit --strict` |
| Weak types (grep) | `rg` for `: any`, `as any`, `<any>` | — | — | LLM agent runs grep as fallback |

## Rust

| Dimension | Tool | Probe | Install | Notes |
|-----------|------|-------|---------|-------|
| Dead code | `cargo-udeps` | `cargo udeps --version` | `cargo install cargo-udeps` | **Nightly only**: `cargo +nightly udeps` |
| Dead code | `cargo-machete` | `cargo machete --version` | `cargo install cargo-machete` | Stable; finds unused dependencies |
| Weak types | `clippy` | `cargo clippy --version` | `rustup component add clippy` | Check `dyn Any`, `Box<dyn>`, wide lints |

## Go

| Dimension | Tool | Probe | Install | Notes |
|-----------|------|-------|---------|-------|
| Dead code | `deadcode` | `deadcode -h` | `go install golang.org/x/tools/cmd/deadcode@latest` | |
| Dead code | `staticcheck` | `staticcheck -version` | `go install honnef.co/go/tools/cmd/staticcheck@latest` | Use `-checks U1000` for unused |
| Weak types | `staticcheck` | — | (as above) | Covers `interface{}` / `any` misuse |

## Scala

| Dimension | Tool | Probe | Install | Notes |
|-----------|------|-------|---------|-------|
| Dead code | `scapegoat` | Check `build.sbt` for plugin | Add to `project/plugins.sbt`: `addCompilerPlugin("com.sksamuel.scapegoat" %% "scalac-scapegoat-plugin" % "...")` | Compiler plugin |
| Weak types | `scalafix` | `scalafix --version` | `addSbtPlugin("ch.epfl.scala" % "sbt-scalafix" % "...")` | Use `ExplicitResultTypes` rule |

## Java

| Dimension | Tool | Probe | Install | Notes |
|-----------|------|-------|---------|-------|
| Dead code | `SpotBugs` | `spotbugs -version` | Gradle/Maven plugin | Many detectors for unused code |
| Dead code | IntelliJ inspections | — | IDE | Best in-IDE; CLI option via `idea.sh inspect.sh` |

## Bootstrap Rules

For tools that need configuration:

- **knip**: `npx knip --init` generates a starter `knip.json`. If user accepts, commit it to the branch with `chore: bootstrap knip config for sweep`.
- **dependency-cruiser**: `npx depcruise --init` generates a starter config. Same commit pattern.
- **scapegoat / scalafix**: adding a compiler plugin is invasive; recommend but do not auto-apply. Ask the user to add manually if they want deeper Scala coverage.

## Install Scope Rules

- **Project-scoped by default** — `npm install -D`, `uv add --dev`, sbt plugin-local
- **Global allowed when no project-scope exists** — `cargo install`, `go install`, `pip install` outside a venv
- **Never sudo** — never `sudo pip install` or `sudo npm install -g` without explicit user request
- **Respect existing venvs / lockfiles** — if a venv is present, install inside it; if `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` present, use the matching package manager

## Degradation Policy

If a tool is missing, the relevant dimension agent proceeds with LLM-only analysis. The agent's findings file must include at the top:

```markdown
> **Tool unavailable:** `<tool-name>` was not available for this run. Findings below are LLM-identified only. Recommend manual verification or install `<tool-name>` for deeper coverage.
```

Never abort the sweep because of a missing tool.

## Tool Output Ingestion

When a tool is available, run it in preflight (or early in the relevant dimension agent) and save raw output to `.docs/cleanup/<session>/tool-output/<tool>.txt`. The dimension agent reads this file as seed evidence and reconciles it against LLM findings, deduplicating and enriching with context.

Example preflight commands (save output, do not abort on tool errors):

```bash
mkdir -p .docs/cleanup/<session>/tool-output

# Python
vulture <scope> > .docs/cleanup/<session>/tool-output/vulture.txt 2>&1 || true
ruff check --select F401,F841 <scope> > .docs/cleanup/<session>/tool-output/ruff.txt 2>&1 || true
pycycle --here --ignore <scope> > .docs/cleanup/<session>/tool-output/pycycle.txt 2>&1 || true
mypy --strict <scope> > .docs/cleanup/<session>/tool-output/mypy.txt 2>&1 || true

# TypeScript
npx knip > .docs/cleanup/<session>/tool-output/knip.txt 2>&1 || true
npx madge --circular <scope> > .docs/cleanup/<session>/tool-output/madge.txt 2>&1 || true
npx tsc --noEmit --strict > .docs/cleanup/<session>/tool-output/tsc-strict.txt 2>&1 || true
```

Never let a tool's non-zero exit code abort the sweep — tools reporting findings is normal.
