# Phase 0: Constraints Discovery

Gather facts that constrain what architectures are viable. This is "figure out the physics before designing the building."

Certain constraints fundamentally shape what architectures are possible. Streaming 100M records vs loading 10K into memory are different architectures, not different implementations. If you discover this during implementation, you have to redo everything. Phase 0 exists to prevent that.

## For Build Mode (Greenfield)

Ask the user targeted questions. Only ask questions whose answers would change the architecture. Keep to 4-6 questions max — don't interrogate.

Categories to probe:

- **Data scale**: How much data? Growth trajectory? This determines streaming vs batch, indexing strategy, storage format.
- **Performance envelope**: Latency requirements? Throughput? SLAs? This determines sync vs async, caching layers, parallelism strategy.
- **Infrastructure**: What services are available? Database, message queue, object storage, compute limits, memory ceiling.
- **Deployment**: Single process? Distributed? Container limits? Serverless?
- **Concurrency model**: Single-threaded? Multi-threaded? Event-driven? This determines actors vs threads vs async vs process pools.
- **Data sources and sinks**: Where does data come from? Where does it go? Formats? APIs? Push vs pull?

Not every category applies to every project. Ask about the ones that matter for this specific system.

## For Refactor/Refine Mode

Explore the existing code AND ask the user. Some constraints are implicit in code, some are only in the operator's head.

Launch explorer subagents to scan for:

- Batch sizes, streaming patterns, pagination
- Connection pool configs, timeouts, retry policies
- Memory management patterns (generators, iterators vs loading all into memory)
- Data volume hints (comments, variable names like `batch_size`, `max_records`, `CHUNK_SIZE`)
- Infrastructure dependencies (what databases, queues, storage services are configured)
- Resource limits (thread pool sizes, worker counts, memory caps)

Then ask the user to confirm and supplement what the code reveals:

> "I found the pipeline processes data in batches of 1000 from S3. Is this due to memory constraints? What's the actual data volume in production?"

> "The code uses a thread pool of 4 workers. Is that a deliberate choice or a default? What's the machine spec?"

The code tells you what IS. The user tells you what SHOULD BE — actual production volumes, upcoming growth, planned infrastructure changes, known pain points.

## Output

Write a constraints section at the top of `plan.md`:

```markdown
## Constraints
- Data: ~120M site records across 3 sources, growing ~5% quarterly
- Performance: Full rebuild must complete in < 2 hours
- Infrastructure: Single EC2 instance, 16GB RAM, S3, PostgreSQL, SQS
- Concurrency: Multi-threaded (Pykka actors), single process
- Implication: Streaming architecture mandatory. Cannot load full datasets
  into memory. Stagers must process records in batches. Temporary SQLite
  for staging (fits in local disk, faster than network round-trips to PostgreSQL).
```

The **Implication** line is the most important part. It's where constraints become architectural decisions. Always write implications explicitly — they bridge Phase 0 and the first horizontal slice.

Multiple implications are fine when constraints interact:

```markdown
- Implication: Streaming mandatory (data scale + memory limit).
  Parallel stagers viable (multi-threaded + independent sources).
  Local staging DB preferred over network DB (latency + single machine).
```

## Architecture-Shaping vs Implementation Details

Not every constraint shapes the architecture. The test: "Would changing this fact change the top-level component diagram?"

**Architecture-shaping** (ask about these):
- "Data is 100M rows" -- streaming vs batch changes component design
- "Must complete in 2 hours" -- parallelism strategy changes the component graph
- "Runs on 16GB machine" -- can't hold full dataset in memory, changes data flow
- "Three independent data sources" -- parallel ingestion vs sequential, changes orchestration
- "Results must be atomic" -- transaction strategy, changes how components coordinate

**Implementation details** (don't ask about these in Phase 0):
- "Which ORM?" -- doesn't change component boundaries
- "Log format?" -- doesn't affect architecture
- "Python version?" -- rarely architecture-shaping
- "Naming conventions?" -- style, not structure
- "Which testing framework?" -- no architectural impact

If you're unsure whether something is architecture-shaping, apply the test. If the answer is "it changes what components exist or how they connect," it belongs in Phase 0.

## When to Skip Phase 0

- **Small scope** -- the constraints are obvious from context (e.g., "add a CLI command to export JSON")
- **Refine mode** -- you're only improving abstractions, not changing data flow or component boundaries
- **User provided constraints** -- the request already includes enough to proceed (e.g., "refactor this to stream from S3 in batches of 10K")

Even when skipping, note any implicit constraints in `plan.md` so they're documented. A one-liner is fine:

```markdown
## Constraints
- Small CLI tool, single-threaded, in-memory dataset (< 1K records). No architectural constraints.
```

This prevents future confusion about why certain design choices were made.
