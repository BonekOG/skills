# Security

## External input

Treat network, file, environment, CLI, IPC, FFI, and deserialized data as untrusted until validated.

Validate:

- length/bounds;
- integer ranges;
- enum/value domains;
- path assumptions;
- resource limits;
- encoding/format;
- authorization context.

## Deserialization

Avoid unbounded allocations from attacker-controlled lengths.
Apply size/depth/time limits when parsing potentially hostile input.
Do not assume serde success means semantic validity.

## Secrets

- Never log secrets/tokens/private keys.
- Prefer secret-wrapper types that reduce accidental formatting where available.
- Avoid long-lived plaintext copies.
- Zeroization may be appropriate for specific threat models; do not claim it solves all memory disclosure risks.

## Filesystem

Consider:

- path traversal;
- symlinks/races;
- permissions;
- atomic writes;
- temp-file security;
- platform-specific path behavior.

## Command execution

Avoid shell concatenation with untrusted input.
Pass arguments structurally to `Command`.
Be explicit about environment and working directory when security-relevant.

## Supply chain

- Keep dependencies deliberate and updated.
- Prefer well-maintained crates for security-critical primitives.
- Do not implement cryptography ad hoc.
- Use dependency audit/advisory tooling where the project supports it.
- Review feature flags because they can materially change dependency surface.

## Denial of service

Bound:

- queues/channels;
- request/body sizes;
- recursion/depth;
- retries;
- concurrency;
- expensive regex/parsing;
- memory growth.

Security failures should not become panics where controlled errors are possible.
