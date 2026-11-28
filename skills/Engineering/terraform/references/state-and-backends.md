# State and backends

Use this reference for backend selection, state layout, refactoring, drift, and recovery.

## State is sensitive

State maps configuration addresses to real objects, tracks provider metadata, and caches attributes for planning. It is JSON and can contain passwords, tokens, keys, and private endpoints in plaintext. `sensitive = true` redacts some displays but does not remove values from state.

Treat state, state backups, saved plans, and plan JSON as secrets. Restrict read access, encrypt storage, enable versioning or snapshots, and audit access. Never commit them.

## Backend choice

| Backend | Locking | Operational notes |
| --- | --- | --- |
| Local | Local file locking | Fine for experiments; poor for shared production state |
| S3 | S3 lock file with `use_lockfile = true` | DynamoDB locking is deprecated and slated for removal; do not adopt it for new configurations. Enable bucket versioning and encryption; scope IAM to the state and lock paths |
| GCS | Native | Enable Object Versioning; use CMEK where required |
| AzureRM | Blob lease | Enable blob versioning or soft delete; restrict data-plane access |
| HCP Terraform | Workspace run queue and state lock | Centralized runs, permissions, history, and policy |
| Postgres or Consul | Native | Encryption, backups, and retention depend on how the service is operated |

Use a shared backend with locking for any state that more than one person or pipeline can change. Locking serializes Terraform writers; it does not prevent console changes or protect other states.

## Configuration

Keep credentials out of backend blocks and `-backend-config` values. Backend settings are written into `.terraform` metadata and can appear in saved plans. Prefer environment credentials, workload identity, or the provider's standard credential chain.

Partial backend configuration is useful when the same root runs in several environments: keep non-secret structure in the backend block and pass the environment-specific bucket, key, or container at initialization. Commit the resulting lock file, not backend credentials.

`terraform init -backend=false` skips backend initialization for local validation. It does not make a production operation state-free.

## Layout

Keep resources together when they share owner, lifecycle, and failure impact. Split along lifecycle, team, access-control, or blast-radius boundaries when independent change or lock contention justifies the coordination cost.

CLI workspaces reuse one configuration and one backend. They separate state instances, not permissions or credentials. Use separate roots or separate managed workspaces when environments need stronger isolation.

For cross-stack values, publish only the needed outputs. A `terraform_remote_state` consumer can read the full state snapshot, not just the output it references.

## Refactoring

Rename or move an address with a `moved` block, then confirm the plan shows a move without destroy or create. `terraform state mv` is the imperative alternative; coordinate it so nobody plans against the intermediate configuration.

Adopt existing infrastructure by declaring the resource and adding an `import` block, then review the plan before applying. The CLI `terraform import` command remains available but is imperative and easier to mismatch.

Split a state by backing up both sides, stopping concurrent runs, removing the object from the source with a `removed` block and `lifecycle { destroy = false }`, then importing it into the destination. Bind each remote object to exactly one Terraform address.

`state rm` forgets an object without destroying it. It is not cleanup; the resource remains and may later be recreated or orphaned.

## Drift

A normal plan refreshes state and proposes changes. Use `plan -refresh-only` to inspect what state would record after an out-of-band change, then decide whether to codify the new reality or restore the configured state. Do not accept refresh results blindly, and do not use `-refresh=false` to make a plan look clean.

`ignore_changes` suppresses update planning for selected attributes. It neither prevents drift nor repairs it.

## Recovery

Back up state before surgery. Stop writers, verify the lock owner, and compare the candidate state with live infrastructure before restoring.

`terraform force-unlock LOCK_ID` removes a lock; it does not change infrastructure. Use it only after confirming the previous run is dead. Never disable locking routinely.

Restoring state does not restore deleted infrastructure or data. Recover those from provider backups or snapshots, then reconcile state and configuration with a reviewed plan.

## Sources

- State: https://developer.hashicorp.com/terraform/language/state
- Backends: https://developer.hashicorp.com/terraform/language/backend
- S3 backend: https://developer.hashicorp.com/terraform/language/backend/s3
- Refactoring: https://developer.hashicorp.com/terraform/language/state/refactor
- State recovery: https://developer.hashicorp.com/terraform/cli/state/recover
