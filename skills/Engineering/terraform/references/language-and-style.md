# Language and style

Use this reference when writing or reviewing HCL, variables, expressions, and resource behavior.

## Files and modules

A directory is a module. Terraform loads every top-level `.tf` and `.tf.json` file in it as one configuration; nested directories are separate modules. Common organization is `main.tf`, `variables.tf`, `outputs.tf`, `locals.tf`, and `terraform.tf` or `versions.tf`. These names are conventions, not requirements.

Put `required_version` and `required_providers` in one obvious file. Split large configurations by resource area when that improves navigation. Avoid splitting a single cohesive resource graph across many files for symmetry alone.

## Style

- Use snake_case for names, lowercase resource labels, and descriptive nouns.
- Use two-space indentation and run `terraform fmt`; do not hand-format around it.
- Avoid repeating the resource type in its label, for example prefer `aws_instance.web` over `aws_instance.web_instance`.
- Keep one blank line between blocks and group related arguments.
- Prefer plain references and expressions over string interpolation that adds nothing.
- Write comments for non-obvious constraints and provider quirks, not for restating the code.

## Variables and outputs

Every root input needs a `type` and `description`. Add `validation` for real constraints such as allowed environments, CIDR shape, or required naming patterns. Use `nullable = false` when `null` must not silently override a default.

Use object types for coherent groups of settings and `optional(TYPE, DEFAULT)` for stable fallbacks. Keep the input surface to decisions the caller genuinely owns; pass identifiers rather than provider-specific resource objects.

Mark secrets with `sensitive = true` so routine CLI output is redacted, and remember the value is still in state and saved plans. Terraform 1.10 and later also support ephemeral variables and resources for values that must not be persisted; use them only where the provider and expression rules allow it.

Outputs are part of the module contract. Add descriptions, export only values callers need, and mark sensitive outputs. Avoid exporting every attribute of every resource.

## Locals and expressions

Use locals to name a repeated expression or encode a decision once. Do not build a second configuration language out of deeply nested conditionals and `merge` calls. Keep shared locals in `locals.tf` and file-specific locals near their use.

Prefer direct expressions, `for` expressions, conditionals, and collection functions. Use quoted templates mainly for interpolation; use heredocs for multiline content and `jsonencode` or `yamlencode` when emitting structured documents.

## Instance identity

`count` addresses instances by index. It fits near-identical instances and optional singletons. `for_each` addresses instances by key and fits objects with meaningful, stable identity. Removing an item from a `count` list can shift every later index and cause replacements; removing a key from `for_each` removes only that instance.

Keys for `for_each` must be known before provider operations. Do not derive them from attributes that are unknown until apply.

Use `depends_on` only for a dependency Terraform cannot infer from references. Broad `depends_on` creates serialization and can make plan values unknown longer than necessary.

## Lifecycle and meta-arguments

- `create_before_destroy` helps when replacement can overlap, but fails when old and new cannot coexist, such as fixed names or unique endpoints.
- `prevent_destroy` blocks a planned destroy only while the rule remains configured. Removing the block removes the guard.
- `ignore_changes` suppresses diffs for selected attributes. Keep it narrow; broad use hides drift and can mask real configuration errors.
- `replace_triggered_by` ties replacement to a planned change in another managed object. Verify that replacement is actually intended.
- `provider = aws.alias` selects a configured alias. Child modules should receive aliases explicitly rather than guessing from the root.
- Lifecycle arguments must be literal values, not computed expressions.

Use `dynamic` blocks only when the number of nested blocks genuinely varies. Literal blocks are easier to read and review. Dynamic blocks cannot generate meta-arguments such as `lifecycle`.

## Version-dependent features

Verify the installed CLI before relying on newer syntax. Documented introduction points include:

| Feature | Version |
| --- | --- |
| `moved` blocks | 1.1 |
| `import` and `check` blocks | 1.5 |
| `terraform test` generally available | 1.6 |
| Test mocking and `removed` blocks | 1.7 |
| Ephemeral variables, outputs, and resources | 1.10 |
| `import` blocks inside modules | 1.16 |
| Variables and locals in provider requirements, `-minimal-refresh` | 1.17 |

Pin `required_version` to a range the project actually tests. Do not assume the newest release is available in CI or on every workstation.

## Review prompts

- Would a list reorder cause replacements?
- Is a rename missing a `moved` block?
- Does `ignore_changes` hide a real update?
- Is a secret stored in a variable default or tfvars file?
- Does a provider alias reach the child modules that need it?
