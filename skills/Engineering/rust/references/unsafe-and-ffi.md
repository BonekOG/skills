# Unsafe Rust and FFI

## Unsafe policy

Unsafe is permitted only when:

- required for FFI/hardware/low-level primitives;
- necessary for a measured performance need not achievable safely;
- implementing a safe abstraction whose invariants can be stated and defended.

## Every unsafe block must answer

1. What operation is unsafe?
2. What preconditions does Rust require?
3. Why are those preconditions true here?
4. Who maintains the invariant over time?

Use a nearby `SAFETY:` comment for non-trivial unsafe operations.

## Audit checklist

Check:

- pointer validity and provenance;
- alignment;
- initialization;
- aliasing / mutable exclusivity;
- lifetimes;
- bounds;
- integer conversion/overflow;
- layout assumptions (`repr(C)`, packing);
- panic/unwind across FFI;
- ownership transfer/freeing responsibility;
- thread-safety;
- callbacks and reentrancy.

## FFI

- Prefer `repr(C)` where ABI layout is required.
- Use explicit integer widths.
- Define ownership of allocated memory in both directions.
- Convert raw external inputs into validated safe Rust types immediately.
- Do not let unwinding cross an ABI boundary unless explicitly supported.
- Keep raw pointers at the boundary; expose safe wrappers internally.

## Unsafe KPI

Target: **0 undocumented non-trivial unsafe blocks**.
A raw count of unsafe blocks is not itself a quality score; justified low-level crates may contain many.
Track unsafe surface changes in review.
