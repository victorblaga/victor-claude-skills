# Implementation Agent Protocol

This document defines how implementation agents must approach writing code. Every subagent spawned for Phase 4 (task implementation) MUST follow this protocol. The subagent should read this file directly; the orchestrator does not need to paste it verbatim into every prompt.

## Performance-First Thinking

Before writing any implementation code, the agent MUST assess whether the code is performance-sensitive. Code is performance-sensitive if it:

- Processes collections of items (lists, streams, query results)
- Makes I/O calls (database queries, HTTP requests, file operations)
- Runs in a loop or is called repeatedly
- Handles data that could grow significantly (user data, event streams, batch jobs)

### When code IS performance-sensitive: Pseudocode-First Pass

**Do not jump straight to implementation.** Instead:

1. **Write a pseudocode sketch or commented outline** of the algorithm, mapping out:
   - Every collection operation and its Big O complexity
   - Every I/O call (DB query, HTTP request, file read/write) and whether it's inside a loop
   - Data structure choices and whether they support the access patterns needed (random access? lookup by key? ordered iteration?)

2. **Identify bottlenecks** in the sketch:
   - **N+1 queries**: A DB query inside a `for` loop over N items → must be replaced with a single batch query before the loop
   - **Wrong data structures**: Index access on a linked list (e.g., Scala's default `List`, which is a linked list — `list(i)` is O(n)), `contains` on an unsorted list (O(n) per call) when a `Set` or `Map` would give O(1)
   - **Unbounded data loading**: Loading an entire table/collection into memory when only a subset is needed
   - **Quadratic or worse patterns**: Nested loops over the same collection, repeated linear scans that could be replaced with a hash index

3. **Iterate on the sketch** until bottlenecks are resolved:
   - Pre-build lookup indices (`Map`/`HashMap`/dictionary) before entering loops
   - Replace N+1 queries with batch reads (e.g., `WHERE id IN (...)` or equivalent)
   - Choose data structures that match access patterns (need random access? use `Vector`/`Array`/`ArrayList`, not linked list)
   - Verify the overall complexity is acceptable for the expected data size

4. **Only then write the actual implementation**, following the optimized sketch.

### When code is NOT performance-sensitive

Skip the pseudocode pass. Implement directly. Don't over-optimize code that runs once, handles small fixed-size data, or is not on a hot path.

## I/O Batching Rules

By default, I/O operations should follow these batching principles. These are strong defaults, not blind laws. If correctness, transactional semantics, ordering requirements, rate limits, API constraints, or a provably tiny bounded workload justify an exception, the agent may deviate — but it must say so explicitly in its task report.

### Database Reads
- Do not query inside an unbounded or data-dependent loop when batching is possible. Collect IDs/keys first, then batch query.
- For large result sets, use streaming/cursors/pagination — don't load everything into memory at once.
- Prefer `WHERE id IN (batch)` over individual lookups.
- If the total set is very large (>10K items), chunk the `IN` clause into batches (e.g., 1000 items per batch) to avoid query parameter limits.

### Database Writes
- Do not insert or update one row at a time in an unbounded or data-dependent loop when bulk operations are available.
- Accumulate items in memory (batch size ~1K-10K depending on row size), then do batch inserts/upserts.
- Use bulk operations: `INSERT INTO ... VALUES (...), (...), (...)` or equivalent ORM batch methods.
- For very large writes, chunk into batches and commit per batch to avoid transaction size limits and memory pressure.

### External API Calls
- If the API supports batch endpoints, use them.
- If not, prefer concurrent or parallel calls for independent requests when rate limits, ordering, and external system constraints allow it.
- Respect rate limits — implement backoff when batching concurrent calls.

### File Operations
- Buffer writes — don't flush after every line/record.
- For large file reads, stream line-by-line or in chunks rather than loading the entire file into memory.

## Data Structure Selection

Choose data structures based on access patterns, not convenience:

| Access pattern | Wrong choice | Right choice |
|---|---|---|
| Lookup by key | `List` + linear scan | `Map`/`HashMap`/`dict` |
| Check membership | `List.contains()` | `Set`/`HashSet` |
| Random access by index | Linked list (`List` in Scala) | `Vector`/`Array`/`IndexedSeq` |
| Ordered iteration + fast lookup | `Map` (unordered) | `TreeMap`/`SortedMap` |
| Append-heavy collection building | Prepending to `List` then reversing | `ArrayBuffer`/`mutable.ListBuffer`/`Vector` builder |
| Queue/FIFO | `List` (O(n) dequeue from end) | `Queue`/`ArrayDeque` |

**Language-specific notes:**
- **Scala**: Default `List` is a singly-linked list. Use `Vector` for indexed access. Use `.view` or `LazyList` for lazy evaluation of chains of `map`/`filter`/`flatMap` to avoid intermediate collection allocation.
- **Python**: Default `list` is an array (good for index access). Use `dict` for key lookup, `set` for membership. Use generators for lazy iteration.
- **JVM general**: Be aware of boxing costs — prefer primitive arrays or specialized collections for numeric-heavy code.

## Pre-computation and Indexing

Before entering a loop that needs to look up related data, build an index:

```
// BAD: O(n*m) — linear scan inside a loop
for item in items:
    related = allRelated.filter(r => r.itemId == item.id)  // O(m) per iteration

// GOOD: O(n+m) — build index first, then O(1) lookup
val relatedByItemId = allRelated.groupBy(_.itemId)  // O(m) once
for item in items:
    related = relatedByItemId.getOrElse(item.id, Nil)  // O(1) per iteration
```

This pattern applies everywhere: if you're about to do a lookup inside a loop, build the lookup table first.

## Memory Awareness

- Don't hold references to large collections longer than needed — let them be GC'd.
- For streaming workloads, process items in windows/batches rather than accumulating everything.
- When doing transformations on large collections, prefer `map`/`flatMap` with lazy evaluation (streams, views, iterators) over eagerly creating intermediate collections.
- Be cautious with `.toList` / `.toSeq` on large streams — this materializes everything into memory.

## Verification Checklist

Before considering implementation complete, the agent MUST verify:

- [ ] No database query or external API call is made inside a loop over a collection
- [ ] Collections are accessed using data structures appropriate for the access pattern
- [ ] Large data sets are processed in batches/streams, not loaded entirely into memory
- [ ] Lookup indices (Maps/Sets) are pre-built before loops that need them
- [ ] Overall algorithmic complexity is reasonable for expected data sizes
- [ ] Batch sizes for I/O operations are bounded (not unbounded accumulation)
