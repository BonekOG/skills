# Swift Networking

## Transport boundary

Separate:

- request construction
- transport execution
- HTTP semantics/status handling
- decoding/encoding
- domain mapping
- authentication/retry policy

Avoid returning raw `URLSession` tuples throughout the app.

## Async behavior

Use `URLSession` async APIs where available. Preserve cancellation all the way to the request. Do not wrap async APIs in extra `Task` layers without a lifetime reason.

## HTTP correctness

- Validate status codes separately from decoding.
- Treat redirects, empty bodies, 204 responses, content types, and server error payloads deliberately.
- Configure timeouts according to product behavior rather than one arbitrary global value.
- Respect idempotency before retrying.
- Use exponential backoff/jitter only for errors where retry is meaningful.
- Do not retry authentication/validation failures blindly.

## Models

Use transport DTOs when server schema and domain model evolve independently. Decode dates/numbers/keys explicitly when wire formats are not Swift defaults.

## Auth and secrets

Do not log authorization headers, cookies, access/refresh tokens, signed URLs, or sensitive bodies. Store long-lived credentials using an appropriate secure store, not `UserDefaults`.

## Testability

Test request formation and response mapping without live internet. Use controlled protocol/session boundaries or local fixtures. Reserve live integration tests for explicit environments.
