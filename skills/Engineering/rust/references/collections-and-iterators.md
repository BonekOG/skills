# Collections and iterators

## Choose collections by access pattern

- `Vec<T>`: default ordered contiguous collection.
- `VecDeque<T>`: efficient push/pop at both ends.
- `HashMap/HashSet`: general keyed membership/lookup.
- `BTreeMap/BTreeSet`: ordered keys, range queries, deterministic iteration.
- specialized/small collections only after evidence or domain need.

Do not choose a complex collection for theoretical performance without matching workload.

## Iterators vs loops

Prefer iterator transformations when they clearly express:

- map/filter/fold/search/collect;
- lazy composition;
- ownership/borrowing intent.

Prefer `for`/`while` when:

- control flow is stateful;
- early exits/multiple mutable states are clearer;
- iterator chains become difficult to read.

“Iterator = always better” is not a rule.

## Indexing

Avoid manual index loops when direct iteration works.
Use indexing when the index itself is meaningful or random access is required.
Prefer safe access (`get`) when an index can be invalid at runtime.

## Entry API

For map read-modify-write patterns, prefer `entry` to duplicate lookups where it improves clarity and performance.

## Allocation

Watch for:

- repeated `collect` between iterator stages;
- `format!`/`to_string()` in hot loops;
- rebuilding temporary vectors only to iterate once;
- repeated growth when capacity is known.

Preallocate only when size is known or profiling shows growth cost matters.

## String handling

- Prefer `&str` for borrowed text.
- Do not assume byte offsets are valid character boundaries.
- Distinguish bytes, Unicode scalar values (`char`), and grapheme clusters.
- Use bytes for protocols when the protocol is byte-oriented.
