# Review checklist

Use this checklist for a Terraform pull request. Load the owning reference when an item needs detail.

## Scope and ownership

- [ ] The change stays within the root module, account, and environment it claims.
- [ ] The owning team and backend are identifiable.
- [ ] No unrelated resources are imported, adopted, renamed, or deleted.
- [ ] Repository layout, naming, module sources, and tagging conventions are preserved.

## Addresses and state

- [ ] Renames and moves use `moved` blocks; the plan shows a move, not replacement.
- [ ] Imports use `import` blocks or a documented CLI step with a reviewed plan.
- [ ] Removed resources are intentional; `removed` plus `destroy = false` is used where management should stop without deletion.
- [ ] No state, plan file, or `.terraform/` content is committed.
- [ ] Backend changes include a migration plan and a state backup.

## Plan

- [ ] The plan was generated from the reviewed commit with the intended variables and workspace.
- [ ] Add, change, destroy, and replace counts are explained.
- [ ] Every replacement has a reason and a data-lifecycle check.
- [ ] Destructive actions are explicitly approved.
- [ ] No unexplained drift is being reverted.
- [ ] Values known only after apply do not hide a risky change.

## Language and modules

- [ ] Variables have types, descriptions, and meaningful validation.
- [ ] Outputs are a small, documented contract.
- [ ] `for_each` is used where identity matters; `count` is limited to near-identical instances.
- [ ] `ignore_changes`, `depends_on`, and `dynamic` blocks are narrow and justified.
- [ ] Child modules declare providers but do not configure them.
- [ ] Module versions or Git refs are pinned.

## Security

- [ ] No credentials or secrets are in code, tfvars, backend config, or examples.
- [ ] Sensitive values are protected in state and plan artifacts.
- [ ] IAM, network, and public-access changes are reviewed for widening.
- [ ] CI uses short-lived credentials and separates plan from apply permissions.
- [ ] Teardown protection combines lifecycle rules with cloud controls where needed.

## Validation

- [ ] Format, validation, lint, scan, and applicable tests pass.
- [ ] New behavior has a plan test or an explained reason it cannot.
- [ ] Apply tests are isolated and clean up after failure.
- [ ] Policy exceptions are narrow, owned, and time-limited.

## Operations

- [ ] The apply path, approver, and rollback or forward-fix plan are clear.
- [ ] Stateful resources have backups and deletion protection.
- [ ] Monitoring or alerts cover new critical infrastructure.
- [ ] Cost impact is understood for material additions.
