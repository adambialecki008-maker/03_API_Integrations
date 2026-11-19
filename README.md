# 03 — API Integrations

A Python backend learning project demonstrating REST API integrations, secure webhook processing, SQLite persistence, and a paginated alarm history API.

The application simulates a service that receives alarm events from industrial machines and provides authenticated access to their history.

## Features

- HTTP GET/POST integrations with `httpx`, query parameters, headers, retry/error handling, and pagination
- API key, Bearer token, and OAuth2 token-management examples
- Secure `POST /webhook` with HMAC-SHA256 signature verification
- Pydantic validation and timestamp freshness checks (±300 seconds)
- Persistent alarm storage in SQLite with duplicate-event protection
- `GET /events` with API key authentication, machine/event filters, UTC date ranges, `limit`, `offset`, and `total`
- Automated tests with `pytest` and FastAPI `TestClient`

## Technology

Python 3.13+, FastAPI, Pydantic, `httpx`, SQLite (`sqlite3`), `pytest`, and `uv`.

## Installation

```bash
git clone https://github.com/adambialecki008-maker/03_API_Integrations.git
cd 03_API_Integrations
uv sync
```

Create a `.env` file in the project root:

```dotenv
WEBHOOK_SECRET=replace_with_a_random_secret
EVENTS_API_KEY=replace_with_a_random_api_key
```

Do not commit the `.env` file or `events.db` to Git. In a production deployment, use HTTPS and appropriately managed secrets.

## Running the API

From the project root:

```bash
uv run uvicorn --app-dir src api_integrations.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

Both endpoints are registered on the same FastAPI application.

## API endpoints

### `POST /webhook` — Receive alarm events

Accepts an alarm event, validates its payload, verifies its HMAC-SHA256 signature, and stores it in SQLite.

Required header: `X-Webhook-Signature` — hexadecimal HMAC-SHA256 digest computed using `WEBHOOK_SECRET` and the **exact raw request body**.

Example request body:

```json
{
  "event_id": "evt_001",
  "event": "alarm.created",
  "timestamp": 1794932368,
  "data": {
    "machine": "PLC_01",
    "alarm_code": 204
  }
}
```

The sample timestamp is illustrative. Actual webhook requests need a current Unix timestamp within ±300 seconds of server time.

Successful response (`200`):

```json
{
  "event_id": "evt_001",
  "machine": "PLC_01",
  "alarm_code": 204
}
```

| HTTP status | Meaning |
| --- | --- |
| `200` | Event accepted |
| `401` | Invalid signature or expired timestamp |
| `409` | Duplicate `event_id` |
| `422` | Invalid payload |

### `GET /events` — Alarm history

Returns stored alarm events. This endpoint requires **only** `X-API-Key` (the value of `EVENTS_API_KEY`), not an HMAC signature.

| Parameter | Type | Default | Meaning |
| --- | --- | --- | --- |
| `event_id` | string | None | Filter by event ID |
| `machine` | string | None | Filter by machine |
| `time_from` | ISO 8601 datetime with timezone | None | Inclusive start (`>=`) |
| `time_to` | ISO 8601 datetime with timezone | None | Exclusive end (`<`) |
| `limit` | integer (1–100) | `100` | Maximum events per response |
| `offset` | integer (`>= 0`) | `0` | Number of matching events to skip |

Timestamps must include a timezone, e.g. `2026-11-18T08:30:00Z` or `2026-11-18T09:30:00+01:00`. The application converts times to UTC.

Example request (PowerShell):

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:8000/events?machine=PLC_01&limit=10&offset=0" `
  -Headers @{ "X-API-Key" = "replace_with_your_api_key" }
```

Example response (illustrative):

```json
{
  "events": [
    {
      "event_id": "evt_001",
      "event": "alarm.created",
      "data": {
        "machine": "PLC_01",
        "alarm_code": 204
      },
      "timestamp": "2026-11-17T16:19:30+00:00",
      "received_at": "2026-11-17T16:19:31+00:00"
    }
  ],
  "total": 1
}
```

`total` is the count of **all matching records before applying `limit` and `offset`**. The `events` array contains the requested page. For example, `limit=10&offset=0` retrieves the first page and `limit=10&offset=10` retrieves the second.

Events are ordered newest first (`timestamp DESC, id DESC`). An empty result has the form `{"events": [], "total": 0}`.

| HTTP status | Meaning |
| --- | --- |
| `200` | History returned, including empty results |
| `401` | Missing or incorrect API key |
| `422` | Invalid query parameters or time range |

## Data storage

The SQLite database file is `events.db`. It is created automatically when needed and is excluded from Git.

Each event contains `event_id`, `event`, `machine`, `alarm_code`, `timestamp`, and `received_at`. Timestamps are saved as UTC ISO 8601 strings with an explicit offset. A unique constraint on `event_id` prevents duplicate registration.

## Project structure

```text
src/api_integrations/
├── main.py
├── api_client.py
├── oauth_token_manager.py
├── security.py
├── models.py
├── events_repository.py
├── events_registry.py
├── events_history/
│   ├── api.py
│   └── handler.py
└── webhooks/
    ├── api.py
    └── handler.py

tests/
├── conftest.py
├── test_api_client.py
├── test_events_history_api.py
├── test_events_history_handler.py
├── test_events_repository.py
├── test_events_registry.py
├── test_models.py
├── test_oauth_token_manager.py
├── test_webhook_api.py
├── test_webhook_handler.py
└── test_webhook_security.py
```

## Testing

Run all tests:

```bash
uv run pytest -q
```

Run event-history tests:

```bash
uv run pytest tests/test_events_history_api.py tests/test_events_history_handler.py tests/test_events_repository.py -q
```

The test suite covers HTTP integration behavior, Pydantic models, HMAC security, persistence, duplicate detection, concurrent webhook requests, filtering, and offset-based pagination. Repository tests use temporary SQLite database files.

## Scope and limitations

This is an educational project, **not a production-ready industrial integration service**. It does not include user accounts, role-based permissions, rate limiting, migrations, monitoring, deployment configuration, or backup/recovery procedures. OAuth2 demonstrations do not integrate with a live identity provider.
