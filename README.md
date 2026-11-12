# 03 — API Integrations

A Python learning project focused on REST API integrations, authentication, webhook processing and automated testing.

## Features

- REST API requests with `httpx`
- Pagination, retries and error handling
- OAuth2 token management and refresh
- FastAPI webhook endpoint
- Payload validation with Pydantic
- HMAC-SHA256 signature verification
- Timestamp validation (±300 seconds)
- In-memory duplicate event detection using `event_id`
- Automated tests with pytest

## Tech Stack

Python, FastAPI, httpx, Pydantic, pytest, uv.

## Installation

```bash
uv sync
```

## Run the API

```bash
uv run uvicorn webhooks.webhook_api:app --reload
```

The webhook endpoint is available at `POST /webhook`.

Create a `.env` file containing:

```env
WEBHOOK_SECRET=your_random_secret
```

Never commit the `.env` file.

## Tests

```bash
uv run pytest -q
```

## Webhook Security

The endpoint verifies the HMAC signature before validating the payload.

Expected responses:

| Status | Meaning |
|---|---|
| 200 | Successfully processed |
| 401 | Invalid signature or expired timestamp |
| 422 | Invalid payload |
| 409 | Duplicate event ID |

## Limitations / Future Improvements

**Replay attack protection is currently educational, not production-ready.**

Duplicate event IDs are stored in an in-memory Python `set`.

This means:

- Stored IDs disappear after an application restart.
- Multiple application processes do not share the registry.
- Concurrent requests may require atomic duplicate detection.
- Stored identifiers are not automatically removed.

**Planned improvement:** Implement persistent event deduplication using SQLite, a unique constraint on `event_id`, and database transactions.

This will be covered separately in the SQL / Database Integration module.

## Purpose

Hands-on practice building and testing Python API integrations, with an emphasis on authentication, input validation and webhook security.