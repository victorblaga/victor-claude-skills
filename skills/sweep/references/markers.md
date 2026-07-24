# `cleanup-sweep-skip` Markers

Inline comment markers that tell future sweep runs to skip specific regions of code. They live with the code, so rationales can't drift — refactoring the code moves the rationale with it.

## Format

```
{comment-prefix} cleanup-sweep-skip: {reason} ({YYYY-MM-DD})
```

- `cleanup-sweep-skip` — literal keyword (case-sensitive, no variants)
- `:` separator (single colon, space after)
- `{reason}` — concrete explanation of why the skill should not flag this code. Good reasons cite architectural constraints, runtime requirements, external API contracts, or specific incidents. Bad reasons are vague ("needed", "important").
- `{YYYY-MM-DD}` — date the marker was placed. Age-nudge at end of each run flags stale markers.

## Per-Language Syntax

| Language | Comment prefix | Example |
|----------|---------------|---------|
| Python | `#` | `# cleanup-sweep-skip: orchestrator requires this catch (2026-04-16)` |
| JavaScript / TypeScript | `//` | `// cleanup-sweep-skip: external API returns untyped JSON (2026-04-16)` |
| Rust | `//` | `// cleanup-sweep-skip: unsafe block needed for FFI (2026-04-16)` |
| Go | `//` | `// cleanup-sweep-skip: err ignored intentionally — Close() documented as no-op here (2026-04-16)` |
| Scala | `//` | `// cleanup-sweep-skip: Any needed for contravariant generic (2026-04-16)` |
| Java | `//` | `// cleanup-sweep-skip: unused field required by framework reflection (2026-04-16)` |
| SQL | `--` | `-- cleanup-sweep-skip: retained for rollback procedure (2026-04-16)` |
| Shell | `#` | `# cleanup-sweep-skip: subshell isolates env vars (2026-04-16)` |
| HTML | `<!-- -->` | `<!-- cleanup-sweep-skip: required by SEO; do not collapse (2026-04-16) -->` |
| YAML / TOML | `#` | `# cleanup-sweep-skip: key required by CI runner (2026-04-16)` |

For multi-line or block comments (e.g., `/* */`), use the single-line style on the line immediately before the protected code. Do not place markers inside block comments.

## Placement Rules

### Line-scoped protection

Marker on the line immediately above the protected code:

```python
# cleanup-sweep-skip: orchestrator retries on this catch (2026-04-16)
except Exception as e:
    log.warning("ingest failed", e)
```

The marker protects the single statement/block on the next source line.

### Block-scoped protection

For a function, class, or block, place the marker on the line immediately above the definition:

```python
# cleanup-sweep-skip: used by plugin_loader via getattr (2026-04-16)
def _legacy_cleanup():
    ...
```

The marker protects the entire definition and its body.

### File-scoped protection

For code where the finding is at module level (e.g., "this whole module should be removed"), place the marker as the first line of the module-level docstring or as the first comment at the top of the file:

```python
"""
cleanup-sweep-skip: module kept for API backwards-compat through 2026-Q4 (2026-04-16)

Legacy parser module. Maintained alongside parser_v2 for compatibility.
"""
```

or

```typescript
// cleanup-sweep-skip: module exports used by external consumer SDK v1 (2026-04-16)
export * from './legacy';
```

### Architecture-level rejects without a natural anchor

When a rejection is about a cross-cutting pattern (e.g., "don't consolidate these two modules"), place the marker at the top of the primary module of the pair. Note the "partner" in the rationale:

```python
"""
cleanup-sweep-skip: do not merge with sibling_module — they diverge in context Y (2026-04-16)

...
"""
```

## Detection Rules

In preflight (Phase 1), scan for markers:

```bash
rg -n "cleanup-sweep-skip" <scope> -g '!.scratch/**' -g '!node_modules/**' -g '!.venv/**'
```

Parse each match into:
- `file`
- `line` (where the marker is)
- `reason` (text after `:` and before trailing date)
- `date` (from parenthesized trailing date, or `unknown` if malformed)
- `protected-range` (determined by placement rules above — next source line / next block / rest of file for file-scoped)

Pass this list to every dimension agent in Phase 2. Agents exclude findings whose `file:line` falls inside any protected range.

## Age Nudge (Phase 7)

At the end of each run, the skill reports:

```
Active cleanup-sweep-skip markers: 23
Oldest markers (>12 months):
  - src/ingest/csv.py:142 — "orchestrator retries on this catch" (2025-02-14, 14 months old)
  - src/api/legacy.py:1 — "API backwards-compat through 2026-Q4" (2024-11-03, 17 months old)
  - ...

Consider revisiting — the original rationale may no longer apply.
```

This nudge is informational only. The skill does not automatically remove or challenge markers.

## Marker Quality

When placing a marker in Phase 5, the skill drafts the rationale based on the triage discussion. If the user's reason is vague ("don't like that change"), prompt for more specificity:

```
Draft marker rationale: "don't like that change"

Future sweeps need a concrete reason so the next reviewer (or future you) can judge whether the reason still applies. Examples of good rationales:
  - "orchestrator requires this to swallow; see retry loop in service.py:80"
  - "external SDK returns untyped JSON at this boundary"
  - "used via getattr for plugin loading"

Want to refine the rationale, or accept the draft?
```

Do not place a marker with a vague rationale unless the user explicitly confirms.

## Anti-patterns (do not emit)

- `cleanup-sweep-skip` without a reason
- `cleanup-sweep-skip: TODO` or `cleanup-sweep-skip: later`
- Marker not adjacent to code (e.g., several blank lines between marker and protected code)
- Markers on `cleanup-sweep-skip` itself — don't nest markers
- Markers anywhere inside a multi-line comment block (use the single-line style instead)
