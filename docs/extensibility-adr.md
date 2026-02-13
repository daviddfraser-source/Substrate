# ADR: Extensibility Strategy (Plugin Runtime Deferred)

## Status

Accepted

## Context

There is demand for custom transition hooks and extension points. Introducing a dynamic plugin runtime immediately would increase governance and security surface area before stability hardening is complete.

## Decision

Adopt a staged extensibility model:

1. Documented extension points first (interfaces/contracts)
2. Static, reviewed integration patterns second
3. Dynamic plugin runtime deferred until post-stability criteria are met

## Rationale

- preserves deterministic governance guarantees
- avoids unbounded execution behavior in core transition path
- reduces security and operational risk for early adopters

## Deferred Scope

- runtime-loaded third-party plugins
- arbitrary transition mutation hooks
- remote extension registries

## Readiness Criteria For Future Plugin Runtime

- stable error code taxonomy and migration strategy
- transition contract coverage on core engine
- permission/sandbox policy baseline for extension execution
- explicit supervisor policy compatibility tests

## Consequences

- near-term extensibility is explicit and code-reviewed
- lower short-term flexibility, higher platform reliability
