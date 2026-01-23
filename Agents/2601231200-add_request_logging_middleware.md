# 2601231200 - Add lightweight request-logging middleware

Date: 2026-01-23 12:00 (UTC assumed for filename consistency)

## Intent
Add a lightweight, least-invasive request hit recorder so that during functional testing we can see which endpoints are actually being exercised. The recorder should not change runtime behavior and should survive restarts (append-only).

## Changes made
- Edited `app/app.py` to append a single-line record to `instance/logs/requests.log` for every non-static request completed.
  - Recorded fields: timestamp (UTC ISO), short request id, HTTP method, request path, endpoint name (if resolved), and response status code.
  - Wrapped in try/except to avoid affecting normal responses on write errors.
  - Ensured the `instance/logs` directory is created if missing.

## Rationale
- Minimal change: uses existing `after_request` hook already present in `create_app()` to avoid adding new middleware plumbing.
- Durable: writes to a simple append-only file under `instance/logs/requests.log` which can be tailed or parsed during testing.
- Safe: exceptions while writing are logged to `app.logger` but do not interrupt request handling.

## How to use during testing
- Start the dev server (e.g., `python run.py`) and exercise routes. Then inspect or tail:

  instance/logs/requests.log

- Example line format:

  2026-01-23T12:34:56.789012 1a2b3c4d GET /dataset/1/files/list datasets.view_dataset 200

## Summary
- File modified: `app/app.py` — added append-to-file logging in `after_request`.
- New/updated files logged here: this file.

Summary of what was done: added a lightweight request hit recorder that appends a timestamped single-line entry per completed request to `instance/logs/requests.log`. This is intended to support test-time verification of which endpoints are hit.
