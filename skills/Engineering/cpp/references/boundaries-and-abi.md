# ABI, External Boundaries, Serialization, and Portability

Read this reference for shared libraries/plugins, public binary interfaces, C APIs, network/file formats, platform boundaries, or cross-platform behavior.

## API versus ABI

Source compatibility and binary compatibility are different. For a stable binary interface, review changes to:

- exported symbol names/visibility;
- class/struct size, alignment, member layout, bases, and virtual tables;
- inline functions and templates visible to consumers;
- exception/RTTI/compiler/runtime-library settings;
- STL types or allocator ownership crossing module boundaries;
- calling conventions and compiler-specific attributes;
- ownership of memory/resources allocated by another module/runtime.

When long-lived/compiler-independent stability is required, consider a narrow C ABI with opaque handles and explicit ownership/versioning. Use PImpl when it provides useful binary/layout isolation, not as automatic ceremony.

## Shared-library/plugin boundaries

- Define who allocates/frees resources.
- Do not pass C++ exceptions through C/foreign boundaries.
- Keep allocator/runtime mismatches in mind, especially across DLL/plugin boundaries.
- Version interfaces deliberately.
- Fail plugin loading/handshake cleanly when versions/capabilities are incompatible.
- Keep threading/reentrancy expectations explicit.

## Serialization and wire formats

Never serialize a native struct by dumping its object bytes unless the format is intentionally compiler/platform-specific and fully controlled.

For persistent/network formats define explicitly:

- schema and versioning;
- byte order;
- integer widths and signedness;
- alignment/padding independence;
- length/count limits;
- optional/unknown field behavior;
- backward/forward compatibility policy;
- validation before allocation/use;
- partial read/write handling;
- checksums/authentication where required by the protocol threat model.

Use established serializers/protocols already present in the repository when suitable.

## Filesystem and IO

- Use `std::filesystem` where it matches supported platforms, but do not assume path encoding/case sensitivity/permissions semantics are identical.
- Handle partial reads/writes and interruption where the underlying API can produce them.
- Avoid assuming one `read`/`write` transfers the full buffer.
- Define durability requirements explicitly before adding flush/fsync behavior.
- Use atomic replace/write-then-rename patterns for files that must not be left partially updated, subject to filesystem guarantees.

## Portability

Do not assume:

- `long` or pointer sizes;
- native endianness;
- `char` signedness;
- alignment beyond the type contract;
- filesystem case sensitivity or path encoding;
- POSIX behavior on Windows or Windows behavior elsewhere;
- x86 memory-ordering behavior on ARM;
- unaligned memory access is safe/cheap;
- compiler extensions exist across the matrix.

Use fixed-width integer types when the external representation requires fixed width, not indiscriminately for ordinary arithmetic.

Localize platform-specific code behind small adapters when behavior genuinely differs. Avoid a giant abstraction layer that merely mirrors OS APIs.
