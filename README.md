# 03 — API Integrations

## Overview

A Python backend learning project focused on REST API integrations, authentication, webhook processing, and persistent event storage.

The project simulates an integration service receiving alarm events from industrial machines.

It demonstrates HTTP communication, data validation, API security, SQLite persistence, and automated testing.

## Features

### REST API Integration
- HTTP GET and POST requests using `httpx`
- Query parameters, headers, and JSON processing
- API key and Bearer token authentication
- Pagination and retry mechanisms
- HTTP error and timeout handling
- OAuth2 token caching and refresh logic

### Webhook Processing
- FastAPI endpoint: `POST /webhook`
- Request validation using Pydantic
- HMAC-SHA256 signature verification
- Timestamp validation (±300 seconds)
- Persistent event storage using SQLite
- Duplicate event detection using a UNIQUE constraint
- Handling concurrent requests with the same `event_id`

### Event Storage

Validated webhook events are stored in SQLite.

Each record contains:

- `event_id` — unique event identifier
- `event` — event type
- `machine` — machine identifier
- `alarm_code` — alarm code
- `timestamp` — event timestamp supplied by the sender
- `received_at` — event reception timestamp

The database is stored in a local file named `events_db`.

Event history persists across application restarts.

## Tech Stack

- Python 3.13+
- FastAPI
- Pydantic
- SQLite
- httpx
- pytest
- uv

## Installation

Install dependencies:

```bash
uv sync
```

Create a `.env` file in the project root:

```env
WEBHOOK_SECRET=your_random_secret
```

Use a securely generated secret. Do not commit the `.env` file to Git.

## Running the Application

Start the FastAPI server from the project root:

```bash
uv run uvicorn --app-dir src api_integrations.webhooks.webhook_api:app --reload
```

API endpoint:

```text
POST http://127.0.0.1:8000/webhook
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Webhook Requirements

Each request must contain:

- A valid JSON payload
- A unique `event_id`
- Event type `alarm.created`
- A current Unix timestamp in seconds
- Machine identifier and integer alarm code
- An `X-Webhook-Signature` header containing the HMAC-SHA256 hex digest of the exact request body

The request signature is generated using `WEBHOOK_SECRET`.

### HTTP Responses

| Status | Description |
|---|---|
| 200 | Event accepted and processed |
| 401 | Invalid signature or expired timestamp |
| 409 | Duplicate event identifier |
| 422 | Invalid event payload |

## Testing

Run the automated test suite:

```bash
uv run pytest -q
```

The tests cover:

- REST API requests and error handling
- OAuth2 token management
- Webhook payload validation
- HMAC signature verification
- Duplicate event detection
- SQLite read and write operations
- Persistence across registry reinitialization
- Concurrent requests with identical event IDs

Tests use mocked external HTTP requests and isolated temporary SQLite databases.

## Project Structure

```text
src/api_integrations/
├── api_client.py
├── oauth_token_manager.py
├── models.py
├── events_repository.py
├── events_registry.py
└── webhooks/
    ├── webhook_api.py
    ├── webhook_handler.py
    └── security.py

tests/
```

## Limitations

This is an educational backend project, not a production-ready industrial integration service.

- OAuth2 demonstration endpoints are placeholders.
- SQLite database location is configured locally.
- Event timestamps are stored as formatted local time strings.
- Duplicate detection protects event registration, but does not guarantee exactly-once execution of external business operations.
- Production deployment, monitoring, and operational recovery are outside the current scope.

## Learning Objectives

- Implement and test REST API integrations
- Understand OAuth2 and HTTP authentication
- Build and validate FastAPI endpoints
- Secure webhook requests using HMAC
- Design SQLite repositories
- Handle database integrity constraints
- Test persistence and concurrent operations
- Practice backend code organization and automated testing

## Status

Educational implementation of persistent webhook event storage (INT-004).