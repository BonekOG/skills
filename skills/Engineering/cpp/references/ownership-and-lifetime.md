# Ownership, Lifetime, Memory Safety, and Undefined Behavior

Read this reference for resource management, pointers/references/views, containers, callbacks, invalidation, buffers, or memory-safety questions.

## Ownership hierarchy

Prefer, in order:

1. Automatic storage/value member.
2. Standard container/value type.
3. RAII wrapper around an external resource.
4. `std::unique_ptr` for necessary dynamic exclusive ownership.
5. `std::shared_ptr` only when multiple owners genuinely determine lifetime.

Use `std::weak_ptr` to observe a shared object without extending lifetime or to break ownership cycles. Never use `shared_ptr` merely because ownership is unclear—resolve the ownership design first.

## RAII

Every acquired resource should have one owner whose destructor releases it: memory, file descriptors/handles, sockets, locks, mappings, transactions, GPU resources, subscriptions, temporary files, and similar resources.

- Prefer Rule of Zero.
- If custom special members are required, review copy/move/destruction as one coherent ownership contract.
- Destructors should not emit exceptions during unwinding.
- Use scope guards for multi-step cleanup that has no natural owning type.

## Borrowed data

A pointer, reference, iterator, `span`, or `string_view` does not own its target.

Before storing a borrow, prove that the owner outlives every use. Be especially careful with:

- views into temporaries or local strings/vectors;
- callbacks capturing stack references;
- asynchronous work capturing `this` or borrowed state;
- references into containers that can reallocate/erase;
- returned views into internal mutable buffers;
- lambdas queued beyond the lifetime of captured objects.

When lifetime cannot be proved simply, redesign ownership rather than documenting hope.

## Container and iterator invalidation

Before keeping pointers/references/iterators into a container across mutation, check that container's invalidation rules. Treat `vector` growth, erase/insert, unordered-container rehashing, string mutation, and ownership moves as potential invalidation points.

Prefer stable IDs/handles/indexes only when their validity model is explicit.

## Buffer and bounds safety

- Prefer containers and `std::span` over naked pointer+length conventions inside C++ code.
- Keep size information with the view throughout the call chain.
- Validate external sizes/offsets before allocation, pointer arithmetic, indexing, casting, or multiplication/addition.
- Check arithmetic overflow when computing byte counts, strides, dimensions, offsets, or capacities from untrusted/external values.
- Do not assume `std::vector::operator[]` performs bounds checks. Use prior validated bounds or checked access where failure must be detected.
- Avoid C string functions and raw arrays unless interoperability requires them and the bounds contract is explicit.

## Undefined behavior watchlist

Actively look for:

- use-after-free / dangling reference / double delete;
- uninitialized reads;
- out-of-bounds indexing or pointer arithmetic;
- invalid object lifetime/type punning;
- strict-aliasing and alignment violations;
- signed integer overflow;
- invalid shifts and narrowing assumptions;
- dereferencing null/invalid pointers;
- data races;
- iterator/reference invalidation;
- accessing moved-from objects beyond their documented guarantees;
- concurrent container access without the required synchronization.

Prefer `std::bit_cast`/`memcpy`-based representation transfer where appropriate instead of aliasing tricks.

## Raw allocation

Avoid direct `new`/`delete` in application code. When custom allocation is required for measured performance or system constraints, isolate it behind an RAII/value-semantic abstraction and test failure/alignment/lifetime behavior explicitly.

Use `std::pmr` only when allocator control or allocation batching is a real requirement; do not introduce polymorphic allocators without measured or architectural value.
