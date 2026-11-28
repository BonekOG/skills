# Patterns and anti-patterns

Use this reference when a plan or configuration shows a recurring failure mode.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Reordering a list replaces or reassigns instances | `count` indexes | Use `for_each` with stable keys |
| A rename plans destroy and create | Missing `moved` block | Add `moved`, review the plan, keep it for consumers still on the old address |
| A plan is slow and mostly serialized | Broad `depends_on` or a mega-state | Remove inferred dependencies; split by lifecycle and ownership |
| Every environment shares one state | One root for everything | Separate roots or managed workspaces with separate backends |
| One configuration behaves like three products | `terraform.workspace` conditionals | Make environments explicit with separate roots |
| A child module assumes a region or account | Provider block inside the module | Configure providers at the root and pass aliases |
| A provider changed unexpectedly | Lock file missing or `init -upgrade` in CI | Commit the lock file; upgrade only in a reviewed change |
| Two engineers overwrite each other | Local or unlocked state | Shared backend with locking and versioning |
| A console change keeps reappearing | Drift | Decide to codify or revert; review with `-refresh-only` |
| A real update never appears in the plan | Broad `ignore_changes` | Narrow or remove the rule |
| Production changes bypass review | `-auto-approve` or local apply | Route through the approved saved plan |
| A targeted apply leaves a partial change | `-target` used as delivery | Reserve for recovery; follow with a full plan |
| A deleted resource reappears | `state rm` used as cleanup | Destroy it, or use a `removed` block to stop managing it |
| A consumer can read unrelated secrets | `terraform_remote_state` used as a broad interface | Publish only the needed values |
| A secret appears despite `sensitive` | State and plans store values | Restrict and encrypt artifacts; use ephemeral values where supported |
| CI can delete production | One administrator identity for all jobs | Split plan and apply identities; scope permissions |
| A module wraps one resource and forwards every argument | Over-abstraction | Remove the module or give it a real contract |
| State is unlocked while a run is active | `force-unlock` without verification | Confirm staleness and lock owner first |
| Apply executes something different from the reviewed plan | Stale plan or changed state | Re-plan and re-review |
| Test resources remain after a failure | No cleanup path | Isolate accounts, use deferred destroy, add a cleanup job |

When a symptom has more than one plausible cause, inspect the plan and state before changing configuration. A fix that only silences the diff usually moves the failure to the next apply.

## Sources

- Lifecycle: https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle
- Refactoring: https://developer.hashicorp.com/terraform/language/state/refactor
- State locking: https://developer.hashicorp.com/terraform/language/state/locking
