# Implementation Plan: API Gateway with Contract-Based Rate Limiting

## Overview
Prove you can protect core infrastructure while honoring enterprise service commitments: per-tenant throttling tied to actual contract terms, not a single global limit.

## Phase 1 — Happy Path
- `throttling/`: a FastAPI middleware enforcing a fixed requests-per-minute limit per `X-Tenant-Id` (token bucket or sliding window, in-memory to start).
- Ship: exceeding the limit returns `429` with a `Retry-After` header; staying under it passes through normally.

## Phase 2 — Hardening
- `throttling/`: move limits to a per-tenant config (a `Contract` model: tier → requests/min, burst allowance) instead of one global number; back the counter with Redis so it survives across multiple app instances.
- `sla_monitoring/`: track p50/p95/p99 latency and error rate per tenant; expose a `/metrics` endpoint (Prometheus format) for scraping.
- `alerts/`: emit a structured alert event when a tenant approaches its quota (e.g. 80% consumed) — not just when they're blocked.

## Phase 3 — Production-Grade
- `degradation/`: implement graceful degradation — when a tenant exceeds burst capacity, queue requests briefly (bounded queue with timeout) instead of hard-rejecting, so short spikes don't immediately fail.
- `alerts/`: automated overage alerts to both the tenant (webhook/email: "you're at 95% of your plan") and internal ops (approaching infra capacity limits across all tenants).
- `sla_monitoring/`: SLA breach detection — if p99 latency for a tenant's tier exceeds contract terms, raise an incident automatically.

## Testing & Deployment
- Load-test the throttling middleware directly (no network) by driving many requests through it in a test and asserting the 429 boundary is exact.
- Test degradation queue behavior under burst: assert requests are delayed, not dropped, up to the queue's bound.
