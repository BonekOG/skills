# Operations

Use this reference for day-2 changes, failed applies, drift, teardown, incidents, and cost.

## Operating discipline

Every managed root needs an owner, a documented backend, a known apply path, and a recovery plan. Production applies should come from a reviewed plan through the approved pipeline. Keep a record of who applied what and which commit produced it.

Change windows and extra approvals are organizational policy, not Terraform features. Apply them where the consequence justifies the delay.

## Failed apply

When apply fails:

1. Stop. Do not immediately rerun or chain a different change.
2. Read the error and identify the resource that failed.
3. Inspect the real object and current state; some earlier resources in the graph may already be changed.
4. Decide whether to forward-fix the configuration, import an object, or restore a missing dependency.
5. Re-plan and review before the next apply.

Terraform has no automatic rollback. A partial apply can leave infrastructure in a state that is neither the old nor the new configuration.

## Drift

Drift is a decision, not an error to suppress. Use a normal plan or `plan -refresh-only` to see what changed outside Terraform. Then choose:

- codify the new reality if it is correct;
- restore the configured state with a reviewed apply if it is not;
- import an object that was created manually and should now be managed;
- remove an object from management deliberately if it should stay outside Terraform.

Do not accept a refresh blindly, and do not add broad `ignore_changes` to silence the symptom.

## Locks and state incidents

Verify that no run is active before unlocking. Use the reported lock ID with `force-unlock`; never disable locking as a routine workaround.

For suspected corruption or accidental deletion, stop writers, preserve a copy, and compare state with live infrastructure. Restoring state repairs Terraform's record, not the resources. Recover data and objects from provider backups, then reconcile.

## Teardown

Before destroy, confirm the root, backend, workspace, account, region, and target. Read the destroy plan and check for resources that should be retained.

`prevent_destroy`, cloud deletion protection, backups, and retention policies are separate controls. Removing a lifecycle block also removes that protection. For shared platforms, require explicit approval and a documented decommissioning step.

## Inventory and cost

Compare cloud inventory and billing with Terraform state and ownership tags. Resources absent from state are unmanaged: either import them, document them as intentionally outside Terraform, or decommission them. Resources in state but absent from configuration are planned for destruction.

Use required owner, environment, and cost-center tags or labels, and enforce them with policy where possible. Infracost and HCP Terraform cost estimation help review deltas, but they estimate rather than bill.

## Incident checklist

- Which root, state, workspace, account, region, and commit are involved?
- Is a run still active, and who holds the lock?
- What did the last reviewed plan propose?
- Which resources were created, changed, or destroyed before the failure?
- Is the immediate priority restoring service, data, or Terraform's record?
- What is the forward fix, and who approves it?
- What evidence must be preserved for the post-incident review?

## Sources

- Apply command: https://developer.hashicorp.com/terraform/cli/commands/apply
- State recovery: https://developer.hashicorp.com/terraform/cli/state/recover
- Drift tutorial: https://developer.hashicorp.com/terraform/tutorials/state/resource-drift
- Infracost: https://www.infracost.io/docs/
