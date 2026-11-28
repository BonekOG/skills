# Modules

Use this reference when designing, reviewing, or consuming reusable Terraform modules.

## Purpose

A module should own a useful capability with a stable interface, such as a network, a service runtime, or a database with its required supporting resources. A module that wraps one resource adds indirection without a contract; a module that bundles an entire environment hides decisions its callers still own.

Prefer composition of small modules over one configurable module with dozens of flags. A caller should be able to predict the resources a module creates from its interface.

## Interface checklist

- Give every variable a concrete `type` and `description`.
- Use object types for related settings and `optional(TYPE, DEFAULT)` for stable defaults.
- Add `validation` for constraints that would otherwise fail late, such as unsupported environments or malformed identifiers.
- Use `nullable = false` when `null` must not override a default.
- Accept identifiers and stable values rather than resource objects from the caller.
- Avoid exposing provider-specific blocks unless translating them is the module's purpose.
- Export only outputs that callers need, each with a description.
- Mark sensitive inputs and outputs, while remembering they remain in state.
- Document required providers and any provider alias the module expects.

## Providers

Reusable modules declare provider requirements but do not configure providers. The root module supplies credentials, region, and aliases. A child that needs an alias declares it with `configuration_aliases` and receives it through `providers = { aws = aws.replica }`.

This keeps one credential and region decision at the composition root. A module that creates its own provider block cannot be safely called twice with different accounts or regions.

## Sources and versions

| Source | Fits | Watch |
| --- | --- | --- |
| Relative path | Modules maintained with the root | Changes affect every consumer immediately |
| Registry | Published reusable modules | Version constraint; the lock file does not pin modules |
| Git with tag or commit | Modules delivered from a repository | Tags can move; a full commit SHA is immutable |
| Vendored copy | Restricted networks or deliberate forks | Copy drift and manual upgrades |

Pin production roots to an exact registry version or an immutable Git reference. A broad constraint can select a newer matching release at the next initialization, even when the root configuration did not change.

Upgrade deliberately: change the source or version, run initialization with the intended behavior, inspect the plan, and commit the resulting configuration and lock changes together.

## Composition

Pass dependencies in and results out. Do not let a module discover another module's resources through shared naming conventions or remote state unless that coupling is explicit and documented.

Use `for_each` to create several instances of a child module keyed by stable identity, and `count` only for near-identical instances or a singleton. Moving a module call into `for_each` changes addresses; plan a `moved` block.

Keep module nesting shallow. Deep trees make provider flow, naming, and plan review harder. If a module mostly forwards variables to another module, collapse it.

## Testing a module

At minimum, format, validate, and run a plan-based test for the interface and conditional branches. Add apply-based tests only for behavior that mocks cannot establish, and clean up real infrastructure reliably. See [testing.md](testing.md).

## Pitfalls

- A module hardcodes region, account, naming prefix, or tags that belong to the caller.
- A module returns every resource attribute instead of a small contract.
- A module accepts a generic `map(any)` and reimplements type checking at runtime.
- A module creates a provider block or assumes the default alias.
- A module references another stack's remote state to avoid an input.
- A version range is treated as a lock; module selections are not recorded in `.terraform.lock.hcl`.

## Sources

- Module development: https://developer.hashicorp.com/terraform/language/modules/develop
- Module composition: https://developer.hashicorp.com/terraform/language/modules/develop/composition
- Providers within modules: https://developer.hashicorp.com/terraform/language/modules/develop/providers
- Module sources: https://developer.hashicorp.com/terraform/language/modules/configuration
