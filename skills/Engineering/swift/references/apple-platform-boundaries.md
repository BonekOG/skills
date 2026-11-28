# iOS / Apple Platform Boundaries

## Deployment target is a contract

Before using a modern API, inspect the actual minimum OS. Do not “fix” availability by silently raising the deployment target unless explicitly authorized.

## Framework boundaries

Prefer native SwiftUI for SwiftUI features, but bridge to UIKit/AppKit when the platform capability genuinely requires it. Keep wrappers small and lifecycle-correct.

When using `UIViewRepresentable` / `UIViewControllerRepresentable` (or AppKit equivalents):

- make creation/update responsibilities explicit
- avoid recreating heavyweight platform views unnecessarily
- keep coordinators focused on delegate/callback bridging
- prevent feedback loops between SwiftUI state updates and platform delegate callbacks
- clean up observers/resources when lifetime ends

## Main actor

UI state and UI framework interactions belong on the appropriate main-actor boundary. Do not mark large unrelated service layers `@MainActor` merely to silence access errors.

## Lifecycle

Account for:

- scene activation/backgrounding
- interruption and cancellation
- restoration/deep links
- resource cleanup
- notifications/observers
- task lifetime relative to scenes/views/controllers

## Platform abstractions

Do not hide platform differences behind a “universal” abstraction if the behaviors are genuinely different. Prefer explicit conditional conformance/implementations when semantics diverge.
