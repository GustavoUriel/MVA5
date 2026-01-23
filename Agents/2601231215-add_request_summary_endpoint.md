# 2601231215 - Add requests summary endpoint

Date: 2026-01-23 12:15 (UTC assumed for filename consistency)

## Intent
Provide a lightweight inspection endpoint to summarize which requests have been recorded by the previously-added `requests.log` recorder. This helps during testing to determine which endpoints were actually hit without needing to tail files manually.

## Changes made
- Edited `app/app.py` to add an endpoint at `GET /__requests/summary`.
  - Behavior: reads `instance/logs/requests.log`, aggregates counts by endpoint and by path, and returns the last 50 log lines.
  - Access control: endpoint returns 403 unless `app.debug` is True or the request comes from `127.0.0.1`/`::1`.
  - Error handling: returns 404 when the log file is missing and 500 on read errors; exceptions are logged to the app logger.

## How to use
1. Start the app in development mode (recommended):

```powershell
python run.py
```

2. Exercise the application routes (browse or run automated tests).

3. Fetch the summary (from the same machine):

```powershell
curl http://127.0.0.1:5005/__requests/summary
```

Response JSON format:
- `total`: integer total recorded lines
- `by_endpoint`: mapping endpoint -> count (empty string key for unknown)
- `by_path`: mapping path -> count
- `sample_lines`: array of last 50 raw log lines

## Summary
- File modified: `app/app.py` — added `GET /__requests/summary`.
- This is a small, safe, debug/local-only utility to speed up verification of which endpoints are exercised during tests.

Summary of what was done: added a debug-local endpoint to read and summarize `instance/logs/requests.log` so testers can quickly see which endpoints were hit.
