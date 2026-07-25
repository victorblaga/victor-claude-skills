# Design Principles

A working reference for how code should be structured. Rooted in Ousterhout's *A Philosophy of Software Design*, with concrete patterns from real data-pipeline architecture.

## The Central Problem: Complexity

The cost of software is not writing it. It is understanding, modifying, and extending it over time.

Complexity shows up as:
- **Change amplification**: A small change requires edits in many places
- **Cognitive load**: You must hold too much context to work safely
- **Unknown unknowns**: You don't know what you don't know

Root causes: dependencies (code that cannot be understood in isolation) and obscurity (important information that is not obvious).

## Abstraction Discipline — The Core Rule

**A component either describes a business flow in abstract terms OR does actual dirty work. Never both.**

This is the single most important structural principle. Every other rule supports it.

### Three layers, three languages

| Layer | Speaks | Example |
|-------|--------|---------|
| **Orchestration** | Domain language | "Build snapshot, publish it, notify" |
| **Coordination** | Pipeline language | "Stage sources, resolve studies, assemble" |
| **Infrastructure** | I/O language | "Stream JSONL from S3, batch-insert into SQLite, execute SQL" |

### DO: Keep layers separate

```python
# ORCHESTRATION — speaks domain
class SnapshotBuilderActor:
    def build_snapshot(self, sources):
        snapshot = self.build_service.build(sources)         # domain verb
        result = self.publisher.publish(snapshot).get()       # domain verb
        self.notifier.notify(result)                          # domain verb

# COORDINATION — speaks pipeline
class BuildSnapshotService:
    def build(self, sources):
        staging_db = self.staging_assembler.assemble(sources) # pipeline step
        return self.snapshot_assembler.assemble(staging_db)    # pipeline step

# COORDINATION — speaks pipeline (one level deeper)
class StagingAssembler:
    def assemble(self, sources):
        db = StagingDatabase.create()
        self.crm_stager.stage(db, sources)           # pipeline step
        self.registry_stager.stage(db, sources)     # pipeline step
        self.study_resolver.resolve(db)              # pipeline step
        return db

# INFRASTRUCTURE — speaks I/O
class CrmStager:
    def stage(self, db, sources):
        for record in crm.stream_records(s3, sources.crm.path):  # I/O
            if not record.get("facility_golden_id"):              # data cleaning
                continue
            db.insert_raw_site(...)                                # I/O
```

### DON'T: Mix layers

```python
# BAD — orchestration mixed with infrastructure
class SnapshotBuilder:
    def build_snapshot(self, sources):
        conn = sqlite3.connect(":memory:")          # infrastructure!
        conn.execute("CREATE TABLE sites ...")      # infrastructure!

        for record in stream_jsonl(s3, path):       # infrastructure!
            if record.get("golden_id"):             # business rule mixed with I/O
                conn.execute("INSERT INTO ...", ...) # infrastructure!

        # Union-find for study resolution
        uf = UnionFind()                            # algorithm detail!
        for row in conn.execute("SELECT ..."):      # infrastructure!
            uf.union(row[0], row[1])

        tar_path = self._create_archive(conn)       # now doing archiving too?
        s3.upload_file(tar_path, bucket, key)        # and S3 upload?
```

This method is doing orchestration, coordination, data streaming, business logic, archiving, AND uploading. Six responsibilities. It should be six components.

## Deep Modules

The best modules provide a simple interface that hides significant implementation complexity.

A module's value is the ratio of functionality hidden to interface complexity exposed. A **deep module** has a small interface and substantial internal logic. A **shallow module** has an interface nearly as complex as its implementation.

### The test
*Is this module actually hiding complexity, or just moving code around?*

### Anti-pattern: classitis
Proliferating tiny single-method classes that each do almost nothing. Every module boundary has overhead (naming, finding, loading context). That overhead is only justified when the boundary hides meaningful complexity.

## Single Responsibility — Properly Understood

SRP means each component has one reason to change. But **coordination IS a single responsibility**.

### GOOD: Coordination responsibility
```python
class StagingAssembler:
    """Coordinates staging of all data sources into a temporary database."""
    def assemble(self, sources):
        self.crm_stager.stage(db, sources)
        self.registry_stager.stage(db, sources)
        self.study_resolver.resolve(db)
        self.site_resolver.resolve(db)
        return db
```
This does "X and Y and Z" but it's ONE responsibility: coordinate the staging pipeline. The "ands" are steps at the same abstraction level serving one coherent goal.

### BAD: Responsibility sprawl
```python
class DataManager:
    """Manages data."""
    def process(self, sources):
        # Parse incoming messages (messaging concern)
        msg = json.loads(raw_message)
        # Stage data (pipeline concern)
        self._stage_from_s3(msg["path"])
        # Score results (business logic concern)
        scores = self._run_model(data)
        # Send notifications (notification concern)
        self._send_email(scores)
```
This has FOUR different responsibilities that change for different reasons.

### The test
Can you describe the component's purpose in one sentence? The sentence can have multiple steps as long as they serve one coherent goal and operate at the same abstraction level. If you need "and" between UNRELATED concerns, split.

## Typed Boundaries

Domain types must cross every module boundary. No raw dicts, no primitive obsession.

### DO
```python
def publish(self, snapshot: Snapshot) -> PublishResult: ...
def score(self, sites: list[StudySiteRow]) -> list[SiteScore]: ...
```

### DON'T
```python
def publish(self, db_path: str, markers: dict, id: str, created_at: str, count1: int, count2: int) -> dict: ...
def score(self, data: list[dict]) -> list[tuple]: ...
```

Rules:
- If two values have different semantics, they get different types (`PathWatermark` vs `TimestampWatermark`, not both `str`)
- Method signatures with >3 parameters: the parameters want to be a single typed object
- `dict[str, Any]` crossing a module boundary is a design failure — make it a dataclass
- Frozen dataclasses with slots for value objects
- Serialization (`to_dict`/`from_dict`) lives on the type, not scattered across callers

## Information Hiding

A module should encapsulate design decisions not visible to other modules. Internal representation, algorithms, edge-case handling — all stay behind the interface.

### Query interfaces over data exposure
- Bad: `cache.hash_to_source_record_ids[hash]` — consumer knows internal dict structure
- Good: `cache.masters_for_hash(hash) -> set[str]` — consumer asks a question, gets an answer

The backing implementation can change (in-memory → Redis, dict → database) without affecting consumers.

## Narrative Readability

Code should read top-down like a story. Each line follows from the previous without jumping to unrelated concerns.

### The test
Write the method body as comments first (no code). Does it read like a story? Each step should be one sentence in domain language.

```python
def build(self, sources):
    # 1. Stage all data sources into a temporary database
    # 2. Assemble the final snapshot from staged data
    # 3. Clean up the staging database
```

If a step needs infrastructure language ("open connection", "execute SQL"), that's a separate component.

## Pull Complexity Downward

Push complexity into the module rather than out to callers.

Warning signs:
- Every caller must remember to validate the same thing
- Every caller must understand ordering constraints
- Every caller must coordinate around side effects

Fix the module, not the callers.

## Define Errors Out of Existence

Design interfaces so exceptional conditions can't arise or are handled internally.
- `delete(file)` succeeds silently if the file doesn't exist
- `find_matches(empty_input)` returns empty output, not an exception
- Optional data returns a default, not an error

## Together or Apart?

Each boundary introduces overhead. The question is not "is this a separate concern?" but "does separating reduce overall complexity?"

### Combine when:
- Pieces share knowledge (same data format, algorithm, invariant)
- Always used together
- Can't understand one without the other

### Separate when:
- Genuinely independent
- One is general-purpose, the other special-purpose
- Combining forces unwanted functionality on callers

## Strategic vs Tactical

Every time you touch code, leave it at least slightly better than you found it. Not as a separate cleanup — as part of the work.

## Red Flags Checklist

Use when evaluating code structure:

- **Mixed abstraction levels** — business logic interleaved with infrastructure in the same method
- **Shallow modules** — interface complexity approximates implementation complexity
- **Classitis** — proliferation of tiny classes, especially pass-through delegators
- **Pass-through methods** — signature mirrors another's, adding no abstraction
- **Information leakage** — same design decision reflected in multiple modules
- **Temporal decomposition** — splitting by when, not by what knowledge is encapsulated
- **Primitive obsession** — raw `str`, `int`, `dict` where domain types should exist
- **Fat method signatures** — >3 parameters often indicate a missing typed object
- **Giant utility modules** — `utils.py`, `helpers.py` — give modules real names
- **Leaking infrastructure** — AWS API shapes, SQL syntax, file path schemes exposed to callers
- **Conjoined methods** — methods you always must read or call together

## Slop Red Flags — Weight Without Purpose

The red flags above are about the wrong shape. These are about shape that should not exist at all. Machine-written code accumulates them by default, so check every level you build.

Do not write, and remove on sight:

- **A guard with no named failure mode** — a try/except, null check, `?.`, or default value you cannot tie to a specific way this call fails. Trusted internal data does not need re-validating at every layer.
- **An abstraction with one implementation** — an interface, base class, registry, or strategy split for a second case that does not exist yet. Write the concrete thing; extract when the second case arrives.
- **A parameter no caller varies** — including a config key or env var nobody asked for. Every option is a branch you must keep working forever.
- **A wrapper that only delegates** — a layer whose whole body is a call with the same arguments. If it hides nothing, it is a name in the way.
- **A test that asserts on a double** — checking that a mock was called tests your wiring, not your behavior. Same for assertion-free tests, tests that restate the implementation, and many parameterized cases covering one branch.
- **A comment narrating the work** — "Enhanced…", "Now also handles…", "replaces the old…". Comments explain why code exists; git explains what changed.
- **A hedge on a decided change** — a flag, a fallback, or the old path kept beside the new one so the change can be switched off. If the decision is made, the replaced code is deleted. If you are not confident in the design, say so and stop; do not ship it wrapped in an escape hatch.

The test for each: name what breaks if it is not there. "Nothing, but it feels safer" means it does not go in.

## Design Questions

### When evaluating a component boundary
- What knowledge does this module hide?
- Is the interface simpler than the implementation?
- Could a caller use this without understanding internals?
- Does each layer provide a genuinely different abstraction?

### When auditing data flow
- Can I name the type that crosses this boundary?
- Is the type a domain concept or a raw container?
- Could I accidentally pass the wrong thing?

### When proposing structure
- Does the proposed change reduce information leakage?
- Would the module be understandable without tribal knowledge?
- Am I splitting because of temporal order rather than information boundaries?

### When the design is nearly settled — the change-amplification test

Name the most likely next requirement out loud. Then count the components this design would make you
edit to satisfy it.

- **One component** — the concept is localized. Ship it.
- **Two or three in the same layer** — acceptable.
- **A branch in the orchestrator, a field on the domain type, a new config key, a mapping table, and
  three tests** — one idea is living in five places. Fix it now; this is the cheapest moment it will
  ever be.

This is not a licence to build for the hypothetical requirement — that is speculative generality,
and it has its own entry in the Slop Red Flags. The count is a measurement, not a mandate: it tells
you where the *current* design has already scattered a single concept. The next requirement is just
the probe that makes the scattering visible.

## Language-Specific: Python

- **Functions over class hierarchies**: Use classes for genuine polymorphism, not for organizing steps
- **Pipeline as deep module**: `run(config) -> result`. Phases are internal details.
- **Configuration**: Typed config objects (frozen dataclasses), not `os.environ` scattered everywhere
- **Duplication vs abstraction**: Prefer small duplication over premature abstraction. Extract when a third copy appears.
