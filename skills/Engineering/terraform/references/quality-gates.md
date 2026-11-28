# Quality gates

Use this reference to build and interpret the checks that run before a Terraform change is merged or applied.

## Gate sequence

| Order | Gate | Command | Proves | Does not prove |
| --- | --- | --- | --- | --- |
| 1 | Format | `terraform fmt -check -recursive` | Canonical layout | Semantic correctness |
| 2 | Init | `terraform init -backend=false` | Providers and modules resolve | Backend or credentials work |
| 3 | Validate | `terraform validate` | Syntax and internal consistency | Provider API acceptance or deployability |
| 4 | Lint | `tflint` with pinned rules | Language and provider-specific issues | Runtime behavior |
| 5 | Scan | Checkov, Trivy config, or KICS | Risky source patterns | All plan-time values |
| 6 | Test | `terraform test` with plan runs and mocks | Module logic and assertions | Real provider behavior |
| 7 | Plan | `terraform plan -detailed-exitcode` | Proposed changes against current state | That apply will succeed |
| 8 | Policy | OPA, Conftest, Sentinel, or equivalent on plan JSON | Planned values satisfy rules | That the rules are complete |

Treat steps 1 to 6 as pull-request gates. A plan should run with the intended variables, workspace, and least-privilege credentials. Apply remains a separate, approved action.

## Exit codes

`terraform plan -detailed-exitcode` returns 0 when there are no changes, 1 on error, and 2 when changes are present. Exit 2 is a successful plan that needs review, not a failed job. A pipeline that treats 2 as failure either never applies changes or teaches people to ignore the gate.

## Static analysis

| Tool | Catches | Limits |
| --- | --- | --- |
| TFLint | Deprecated syntax, unused declarations, provider rules and plugins | Rule coverage depends on configuration; deep checks may need credentials |
| Checkov | IaC security and compliance, graph checks, source and plan JSON | Broad skips or soft-fail can hide findings |
| Trivy config | Terraform misconfigurations and custom Rego checks | Source conversion omits some attributes and treats absent settings as defaults |
| KICS | Security and best-practice queries for source and plan JSON | Query coverage varies |
| Semgrep | Custom HCL patterns and organization conventions | Depends entirely on the ruleset |
| OPA or Conftest | Organization policy over parsed configuration or plan JSON | You own policy design, tests, and exceptions |

tfsec still exists, but its maintainers direct new work toward Trivy. Prefer Trivy for a new standard.

## Plan policy

Convert a saved plan with `terraform show -json`, then evaluate only the fields the policy needs. Plan JSON can contain sensitive values; treat it as a secret artifact and delete it when no longer needed.

Useful policy targets include public ingress, unencrypted storage, wildcard IAM, missing tags, forbidden regions, and resources scheduled for destruction. Keep policies small enough to test and explain.

## Suppressions

A suppression needs a reason, an owner, and an expiry or review date. Scope it to the narrowest resource or rule. Do not enable global soft-fail to make a noisy gate pass.

Pinned tool and ruleset versions make results reproducible. An unpinned scanner can turn a routine merge into a policy migration.

## Plan review

Inspect:

- additions, changes, replacements, and destroys, including reasons for replacement;
- identity, network, DNS, data-store, and deletion-protection changes;
- IAM or role widening and new public endpoints;
- address moves and whether the old and new objects are the same real resource;
- values shown as known after apply, which can hide risky changes;
- drift that the plan would revert.

Summarize these in the pull request. Do not paste a full plan or JSON.

## What a clean run means

A clean run means the enabled checks passed for the inputs they examined. It does not prove that the cloud quota allows the change, that the provider API accepts every value, that the apply will finish, or that the result is secure. State those limits when reporting.

## Sources

- Plan: https://developer.hashicorp.com/terraform/cli/commands/plan
- Validate: https://developer.hashicorp.com/terraform/cli/commands/validate
- JSON format: https://developer.hashicorp.com/terraform/internals/json-format
- TFLint: https://github.com/terraform-linters/tflint
- Trivy Terraform scanning: https://trivy.dev/docs/latest/tutorials/misconfiguration/terraform/
- Checkov: https://www.checkov.io/
