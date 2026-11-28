# Swift Architecture

## First rule

Choose the **smallest architecture that makes state ownership, dependencies, side effects, navigation, and tests explicit**.

Do not migrate architecture because a pattern is fashionable.

## Decision guide

### Simple feature / local SwiftUI

Use direct model/state composition when state is local, workflows are shallow, and dependencies are few.

### MVVM

Useful when presentation state/transformations and asynchronous interactions are complex enough to deserve a testable presentation boundary. Avoid giant view models that become feature god objects.

### MVI / reducer-style

Useful when explicit state transitions, event logs, reproducibility, or complex state machines matter. Cost: more ceremony and indirection.

### TCA

Useful when the codebase already benefits from reducer/effect composition, dependency/test infrastructure, and explicit navigation/state. Do not introduce it casually for one screen.

### Clean / layered architecture

Useful when domain logic is substantial, platform/storage/transport implementations must vary, or multiple frontends share core behavior. Avoid one-interface-per-class boilerplate.

### Coordinator / router

Useful when navigation is sufficiently complex to deserve ownership outside individual views/controllers. Avoid duplicating SwiftUI's own navigation model without a real need.

## Boundaries

Healthy boundaries often align with:

- volatile external systems (network, database, keychain, clock, notifications)
- independent business capabilities
- independently testable domain logic
- module ownership/team boundaries

Avoid layers whose only job is forwarding identical method calls.

## Architecture smells

- View/ViewController performs domain/network/database logic directly.
- One service owns unrelated features.
- One view model owns navigation, storage, networking, formatting, analytics, and business rules.
- Every concrete type has a one-to-one protocol solely for mocks.
- Repositories merely rename framework APIs without hiding a meaningful boundary.
- Domain layer imports UI or transport implementation details.
- Cyclic package/module dependencies.

## Refactoring rule

Preserve observable behavior and migrate one seam at a time. Add characterization tests before moving code whose behavior is poorly understood.
