---
name: terraform
description: Use when designing, implementing, reviewing, or operating Terraform infrastructure as code, including module and state architecture, plans and applies, provider upgrades, testing, security, and CI delivery.
compatibility: "Requires terraform."
disable-model-invocation: false
---

# Terraform Engineering

## Purpose

Make Terraform changes correct for the actual repository, cloud account, and environment: predictable plans, explicit state ownership, reviewable applies, and recoverable operations. Treat infrastructure changes as production changes even when the configuration is small.

The user's request takes precedence over this skill's recommendations. Treat the guidance as decision support unless a rule protects credentials, live infrastructure, or an explicit authorization boundary.

## Select the operating mode

Use only the modes required by the request:

1. **Configuration development** — write or review HCL, modules, variables, outputs, providers, backends, and tests.
2. **Plan review** — inspect a plan, saved plan, or plan JSON without changing infrastructure.
3. **Live apply** — initialize, plan, apply, import, change state, or destroy after exact authorization.
4. **Diagnosis and recovery** — investigate drift, a failed apply, a lock, or a state incident, starting read-only.

Editing configuration does not authorize applying it. Producing a plan does not authorize applying that plan.

## Discover context proportionally

Inspect repository instructions, existing configurations, CI, and recent history before introducing a pattern. Capture only context that can change the result:

- Terraform or OpenTofu CLI version and the repository's `required_version` policy;
- root module, backend, state location, locking, and selected workspace;
- cloud account, subscription, or project; region; environment; ownership and criticality;
- provider versions, committed lock file, module sources, and registry or mirror restrictions;
- pipeline, approval model, credentials, and whether applies run locally or remotely;
- stateful resources, deletion protection, backups, and data-retention obligations;
- existing layout, naming, tagging, module, and review conventions.

For offline configuration work, continue with explicit assumptions. Before live commands, resolve the working directory, CLI version, backend, workspace, identity, account, and region. Use read-only checks such as `terraform version`, `terraform workspace show`, `terraform state list`, and the cloud CLI's identity command. Do not print tokens, keys, or full credential context.

## Load focused guidance

Read only the references relevant to the selected mode and observed risks:

- Terraform's operating model, fit, risk tiers, and change boundary: [operating-model.md](references/operating-model.md).
- HCL structure, style, variables, expressions, meta-arguments, and lifecycle: [language-and-style.md](references/language-and-style.md).
- Root modules, stack and state boundaries, environments, and repository layout: [architecture.md](references/architecture.md).
- Reusable module interfaces, sources, versioning, and provider passing: [modules.md](references/modules.md).
- Backend choice, locking, state layout, refactoring, drift, and recovery: [state-and-backends.md](references/state-and-backends.md).
- Version constraints, lock file, provider upgrades, and OpenTofu: [providers-and-versions.md](references/providers-and-versions.md).
- Secrets, credentials, least privilege, supply chain, and policy: [security.md](references/security.md).
- Native tests, mocking, integration tests, and test scope: [testing.md](references/testing.md).
- Formatting, validation, linting, scanning, policy, and plan gates: [quality-gates.md](references/quality-gates.md).
- CI/CD, apply approvals, saved plans, and drift schedules: [delivery-tooling.md](references/delivery-tooling.md).
- Day-2 operations, failed applies, teardown, incidents, and cost: [operations.md](references/operations.md).
- Recurring failure modes and their fixes: [patterns-and-anti-patterns.md](references/patterns-and-anti-patterns.md).
- Pull-request review: [review-checklist.md](references/review-checklist.md).
- AWS, Azure, and GCP backend, authentication, and tagging differences: [cloud-providers.md](references/cloud-providers.md).

Do not load a cloud-provider section unless the task targets that provider.

## Operating invariants

1. Start live work with the narrowest useful read-only inspection.
2. Do not run a state-changing command without explicit authorization for the exact action and target. This includes `apply`, `destroy`, `import`, `state mv`, `state rm`, `state push`, `force-unlock`, backend migration, and any refresh or provider upgrade that can rewrite state or the lock file.
3. Treat production, shared state, identity and access, networking, data stores, and deletion-protected resources as high risk regardless of naming.
4. Never commit state, saved plans, plan JSON, `.terraform/` contents, credentials, or variable files containing secrets.
5. `sensitive = true` redacts routine output; it does not remove values from state, saved plans, or JSON output. Protect those artifacts as secrets.
6. Do not unlock state while a run may still be active, and do not use `-lock=false` as a routine workaround.
7. Do not use `-auto-approve` for unreviewed production changes, `-target` as routine delivery, or `-refresh=false` to hide drift.
8. Preserve repository conventions for layout, naming, module sources, tagging, and review. Do not add a parallel pattern for convenience.
9. Distinguish provider requirements, organizational policy, and optional hardening. Do not turn preferences into universal requirements.
10. Understand blast radius before a mutation: expected additions, changes, replacements, and destroys; success signal; failure signal; and recovery path. Terraform has no automatic rollback.
11. Do not adopt, modify, or delete resources outside the stated scope. Import only objects the user intends Terraform to manage.
12. If an apply would execute something different from the plan that was reviewed, stop and re-review.

## Work method

1. Identify the root module, backend and state, workspace, account, region, and owning team.
2. Read the smallest evidence set: `required_version`, backend configuration, variables, module calls, provider constraints, CI workflow, and recent changes.
3. Select applicable domains: language, architecture, state, providers, security, testing, delivery, or operations.
4. Make the smallest coherent change. Keep contracts aligned: variable and output types, resource addresses, provider aliases, backend keys, tags, and cross-stack outputs.
5. Validate at the closest reliable boundary: `terraform fmt -check`, `validate`, native tests, a plan with real variables, policy checks, and scans.
6. Report plan counts and every destructive or replacement action before applying. Apply only when authorized, preferably the exact saved plan, then observe the result and stop on unexpected behavior.

## Output

Report the result in the shape most useful to the request. Include:

- target, root module, workspace, account, and material assumptions;
- evidence or changed artifacts;
- plan summary with add, change, destroy, and replace counts plus risky resources;
- validation performed, tool versions, and remaining gaps;
- live impact, failure handling, and recovery notes when applicable.

Separate direct evidence from inference. If missing information prevents a safe live operation, stop before the mutation and ask for that exact information.
