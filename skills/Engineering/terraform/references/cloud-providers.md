# Cloud providers

Use this reference for provider-specific backend, authentication, and tagging details. Load only the section for the target cloud.

## AWS

Use an S3 backend with bucket versioning, server-side encryption, and `use_lockfile = true`. DynamoDB-based locking is deprecated and slated for removal; do not introduce it for a new configuration. Scope IAM to the state object and lock object paths.

For CI, use GitHub or another OIDC issuer with `assume_role_with_web_identity`. Restrict the role trust policy to the repository, branch, and environment. For cross-account work, assume a target-account role from the pipeline role rather than storing long-lived keys.

Use provider `default_tags` for common allocation tags, and verify that resources with special tagging behavior are handled explicitly. Provider aliases are the normal way to target several regions or accounts.

Watch for resources that cannot be destroyed while non-empty, replacement of identifiers such as names, and services that create hidden dependencies outside Terraform.

## Azure

The `azurerm` backend stores state in Blob Storage and uses blob leasing for locking. Enable blob versioning or soft delete, restrict data-plane access, and use a dedicated storage account for state.

Prefer Entra ID with OIDC or workload identity federation. Use a managed identity on Azure-hosted runners and Azure CLI authentication for local work. Scope the service principal or managed identity to the target subscription and resource groups.

The Azure provider does not have a universal `default_tags` equivalent. Apply shared tags with locals and `merge`, and use Azure Policy to require or inherit tags. Tag support varies by resource type, so verify the planned result.

Be careful with resource providers that are registered per subscription, role assignments that require directory permissions, and resources with soft-delete or purge protection.

## Google Cloud

Use a GCS backend with Object Versioning and, where required, CMEK. The backend supports locking; protect the bucket with IAM and retention controls.

Use application default credentials locally and Workload Identity Federation in CI, optionally impersonating a narrowly scoped service account. Avoid downloaded service-account keys.

The Google provider supports `default_labels`. Confirm label support per resource and use organization policy or a custom gate for mandatory labels.

Watch for project-level API enablement, IAM bindings that replace rather than add, and resources tied to a project or region that cannot be moved without replacement.

## Cross-provider rules

- Configure providers only in root modules and pass aliases explicitly.
- Keep one state per account, region, and lifecycle boundary where isolation matters.
- Use short-lived credentials and separate plan and apply identities.
- Verify provider version constraints and commit the lock file with checksums for every runner platform.
- Review provider upgrades as infrastructure changes, not routine dependency bumps.

## Sources

- S3 backend: https://developer.hashicorp.com/terraform/language/backend/s3
- AzureRM backend: https://developer.hashicorp.com/terraform/language/backend/azurerm
- GCS backend: https://developer.hashicorp.com/terraform/language/backend/gcs
- AWS provider: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Google provider: https://registry.terraform.io/providers/hashicorp/google/latest/docs
