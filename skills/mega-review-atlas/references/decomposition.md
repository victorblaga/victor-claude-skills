# Decomposition Rules

How to turn the inventory into units, seams, sweeps, and the cohesion overlay. Behavioral boundaries govern everything here; files, directories, and line counts never do.

## Node kinds

- **group** — navigation context (a lifecycle phase, the production envelope). Not reviewable; never triggers duplicate review of child code.
- **unit** — a reviewable behavioral leaf. The atom of the campaign.
- **seam** — a reviewable contract between units, or between the system and an opaque/external dependency.
- **sweep** — a focused horizontal review across many units, carrying one question.

## Units

### The four-part stopping rule

A candidate becomes a leaf only when **all four** hold:

1. **One guarantee.** You can summarize it as "given X, this unit guarantees Y."
2. **Bounded state transition.** Its inputs, outputs, side effects, invariants, and failure behavior can be described together, completely.
3. **Manageable review packet.** Implementation + contracts + focused tests fit one deep-review context.
4. **No independently meaningful child.** Any child with its own contract or invariant forces a split.

If a candidate fails rule 1 or 4, split by guarantee or invariant. If it fails rule 3 but passes the rest, it may stay whole with an explicit rationale — see size warnings.

### Size warnings

Size is a warning signal, not the definition. Flag a leaf above roughly **5–10 primary files or 1,000–2,000 non-test source lines**. A larger cohesive unit is allowed with a recorded rationale in its packet. Never split by arbitrary line count — split by behavior and symbols.

### The lifecycle spine

The primary hierarchy follows **runtime execution and data flow**, not the package tree. Order groups the way the system actually runs: ingest → transform → persist → serve, or whatever the target's real sequence is. Physical code layout appears only in the cohesion overlay when it disagrees with behavior.

### Shared capabilities

Implementation reachable from multiple lifecycle phases (a client wrapper, a retry helper, a shared repository layer) gets **one canonical unit**, reviewed once, with dependency edges from each consumer. Consumers list it as context-only scope.

### Canonical ownership

- Every reachable production symbol is **owned by exactly one unit**, explicitly excluded with a reason, or classified opaque/external.
- A unit may cross files, packages, or repositories. A file may be split across units by qualified symbol.
- Declarative artifacts without symbols (SQL, YAML, JSON, shell, IaC, migrations) use whole-file ownership.
- Tests may support several units, but each test gets one primary behavioral owner.
- **Context-only scope** is code a reviewer may read to understand a unit but may not report findings against — those findings belong to the owning unit.

## Seams

Create an explicit seam node for every **material** cross-unit contract. Materiality test: if this boundary silently disagreed, would the system misbehave in a way neither side's unit review would catch? Candidate classes:

- Artifact / schema handoffs between phases
- Database transaction, locking, and isolation boundaries
- Retry / replay / idempotency assumptions shared across units
- Concurrency and ordering dependencies
- Version / model / data compatibility between producer and consumer
- Opaque-platform usage contracts (the target's side of the contract only)
- Deployment and runtime configuration crossing unit boundaries
- Failure propagation and lifecycle cleanup

Every opaque dependency must have a seam describing the contract the target relies on. A seam packet names both endpoints and states which side is primary scope and which is context.

## Sweeps

One focused question ran horizontally. A sweep may span more code than any leaf **because** it carries a single question; its packet must list the exact units and symbols in scope, never "the whole repo". Default set for a full atlas:

- Cross-unit architecture and invariant consistency
- AI slop: duplicated, speculative, or reinvented machinery across units
- Performance and scale, evaluated against the runtime profile
- Test and evidence quality across units
- Contract and data-safety coverage
- Cohesion / refactoring signals (consumes the overlay)

Trim only with a recorded reason in `decisions.md`.

## Production envelope

When in scope, model deployment wiring, configuration, scheduling, resource sizing, model/data availability, and database schema/index assumptions as a **group** with its own units and seams. Local dev harnesses and runbooks are evidence for other nodes, not business stages.

## Cohesion overlay

Structural smells recorded **without prescribing fixes**, each linked to the nodes it touches and to inventory evidence:

- One behavior scattered across unrelated locations
- One file owned by multiple behavioral units
- Repeated or cyclic dependency crossings
- Contracts defined far from both producer and consumer
- Hidden coupling through shared state or artifacts
- Excessive test setup caused by poor isolation
- Duplicated implementation; shared abstractions with a single real consumer

These become review input for the cohesion sweep. They are not findings and not accepted refactoring work.
