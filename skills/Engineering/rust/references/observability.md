# Observability

## Logs vs tracing vs metrics

- Logs: discrete diagnostic events.
- Tracing/spans: causal/request/task context across operations.
- Metrics: aggregated system behavior and SLO signals.

Choose based on operational question, not library fashion.

## Structured events

Prefer structured fields over formatted blobs for machine-queryable data.
Do not log secrets or sensitive payloads by default.

## Levels

Use levels consistently:

- error: operation/system failure needing attention;
- warn: abnormal/degraded but handled;
- info: meaningful lifecycle/business milestones;
- debug/trace: diagnostic detail.

Avoid logging the same error at every layer. Either add context and propagate or log at the boundary that owns handling.

## Async/requests

Attach stable context:

- request/job ID;
- operation name;
- peer/resource identifiers where safe;
- retry attempt/deadline where useful.

## Metrics

Measure domain/system outcomes:

- request count/error rate;
- queue depth;
- latency distribution;
- retry count;
- saturation/resource use.

Avoid high-cardinality labels from user-controlled identifiers.

## Instrumentation overhead

Do not allocate expensive log fields unless the event is enabled when the logging framework makes that relevant.
Profile highly instrumented hot paths.
