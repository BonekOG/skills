# Security

Use this reference for secrets, credentials, least privilege, supply chain, policy, and teardown protection.

## Threat model

Terraform concentrates power: it holds cloud credentials, writes state that can contain secrets, and can create or delete critical infrastructure. The main risks are credential theft, over-privileged runners, leaked state or plans, malicious or compromised providers and modules, unreviewed public exposure, and destructive changes.

## Secrets

Do not put secrets in `.tf` files, committed `.tfvars`, backend configuration, or module defaults. Environment variables and secret-manager data sources keep secrets out of the repository, but values read into resources can still land in state.

`sensitive = true` redacts routine CLI output. It does not remove the value from state, saved plans, `terraform output -json`, or `-raw` output. Terraform 1.10 and later support ephemeral values and write-only provider arguments for cases that must not be persisted; use them where the provider supports the flow, and still protect state and plan artifacts.

Treat a leaked state file as a credential leak. Rotate affected secrets, restrict access, and remove unnecessary copies.

## Credentials

Prefer short-lived, scoped credentials:

- local work: cloud CLI SSO, application default credentials, or an assumed role;
- CI: OIDC or workload identity federation restricted to the repository, branch or environment, and workflow;
- apply: a separate identity with write permissions, used only after review;
- emergency access: a named, audited, time-limited elevated role with MFA or just-in-time approval.

Avoid long-lived access keys and shared administrator identities. Give plan jobs read-oriented permissions where the provider allows it, and remember that backend access is separate from provider access: reading state and taking a lock may require permissions even for a plan.

## State access

Encrypt state at rest, enable versioning or snapshots, and restrict bucket or container access to the identities that run Terraform. Separate read access from write access where possible. Audit access to state and saved plans.

Saved plans can contain sensitive values in cleartext. Restrict artifact access and retention, and never attach a raw plan or plan JSON to a public pull request.

## Supply chain

- Commit the provider lock file and generate checksums for every runner platform.
- Use official or approved provider sources and verify the source address.
- Pin reusable modules to exact versions or immutable Git commits.
- Use an approved registry mirror where the organization requires it.
- Review provider and module upgrades as dependency changes, not routine noise.

## Policy and guardrails

Static scanners catch risky source patterns early. Policy against `terraform show -json` can evaluate planned values and changes. Use both where the risk justifies it, and keep the plan JSON private.

Policy is not a substitute for review. A rule can allow a dangerous change that matches its pattern, and a suppression can silently disable protection. Version rules, require narrow exceptions with an owner and expiry, and test policies against representative plans.

## Teardown protection

`prevent_destroy` blocks a planned destroy only while the resource block and the rule remain configured. Combine it with cloud-native deletion protection, backups, retention policies, and explicit teardown approval for stateful resources.

Do not rely on a single control. A lifecycle rule can be removed in the same change that destroys the resource.

## Pitfalls

- A secret is marked sensitive and assumed safe, but appears in state or a saved plan.
- CI uses one long-lived administrator identity for plan and apply.
- A plan job can write to production because permissions were copied from the apply job.
- A module is pinned to a branch name rather than a commit.
- A scanner exception is global and permanent.
- A database is "protected" only by `prevent_destroy`.

## Sources

- Sensitive data: https://developer.hashicorp.com/terraform/language/manage-sensitive-data
- State purpose: https://developer.hashicorp.com/terraform/language/state/purpose
- Lifecycle: https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle
- GitHub OIDC: https://docs.github.com/en/actions/reference/security/oidc
