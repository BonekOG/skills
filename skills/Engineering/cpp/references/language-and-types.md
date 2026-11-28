# Language, Types, and Generic Programming

Read this reference when choosing C++ language features, public/internal types, templates, concepts, ranges, modules, or compile-time techniques.

Adopt language features because they improve semantics, safety, diagnostics, or maintainability—not merely because they are modern.

## Standard selection

- Use the standard declared by the repository/toolchain matrix.
- For greenfield work, prefer C++23 when all required compilers, standard libraries, platforms, and dependencies support the needed features reliably.
- Use C++20/17 where compatibility requires it.
- Use post-C++23/C++26 features only when the project explicitly supports the relevant compiler/library implementations.
- Prefer feature checks/toolchain configuration over ad-hoc compiler-version conditionals when practical.

## Value and parameter semantics

Prefer types that communicate semantics:

- `T`: owned value, copied/moved as part of the API.
- `T&`: required mutable borrow.
- `const T&`: required read-only borrow when copying is undesirable.
- `T*` / `const T*`: nullable non-owning object reference or interoperability boundary; document exceptions.
- `std::span<T>`: borrowed contiguous sequence with size.
- `std::string_view`: borrowed character sequence; never store unless lifetime is externally guaranteed.
- `std::unique_ptr<T>`: exclusive dynamic ownership or ownership transfer.
- `std::shared_ptr<T>`: actual shared lifetime, not general-purpose indirection.
- `std::optional<T>`: value may be absent without an error.
- `std::expected<T, E>` or repository equivalent: recoverable result/failure.
- `std::variant<...>`: closed set of alternatives.

For small trivially copyable values, passing by value is often clearer than `const&`; do not cargo-cult reference parameters.

## Move semantics

- Treat moved-from objects as valid but generally unspecified unless their type documents a stronger guarantee.
- Do not `std::move` a local in a normal return statement when it would inhibit or complicate return-value optimization without need.
- Use `std::forward<T>` only in forwarding contexts where `T&&` is a forwarding reference.
- Avoid APIs that force callers into unclear post-move states unless ownership transfer is the point of the operation.

## Templates and concepts

- Use templates when behavior is genuinely generic or static polymorphism provides meaningful value.
- Constrain templates with concepts/`requires` when C++20+ is available; make invalid instantiations fail with useful diagnostics.
- Prefer named concepts that express semantic requirements over long syntactic `requires` expressions repeated across APIs.
- Avoid exposing heavy template machinery in public headers unless zero-overhead genericity or customization requires it.
- Watch code-size, compile-time, debug-info, and ABI impact from template proliferation.
- Consider explicit instantiation or type erasure when implementation variation does not need to infect callers.
- Do not implement metaprogramming puzzles where normal runtime code is sufficient.

## Ranges and algorithms

- Prefer standard algorithms/ranges when they express the operation more clearly than index/iterator bookkeeping.
- Avoid opaque range pipelines that hide expensive copies, allocations, repeated traversal, or lifetime hazards.
- Materialize intermediate data when ownership or complexity becomes clearer by doing so.

## Strong types

Introduce a wrapper when it prevents a realistic category error, validates an invariant at construction, represents a unit/domain concept, or is already established vocabulary. Do not wrap every scalar for symmetry.

For units, IDs, sizes, offsets, timestamps, and money-like values, consider whether the cost of mixing raw primitives exceeds the cost of an explicit type.

## `constexpr`, `consteval`, and compile time

- Use `constexpr` for values/functions that benefit from usable compile-time evaluation or immutable semantic expression.
- Use `consteval` only when compile-time evaluation is a hard contract.
- Avoid moving ordinary business logic to compile time solely because it is possible; consider compiler cost and diagnostics.

## Modules

Use modules only when the repository/toolchain/build-system support is mature enough for all supported platforms. Treat modules as a dependency/encapsulation mechanism, not an automatic build-speed switch. Measure compile-time effects and maintain a coherent migration boundary rather than mixing mechanisms randomly.
