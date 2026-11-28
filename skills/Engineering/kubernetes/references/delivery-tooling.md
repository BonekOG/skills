# Helm, Kustomize, GitOps, and delivery CI

Use this reference when Kubernetes desired state is rendered, packaged, reconciled, or validated by delivery tooling.

## Find the owner

Determine whether raw manifests, a Helm chart, a Kustomize overlay, an operator custom resource, or a GitOps object owns the final resource. Change that source and preserve its composition model. Do not add a parallel delivery mechanism for convenience.

## Helm

- inspect chart and dependency versions, value schema, release namespace, capabilities, and lookup usage;
- render with the exact values and relevant API capabilities;
- distinguish omitted, null, false, zero, and empty values in templates;
- avoid placing credentials in committed values or command history;
- review hooks, CRDs, ownership annotations, immutable fields, and deletion behavior;
- use `helm lint`, repository tests, rendering, and an available diff mechanism before upgrade.

## Kustomize

- build the exact overlay, including generators and replacements;
- keep bases environment-neutral unless the repository intentionally does otherwise;
- prefer targeted patches over copies of whole resources;
- understand name transformations before writing cross-resource references;
- inspect generated object names and hash behavior for ConfigMaps and Secrets;
- validate the rendered result, not only individual inputs.

## GitOps

Inspect reconciliation ownership, source revision, target cluster, prune behavior, health rules, sync order, drift ignores, suspension, and controller permissions. A manual `kubectl` change can be immediately reverted and can conceal the real fix.

Do not trigger sync, reconcile, suspend, resume, or prune without treating it as a live mutation. Prefer a reviewed repository change and observe the controller's resulting conditions.

## CI validation

A useful pipeline renders every supported environment, validates schemas and CRDs against supported versions, runs policy checks, and detects cross-resource mismatches. Avoid tests that merely assert particular YAML formatting.

## Sources

- Helm documentation: https://helm.sh/docs/
- Kustomize: https://kubectl.docs.kubernetes.io/references/kustomize/
- Declarative management: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/
