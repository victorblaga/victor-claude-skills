# Design Principles Reference

A working reference for how code should be structured. Rooted in John Ousterhout's *A Philosophy of Software Design*, extended with practical criteria for data-intensive systems.

Use this document when evaluating existing code structure, proposing outlines, and writing implementation task contracts. These principles inform what "good structure" means throughout the `/architect` workflow.

---

## The Central Problem: Complexity

The cost of software is not writing it. It is understanding, modifying, and extending it over time.

**Complexity** is anything that makes a system hard to understand or change. It shows up as:

| Symptom | What it looks like |
|---|---|
| **Change amplification** | A small change requires edits in many places |
| **Cognitive load** | You must hold too much context to work safely |
| **Unknown unknowns** | You don't know what you don't know |

Two root causes: **dependencies** (code that cannot be understood in isolation) and **obscurity** (important information that is not obvious).

---

## Deep Modules

The most important heuristic: **the best modules provide a simple interface that hides significant implementation complexity.**

A module's value is the ratio of functionality hidden to interface complexity exposed. A **deep module** has a small interface and substantial internal logic. A **shallow module** has an interface nearly as complex as its implementation — it redistributes complexity rather than absorbing it.

### The test

*Is this module actually hiding complexity, or just moving code around?*

A module is useful not because it exists, but because it **reduces what others need to know**.

### The anti-pattern: classitis

Proliferating tiny single-method classes that each do almost nothing. Each module boundary has overhead (naming, finding, loading context). That overhead is only justified when the boundary hides meaningful complexity.

> This does NOT mean "write big classes." It means write **better abstractions**. Every module boundary should earn its existence.

---

## Information Hiding

A module should encapsulate design decisions not visible to other modules. Internal representation, algorithms, edge-case handling — all stay behind the interface.

### Information leakage

When a design decision is reflected in multiple modules, those modules are coupled — regardless of their call graph. **Temporal decomposition** is a frequent cause: splitting code by *when* things happen rather than *what knowledge they encapsulate*.

### The check

- What knowledge should exist in exactly one place?
- What should callers never need to know?
- What decisions can remain internal?

### Query interfaces over data exposure

A common form of information leakage is exposing raw data structures (dicts, DataFrames, indices) to consumers. Instead, expose **query methods** that answer questions:

- Bad: `cache.hash_to_source_record_ids[hash]` — consumer knows the internal dict structure
- Good: `cache.masters_for_hash(hash) -> set[str]` — consumer asks a question, gets an answer

This matters because the backing implementation can change (in-memory → Redis, dict → database) without affecting consumers. Design components as **queryable services**, not **data bags**.

---

## Different Layer, Different Abstraction

Every layer should provide a genuinely different abstraction from layers above and below. If the abstraction doesn't change at each boundary, the layers aren't earning their keep.

### Red flags

- **Pass-through methods** — signature mirrors another's, adding no abstraction. Fix: expose the lower layer directly, redistribute responsibilities, or merge.
- **Pass-through variables** — values threaded through layers that don't use them. Fix: attach to a shared object or use a scoped context object.
- **Decorators** — wrapping an interface with the same interface, adding minimal functionality. Ask: can this live in the underlying module directly?

---

## Pull Complexity Downward

Push complexity into the module rather than out to callers.

Warning signs of a leaky abstraction:
- Every caller must remember to validate the same thing
- Every caller must understand ordering constraints
- Every caller must know the same hidden invariant
- Every caller must coordinate around side effects

Fix the module, not the callers.

---

## Define Errors Out of Existence

Design interfaces so exceptional conditions can't arise or are handled internally.

- `delete(file)` succeeds silently if the file doesn't exist — postcondition already met
- `find_matches(empty_input)` returns empty output, not an exception
- Optional data returns a default, not an error

Every exception that surfaces through an interface is complexity pushed onto the caller. Use exceptions only for genuinely exceptional conditions the caller cannot handle with a default.

---

## Fractal Depth

Deep module principles apply recursively. A pipeline is a deep module that hides its stages. A complex stage can itself be a deep module hiding its own sub-steps.

The test is the same at every level: **does this internal boundary hide enough complexity to justify its existence?** A stage that's 30 lines of straightforward logic stays a private method. A stage with algorithmic complexity and internal data types earns its own module — which can itself contain further private structure.

**The constraint:** at every level, the boundary must hide real complexity. A nested class that just delegates is shallow regardless of where it sits.

---

## Together or Apart?

Each boundary introduces interface overhead, glue code, and cognitive switching. The question is not "is this a separate concern?" but **"does separating reduce overall complexity?"**

### Combine when:
- The pieces share knowledge (same data format, algorithm, invariant)
- They are always used together
- You cannot understand one without reading the other
- Merging produces a simpler, deeper interface

### Separate when:
- Genuinely independent — neither needs knowledge of the other
- One is general-purpose and the other is special-purpose
- Combining forces callers to get functionality they don't need

### Method/function length

The correct question is not size but **coherence**: does the extracted piece form an independently understandable abstraction? A 150-line function that reads top-to-bottom is better than 5 functions that force you to bounce between files.

**Conjoined methods** — methods you must always read or call together — are a sign the boundary is wrong.

---

## General-Purpose Interfaces

Design modules to be somewhat general-purpose: don't build a framework, but don't encode current-use-case assumptions into interfaces. The interface should reflect the general capability; the caller's specific needs stay in the caller.

---

## Strategic vs. Tactical Programming

| | Tactical | Strategic |
|---|---|---|
| **Goal** | Get the current task done fast | Improve structure while completing the task |
| **Investment** | ~0% overhead | ~10–20% extra |
| **Long-term** | Compounds complexity | Pays off within months |

Every time you touch code, leave it at least slightly better than you found it. Not as a separate cleanup — as part of the work.

---

## Consistency

Every inconsistency becomes another exception someone must remember. Pick patterns and enforce them. The effort of maintaining consistency is always less than the cost of explaining exceptions.

---

## Obvious Code

Prefer code that is obvious to readers. Be skeptical of code that is clever, compressed, or elegant only after explanation.

---

## Naming

Naming is a design activity. Good names are specific, domain-aligned, unambiguous, and informative without extra lookup. If you can't name something clearly, you may not yet understand what it does.

---

## Python-Specific Patterns

### Functions over class hierarchies

Use class hierarchies only for genuine polymorphism — multiple implementations behind the same interface that callers switch between. Not for organizing sequential steps.

A function that reads, transforms, and writes is one deep module. An ABC that forces three method implementations is three shallow ones.

### Pipeline as a deep module

A pipeline's public interface should be minimal — `run(config) -> result`. Phases are internal implementation details that should not appear in the public interface.

The `run` method reads like a table of contents. Internal functions are private. Tests exercise via `run()`, not by calling phases individually.

### Configuration

Use typed configuration objects (frozen dataclasses, Pydantic models, or equivalent) with factory methods that read from the environment. Callers work with `config.data_bucket`, never with `os.environ["DATA_BUCKET"]`.

### Duplication vs abstraction

Prefer small duplication over premature abstraction. Only extract when:
- The duplication is truly mechanical (identical logic, zero context variation)
- The resulting shared function is simpler than the copies it replaces

When in doubt, keep the duplicate and reconsider when a third copy appears.

---

## Red Flags Checklist

Use this when evaluating code structure in the outline:

- **Shallow modules** — interface complexity approximates implementation complexity
- **Classitis** — proliferation of tiny classes, especially pass-through delegators
- **Pass-through methods** — method signature mirrors another's, adding no abstraction
- **Conjoined methods** — methods you always must read or call together
- **Information leakage** — same design decision reflected in multiple modules
- **Temporal decomposition** — splitting by when, not by what knowledge is encapsulated
- **Excessive exception propagation** — pushing error handling onto callers
- **Special-case proliferation** — each edge case gets its own code path instead of being generalized
- **Pass-through variables** — values threaded through layers that don't use them
- **Giant utility modules** — `utils.py`, `helpers.py`, `common.py` — give modules real names or inline the code
- **ABC hierarchies for sequential steps** — use plain functions instead
- **Leaking infrastructure mechanics** — AWS API shapes, SQL syntax, file path schemes exposed to callers

---

## Design Questions

### When evaluating a module boundary

- What knowledge does this module hide?
- Is the interface simpler than the implementation?
- Could a caller use this without understanding the internals?
- Am I splitting because of temporal order rather than information boundaries?
- Does each layer provide a genuinely different abstraction?

### When proposing restructuring

- Is the current structure still right given what we now know?
- Does the proposed change reduce or increase information leakage?
- Are there special cases we could eliminate instead of extend?
- Would the module be understandable without tribal knowledge?
