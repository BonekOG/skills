# Delivery tooling

Use this reference to place Terraform in CI/CD and choose an execution platform.

## Pipeline shape

A reviewable pipeline separates proposal from mutation:

1. On pull request, run format, validation, lint, scans, and tests for the changed roots.
2. Run a plan with the target workspace, variables, and read-oriented credentials.
3. Publish a short summary: add, change, destroy, replace, policy results, and estimated cost.
4. Require review and environment approval for production.
5. After merge, apply the reviewed plan, or regenerate and review a new plan if state or code changed.
6. Run scheduled drift checks and report differences without applying automatically.

Run one pipeline per root module. A monorepo needs reliable change detection, but path filters can miss shared modules; include module changes in the affected set.

## Saved plans

Save the plan with `-out` and apply that file, so the approved actions match what executes. A saved plan is bound to the state and configuration it was created from and becomes stale after either changes.

Treat the plan file as sensitive: it can contain cleartext values. Restrict artifact access and retention, encrypt at rest, and never attach it to a public comment. If the plan cannot be trusted or is stale, regenerate and review it instead of forcing an apply.

## Credentials and approvals

Use OIDC or workload identity federation with a trust policy restricted to the repository, branch, and environment. Give plan jobs read-oriented provider permissions and apply jobs write permissions only in the protected environment.

Use environment protection, required reviewers, and a concurrency group per state. Do not cancel an apply that is already running; let it finish or fail, then inspect state and infrastructure before retrying.

## Concurrency

Backend locking protects state from simultaneous writes, but it does not coordinate two pipelines that plan different commits. Use one queue per root and environment, and avoid a manual apply racing an automated one.

Do not run Terraform from a developer laptop against production state that a pipeline also manages. If local access is necessary for an incident, pause the pipeline and record the intervention.

## Platforms

| Platform | Fits | Considerations |
| --- | --- | --- |
| GitHub Actions or another CI runner | Teams already using the CI for delivery | You own state access, approvals, artifact handling, and drift jobs |
| HCP Terraform or Terraform Enterprise | Centralized runs, state, variables, policy, and approvals | Platform coupling and cost; remote runs need network access to providers and cloud APIs |
| Atlantis | Pull-request-driven plan and apply with repository conventions | Requires a service, credentials, and clear ownership of the apply command |
| Spacelift, env0, and similar | Managed orchestration with policy and stack controls | Vendor-specific configuration and migration work |

Choose based on where approvals, credentials, and audit evidence already live. Do not run two platforms that can apply the same state.

## GitOps

A GitOps controller can reconcile Terraform, but the controller becomes the only writer. Do not let a pipeline and a controller both apply the same root. Treat a manual apply as an incident that the controller may revert.

## Drift checks

Schedule a refreshed plan per production root and report differences. Do not auto-apply drift remediation without review; the drifted value may be an intentional emergency fix or a provider-side change that needs codifying.

## Pitfalls

- The pipeline applies a freshly generated plan that nobody reviewed.
- The saved plan is reused after the branch moved.
- Plan and apply share an administrator identity.
- Two workflows can apply the same state concurrently.
- A cancelled apply leaves the next run guessing about partial changes.
- Path filters skip a shared module and miss affected roots.
- Drift is detected but nobody owns the decision.

## Sources

- Automating Terraform: https://developer.hashicorp.com/terraform/tutorials/automation/automate-terraform
- Plan command: https://developer.hashicorp.com/terraform/cli/commands/plan
- GitHub environments: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- HCP Terraform runs: https://developer.hashicorp.com/terraform/cloud-docs/workspaces/run
