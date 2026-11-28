# Operating model

Use this reference to decide whether Terraform is the right tool, which operating mode applies, and how much risk a change carries.

## What Terraform does

Terraform reads the configuration as desired state, refreshes the objects recorded in state, computes a dependency graph, and proposes the difference as a plan. Apply executes that graph and records the result in state. The state file is the mapping between configuration addresses and real objects, not a copy of the infrastructure.

Idempotence is conditional. Providers can normalize values, apply defaults, or report attributes differently than configured, so a second plan is not guaranteed to be empty. A plan is a proposal based on current state and provider behavior, not proof that apply will succeed.

Terraform has no rollback transaction. A failed apply can leave some objects changed and others untouched. State reflects what Terraform knows it changed; restoring state does not restore infrastructure or data.

## Fit

Terraform fits long-lived resources with stable identities and CRUD APIs, owned through configuration, where a shared lifecycle and reviewable change history matter. Typical examples are cloud accounts, networks, managed data stores, DNS, identity, and platform add-ons.

It fits poorly when:

- the resource is per-request or per-user application data;
- no stable identifier or import path exists;
- the provider cannot manage the resource safely or completely;
- another controller already owns the object, such as a Kubernetes operator or GitOps reconciler;
- the change is an emergency console fix that nobody intends to codify.

Terraform can manage Kubernetes objects, but doing so alongside a GitOps controller creates two owners. Pick one owner for each object.

## Modes and authorization

| Mode | Typical actions | Authorization |
| --- | --- | --- |
| Configuration development | Read repository, edit HCL, run format, validate, tests | No live mutation |
| Plan review | Init, plan, show, inspect state, read cloud metadata | Read-only intent; a plan can read cloud APIs and refresh state |
| Live apply | Apply, destroy, import, state changes, backend migration, unlock | Explicit for the exact action and target |
| Diagnosis and recovery | Inspect state, plans, logs, cloud inventory, lock metadata | Read-only first; recovery actions follow the live-apply rule |

Initialization is not always harmless. `terraform init` can download providers, rewrite the lock file, and configure a backend. A refresh can update state. Treat unexpected writes during a supposedly read-only step as an incident.

## Risk tiers

Classify by consequence, not by environment label:

- **Low:** new isolated resources in a disposable environment, no replacements or deletions.
- **Medium:** changes to non-production resources, provider or module upgrades, identity changes with limited scope.
- **High:** production changes, replacement of stateful resources, IAM widening, public network exposure, DNS, shared modules, backend migration.
- **Critical:** destruction of data stores, changes to security controls or audit trails, state surgery on shared production state, cross-account trust changes.

Replacement is often more dangerous than an explicit destroy because it can appear as a routine update. Inspect the reason and the resource's data lifecycle.

## Ownership and scope

Each root module and state should have an identifiable owner. A change should stay within that owner's resources. Cross-team dependencies belong in explicit outputs or a shared data source, not in edits to another team's state.

Do not adopt unmanaged resources, rename addresses, or delete leftovers unless the request includes that scope. "Clean up the plan" is not authorization to import or destroy unrelated objects.

## Assumptions and evidence

Record the root module, backend, workspace, account, region, and CLI version that the conclusion depends on. When any of these is unknown, offline advice can still be useful, but a live operation must stop before mutation.

Report direct evidence separately from inference. A clean validation run proves only that the enabled checks passed for the inputs they examined.

## Sources

- Terraform state purpose: https://developer.hashicorp.com/terraform/language/state/purpose
- Plan command: https://developer.hashicorp.com/terraform/cli/commands/plan
- Apply command: https://developer.hashicorp.com/terraform/cli/commands/apply
- Dependency graph: https://developer.hashicorp.com/terraform/internals/graph
