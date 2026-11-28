# Testing

Use this reference to choose tests for Terraform modules and configurations.

## Layers

1. `terraform fmt -check` and `terraform validate` catch formatting and internal configuration errors. Validation does not call provider APIs or prove that an apply will succeed.
2. Plan-based native tests exercise expressions, conditionals, validation rules, and resource counts without creating infrastructure.
3. Apply-based native tests exercise real provider behavior and resource relationships in a disposable account.
4. External integration tests cover multi-step deployment, runtime behavior, and cleanup that native tests cannot express.

Use the cheapest layer that can catch the risk. Most module logic belongs in plan tests; reserve apply tests for behavior that mocks cannot establish.

## Native tests

`terraform test` runs `.tftest.hcl` files. A run can use `command = plan` or `command = apply`; the default is apply. Assertions read resource attributes or outputs.

    run "creates_one_bucket_per_environment" {
      command = plan

      variables {
        environments = ["dev", "prod"]
      }

      assert {
        condition     = length(aws_s3_bucket.this) == 2
        error_message = "Expected one bucket per environment."
      }
    }

Terraform 1.7 and later support `mock_provider`, `override_resource`, and `override_data`. Mocks let plan tests run without real credentials, but they also mean the provider's actual API behavior is not tested.

Use variables per run to cover branches. Keep assertions about observable contracts, such as names, counts, references, and validation outcomes, rather than incidental defaults.

## Apply and integration tests

Apply tests create real resources. Run them in an isolated account or project with a budget, least-privilege credentials, unique naming, and reliable cleanup. A failed test must not leave expensive or security-sensitive infrastructure behind.

Terratest (Go) fits multi-step scenarios that deploy infrastructure and then test it through APIs, HTTP, or cloud SDKs. Use deferred destroy and a separate cleanup path for interrupted runs.

`terraform-compliance` expresses BDD-style policy assertions against plans. It complements plan policy; it does not test deployed behavior.

## What to test

- variable validation and rejected inputs;
- conditional resource creation and counts;
- names, tags, and references that form contracts;
- module outputs consumed by other stacks;
- `moved` and import behavior when addresses change;
- risky policy outcomes such as public access or missing encryption.

Do not test Terraform's formatting, provider internals, or incidental defaults that the provider may change. Do not assert a full resource graph when a narrow contract is enough.

## Cost and isolation

Plan tests are cheap and suitable for every pull request. Apply tests cost money and time; run them on a schedule, before release, or for changes that touch the relevant behavior. Never run apply tests against production.

## Pitfalls

- Validation passes and is treated as proof the configuration deploys.
- Mocks pass while the real provider rejects the configuration.
- Tests share an account and collide on fixed names.
- A failed test skips cleanup and leaves billable resources.
- Assertions encode implementation details that change on every refactor.

## Sources

- Test language: https://developer.hashicorp.com/terraform/language/tests
- Mocking: https://developer.hashicorp.com/terraform/language/tests/mocking
- Validate: https://developer.hashicorp.com/terraform/cli/commands/validate
- Terratest: https://terratest.gruntwork.io/docs/getting-started/quick-start/
