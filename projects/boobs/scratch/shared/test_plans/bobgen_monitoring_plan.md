# BobGen Monitoring Plan

This document outlines basic health checks, latency, error thresholds, and end-to-end validation for the BobGen status API scaffold.

- Health checks:
  - /health endpoint returns { ok: true, uptime, version }
  - Bootstrap health: if /health fails, alert and auto-restart
- Latency targets:
  - p95 latency target: <= 200ms
  - p99 latency target: <= 500ms
- Error thresholds:
  - Error rate: max 1% over a 5-minute window
  - Endpoint error rate across /bobgen/status and /bobgen/status/:id should remain below threshold
- Validation:
  - Validate health endpoint response schema
  - Validate status list structure and single-item responses
- Mock failures:
  - Simulate /health failing and observe alerting
  - Simulate /bobgen/status/:id not found (404) and verify response shape
