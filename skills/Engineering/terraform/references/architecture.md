# Architecture

Use this reference to choose root modules, state boundaries, environment strategy, and repository layout.

## Composition roots

A runnable root module is the composition root. It configures providers and backends, calls child modules, and passes dependencies through inputs and outputs. Keep the module tree shallow; flat composition is easier to reuse and review than deeply nested wrappers.

A root should represent a system or component with a coherent owner, lifecycle, and failure domain. It is not a folder for unrelated resources that happen to share an account.

## Boundaries

Split when teams change infrastructure independently, lifecycles differ, access controls differ, a failure should have a smaller blast radius, or plan time and lock contention become material. There is no universal resource-count threshold for splitting a state.

Do not split so finely that every resource needs a remote-state lookup. Each boundary adds coordination, backend configuration, and a new apply that can fail independently.

## Layouts

Monorepo with environment roots fits a small or medium team that wants one change history and local modules:

    terraform/
      modules/
        network/
        service/
      environments/
        dev/
        prod/
      .github/CODEOWNERS
      README.md

Separate live configurations and shared modules fits independent component owners or release cadences:

    live/
      networking/prod/
      payments/prod/
      payments/staging/

    terraform-aws-network/
    terraform-aws-service/

Workspaces per component and environment in HCP Terraform fit teams that want centralized runs, variables, permissions, and history:

    repo/
      components/
        networking/
        payments/
      modules/
        shared-service/

    # Workspaces: networking-prod, payments-prod, payments-staging

Name roots by domain and purpose. Document each root's owner, backend, lifecycle, and dependencies. Use `CODEOWNERS` for review routing; it does not replace branch protection.

## Environments

Separate directories with separate backends give the strongest isolation and the clearest blast radius. They duplicate a small amount of root configuration, which is often acceptable.

Terraform CLI workspaces select different state instances for the same configuration. They are not a security boundary and are a poor fit when environments need separate credentials, access controls, or radically different topology. Avoid conditionals keyed on `terraform.workspace` that make one configuration behave like several products.

HCP Terraform workspaces are separate execution contexts and are commonly used per component and environment. They can centralize approvals, variables, state access, and run history, but add platform coupling.

Variable precedence favors later sources: environment variables, then `terraform.tfvars`, then lexically ordered `*.auto.tfvars`, then command-line options. Keep layering small enough that a reviewer can predict the result.

## Interfaces between stacks

Prefer publishing specific values through a parameter store, DNS, or a data source owned by the consuming stack. `terraform_remote_state` reads root outputs, but access to it can expose the full state snapshot, including values the consumer does not need. Treat it as a broad interface, not a convenient one.

Keep outputs stable and documented. A consumer that depends on an internal resource attribute couples two stacks that were meant to evolve independently.

## Scale

Terraform walks the dependency graph with up to ten concurrent operations by default; `-parallelism` changes the limit but not the dependencies. Large graphs increase plan time and memory. Split on measured pressure, remove unnecessary ordering, and avoid wide modules that take every resource as an input.

## Pitfalls

- One root owns unrelated teams or environments. Split by ownership, lifecycle, and blast radius.
- A module wraps a single resource or exposes dozens of pass-through flags. Remove the abstraction.
- Child modules configure providers or assume a region. Move that decision to the root.
- Environment behavior hides in workspace-name conditionals. Make the mapping explicit or use separate roots.
- Every stack reads every other stack's state. Narrow the interface to the values actually needed.

## Sources

- Module composition: https://developer.hashicorp.com/terraform/language/modules/develop/composition
- CLI workspaces: https://developer.hashicorp.com/terraform/language/state/workspaces
- HCP workspace practices: https://developer.hashicorp.com/terraform/cloud-docs/workspaces/best-practices
- Variable precedence: https://developer.hashicorp.com/terraform/language/values/variables
