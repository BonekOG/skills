# SwiftUI Engineering

## Scope

Focus on SwiftUI correctness and behavior. Do not impose a whole-app architecture from this skill alone.

## State ownership

For every mutable state value, identify one owner.

- Local ephemeral UI state -> local `@State` where appropriate.
- Bindings -> use for controlled read/write access to state owned elsewhere.
- Observable reference models -> use Observation patterns appropriate to the deployment/toolchain and ownership semantics.
- Environment -> use for broadly scoped dependencies/state only when implicit access improves the design rather than hiding dependencies.

Avoid duplicating the same source of truth in multiple wrappers/models.

## View identity

- Use stable domain identity in `ForEach`/lists.
- Never use a changing display value as identity.
- Understand that changing identity destroys/recreates view-local state.
- Avoid `AnyView` as a routine type-erasure tool; it can hide structure and impede optimization/debugging.

## Composition

- Keep `body` declarative.
- Extract a subview when it has independent meaning, state, reuse, or a performance/debugging boundary—not merely to hit a line-count target.
- Move domain side effects/business rules out of rendering code.
- Keep expensive computation out of frequently recomputed view bodies; precompute/cache at the appropriate owner when measurement shows it matters.

## Async lifecycle

Prefer view-scoped `.task` for work whose lifetime follows the view. Use task IDs to cancel/restart work when input identity changes. Do not launch unmanaged long-lived tasks from `body` or transient event paths without ownership.

## Navigation and presentation

- Prefer type-safe navigation state where supported.
- Make deep-link restoration and sheet/full-screen item identity explicit.
- Avoid maintaining several partially overlapping navigation booleans that can conflict.

## Lists and scrolling

- Use stable identifiers.
- Avoid filtering/sorting expensive collections inline every render when it causes measurable repeated work.
- Use lazy containers for large offscreen content, not automatically for small static layouts.

## Accessibility

Accessibility is part of correctness:

- meaningful labels/values/hints only where needed
- support Dynamic Type and content size changes
- respect reduced motion/contrast where relevant
- ensure hit targets and focus order remain usable
- do not rely on color alone to convey state

## Animations

Tie animations to explicit state changes. Avoid blanket animations that animate unrelated updates. Validate transitions with reduced motion and interruption/reversal behavior where user interaction can race animations.

## Availability

Use APIs compatible with the minimum deployment target. Gate newer APIs with availability checks and provide a deliberate fallback where product behavior requires it.

## Performance review

Measure before rewriting. Investigate:

- unexpected view invalidations
- unstable identity
- expensive body computations
- image decode/downsample issues
- overly broad observable dependencies
- layout feedback loops
- unnecessary bridging

## Observation and wrapper selection

For modern Observation-based models (`@Observable`) where deployment support allows it:

- own a model in a view with `@State` when the view owns that model's lifetime;
- use `@Bindable` when a view needs bindings into an observable model it does not own;
- use the environment only for dependencies/state whose broad implicit scope is intentional;
- do not wrap the same logical state in both Observation and legacy `ObservableObject` machinery without a migration reason.

For legacy `ObservableObject` code, preserve `@StateObject` for ownership and `@ObservedObject` for observation of an externally owned object. Do not mechanically rewrite wrapper choices without checking lifetime semantics.

## View-model rule

Do not create a view model by default. Add a presentation model when it materially owns presentation state, transformations, effects, or coordination that would otherwise make the view hard to reason about or test. Tiny views with local state usually do not benefit from another reference type.

## Layout

Prefer SwiftUI's proposal-based layout system, stacks/grids, `Layout`, `ViewThatFits`, alignment guides, and container-relative sizing before reaching for `GeometryReader`. Use geometry reading only when the parent/child geometry relationship is actually part of the design.

## Images

For large/local/remote images:

- decode/downsample near the display size when memory matters;
- keep caching policy explicit;
- avoid repeatedly decoding the same large asset during view invalidations;
- make placeholder/error/cancellation states deliberate for remote images.

## Accessibility as a release criterion

For interactive UI verify at minimum:

- semantic labels/values/actions;
- Dynamic Type without truncating critical meaning;
- focus/navigation order;
- touch target usability;
- reduced motion where motion is nonessential;
- non-color affordances for state;
- chart/visual-data fallback semantics where applicable.
