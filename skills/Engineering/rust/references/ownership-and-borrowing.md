# Ownership, borrowing, and lifetimes

## Decision hierarchy

For an input parameter:
1. `&T` / `&mut T` if the function only needs temporary access.
2. Slice/view type (`&str`, `&[T]`, `&Path`) instead of borrowing an owned container where appropriate.
3. `T` when ownership transfer is part of the operation.
4. `Cow<'a, T>` when most callers can borrow but some paths need conditional ownership.
5. `Arc<T>` / `Rc<T>` only when shared ownership is truly part of the model.

## Preferred signatures

Prefer:
```rust
fn parse(input: &str)
fn process(items: &[Item])
fn open(path: &Path)
```

over:
```rust
fn parse(input: &String)
fn process(items: &Vec<Item>)
fn open(path: &PathBuf)
```

unless the owned type itself is semantically required.

## Clone discipline

A clone is acceptable when:
- ownership genuinely needs to diverge;
- a value crosses a task/thread boundary and cannot safely borrow;
- data is intentionally snapshotted;
- the object is cheap and duplication improves a clearly bounded API;
- measurement shows ownership gymnastics would be more costly/complex than copying.

A clone is suspicious when:
- inserted immediately after a borrow-checker error without model analysis;
- inside a hot loop;
- cloning a large collection to enable mutation;
- cloning before conversion when moving would work;
- repeated across async task creation because ownership was not planned.

During review, classify every non-trivial clone as **semantic**, **boundary**, **performance-insensitive**, or **debt**.

## Lifetimes

- Prefer lifetime elision when obvious.
- Introduce explicit lifetimes to express a real relationship, not merely to satisfy syntax.
- Avoid structs holding references unless the borrowing lifetime is central to the type's purpose.
- Prefer owned internal state when long-lived borrowed state would infect the architecture with difficult lifetime coupling.
- Do not use `'static` as a generic fix; understand whether the API requires owned/static data.

## Mutable borrowing

- Keep mutable borrow scopes small.
- Compute values before taking a mutable borrow if it avoids aliasing conflicts.
- Consider split borrows through field access or collection APIs.
- Prefer `get_mut`, `entry`, `split_at_mut`, iterators, or dedicated methods over unsafe aliasing workarounds.

## Interior mutability

Use intentionally:
- `Cell<T>`: copy-like values, single-threaded.
- `RefCell<T>`: runtime borrow checking, single-threaded.
- `Mutex<T>`: mutual exclusion across threads/tasks when blocking semantics are acceptable.
- async mutex: only when a lock must be held across `.await`.
- atomics: small lock-free shared state with explicitly understood memory ordering.

Interior mutability is not a substitute for unclear ownership.
