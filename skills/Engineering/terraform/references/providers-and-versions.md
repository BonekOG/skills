# Providers and versions

Use this reference for version constraints, dependency locking, upgrades, and Terraform versus OpenTofu.

## Declare what you test

Set `required_version` to a range the project actually runs in CI and on developer machines. A range that admits untested versions turns an unrelated CLI upgrade into a behavior change.

Declare each provider in `required_providers` with a source address and a version constraint:

    terraform {
      required_version = ">= 1.9, < 2.0"

      required_providers {
        aws = {
          source  = "hashicorp/aws"
          version = "~> 6.0"
        }
      }
    }

Use pessimistic constraints for providers when the major version is the compatibility boundary. Avoid exact pins that block security patches unless the repository deliberately vendors dependencies.

## Lock file

Commit `.terraform.lock.hcl`. It records selected provider versions and checksums, so an unchanged configuration installs the same providers. It does not lock remote module selections.

Generate checksums for every platform that runs Terraform:

    terraform providers lock -platform=darwin_arm64 -platform=linux_amd64

Add platforms used by CI and by developers. A lock file with only one platform can fail checksum verification elsewhere.

Run `terraform init -upgrade` only as a reviewed dependency change. Inspect the lock diff, the provider changelog, and the resulting plan. Do not let a pipeline upgrade providers implicitly on every run.

## Provider configuration

Configure providers in root modules. Use aliases for multiple regions, accounts, or subscriptions and pass them explicitly to child modules. Keep credentials in the environment or workload identity, never in committed configuration.

Set provider defaults deliberately: default tags or labels, default region, and assume-role behavior. Provider defaults are part of the infrastructure contract even though they do not appear on each resource.

## Registry trust

Use official or organization-approved provider sources. Verify the source address, not only the local name. In restricted environments, use an approved mirror or filesystem mirror and document how the lock file is refreshed.

Provider upgrades can change defaults, add deprecations, or alter plan behavior without a configuration change. Treat a major upgrade as a change with its own review and rollback plan.

## Terraform and OpenTofu

OpenTofu is a fork created after HashiCorp moved Terraform from MPL 2.0 to BUSL 1.1 in 2023. Terraform 1.5.7 is MPL; releases from 1.6 onward use BUSL. OpenTofu remains MPL 2.0. Check the license attached to the exact release in use and obtain legal review for redistribution or hosted competitive use.

OpenTofu aims for language and provider compatibility. State interoperability is not symmetric: OpenTofu documents reading Terraform 1.x state, while Terraform may not reliably read state written with OpenTofu-specific features. The default registries are separate, so confirm provider and module availability.

Notable OpenTofu differences include built-in state and plan encryption and its own test command. Terraform also has native testing, so testing alone is not a differentiator.

When migrating, back up state, stop dual writers, run a no-change plan, and exercise a small change before switching. Do not point Terraform and OpenTofu at the same state.

## Pitfalls

- A provider constraint admits a major version the configuration was never tested against.
- The lock file is ignored, so CI and laptops resolve different provider builds.
- `init -upgrade` runs on every pipeline execution.
- A module's Git ref points at a movable branch.
- A migration switches binaries while both still write the same state.

## Sources

- Dependency lock file: https://developer.hashicorp.com/terraform/language/files/dependency-lock
- Provider lock command: https://developer.hashicorp.com/terraform/cli/commands/providers/lock
- Version constraints: https://developer.hashicorp.com/terraform/language/expressions/version-constraints
- OpenTofu migration: https://opentofu.org/docs/intro/migration/migration-guide/
- HashiCorp license FAQ: https://www.hashicorp.com/en/license-faq
