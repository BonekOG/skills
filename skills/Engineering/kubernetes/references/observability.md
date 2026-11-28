# Observability

Use this reference when application or platform work involves metrics, logs, traces, alerts, or incident evidence.

## Design for diagnosis

Expose signals that distinguish demand, success, dependency failure, saturation, and rollout regressions. Prefer application and user-impact signals over pod-count-only health.

## Logs

Write structured, bounded logs to standard output or standard error unless the platform defines another contract. Include stable correlation fields but exclude credentials, tokens, request bodies, and sensitive personal data. Handle multiline stack traces according to the collector's parsing rules.

## Metrics

Use stable metric names, units, and label cardinality. Never put user IDs, request IDs, pod UIDs, unbounded paths, or arbitrary error text in labels. Distinguish counters, gauges, and histograms correctly. Verify that ServiceMonitor or PodMonitor selectors, namespaces, and named ports match the installed Prometheus operator configuration.

## Traces

Propagate context across supported protocols, sample intentionally, and avoid attaching secrets or high-cardinality payloads. Flush exporters during graceful shutdown within a bounded time.

## Alerts

Tie alerts to actionable impact or exhaustion with an owner and runbook. Avoid alerting on every restart or transient scheduling event without duration, severity, and user impact. Validate queries against the actual telemetry backend and retention window.

## Operational checks

When evaluating a rollout, compare before and after over an appropriate interval. Account for scrape delay, log ingestion delay, sampling, and missing-data semantics before declaring success.

## Sources

- Kubernetes observability: https://kubernetes.io/docs/concepts/cluster-administration/observability/
- Logging architecture: https://kubernetes.io/docs/concepts/cluster-administration/logging/
- Metrics instrumentation: https://prometheus.io/docs/practices/instrumentation/
