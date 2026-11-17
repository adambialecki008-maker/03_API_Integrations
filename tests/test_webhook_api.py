from fastapi.testclient import TestClient
from api_integrations.webhooks.webhook_api import app
from api_integrations.webhooks.webhook_api import secret
from api_integrations.webhooks.security import calculate_signature
import json, time, threading
from uuid import uuid4
from api_integrations.events_repository import EventsRepository, DuplicateEventError
from api_integrations.events_registry import EventRegistry
from concurrent.futures import ThreadPoolExecutor

client = TestClient(app)


def test_webhook_returns_200(valid_payload, tmp_path, monkeypatch):
    test_path = tmp_path / "test.db"
    monkeypatch.setattr(
        "api_integrations.webhooks.webhook_api.registry.path", test_path
    )
    payload = valid_payload
    raw_body = json.dumps(payload).encode("utf-8")
    signature = calculate_signature(raw_body, secret)
    headers = {"Content-Type": "application/json", "X-Webhook-Signature": signature}
    response = client.post(url="/webhook", content=raw_body, headers=headers)
    expected_json = {
        "event_id": "evt_001",
        "machine": "PLC_01",
        "alarm_code": 204,
    }
    assert response.status_code == 200
    assert response.json() == expected_json


def test_webhook_returns_422_on_wrong_event(valid_payload, tmp_path, monkeypatch):
    test_path = tmp_path / "test.db"
    monkeypatch.setattr(
        "api_integrations.webhooks.webhook_api.registry.path", test_path
    )
    payload = valid_payload
    payload["event"] = "alarm.deleted"
    raw_body = json.dumps(payload).encode("utf-8")
    signature = calculate_signature(raw_body, secret)
    headers = {"Content-Type": "application/json", "X-Webhook-Signature": signature}
    response = client.post(url="/webhook", content=raw_body, headers=headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid webhook payload"}


def test_webhook_returns_422_on_invalid_body(tmp_path, monkeypatch):
    test_path = tmp_path / "test.db"
    monkeypatch.setattr(
        "api_integrations.webhooks.webhook_api.registry.path", test_path
    )
    raw_body = json.dumps([1, 2, 3]).encode("utf-8")
    signature = calculate_signature(raw_body, secret)
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
    }
    response = client.post(
        url="/webhook",
        content=raw_body,
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid webhook payload"}


def test_receive_webhook_raises_http_401_on_missing_header(
    valid_payload, tmp_path, monkeypatch
):
    test_path = tmp_path / "test.db"
    monkeypatch.setattr(
        "api_integrations.webhooks.webhook_api.registry.path", test_path
    )
    payload = valid_payload
    raw_body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    response = client.post(url="/webhook", content=raw_body, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid webhook signature"}


def test_receive_webhook_raises_http_401_on_wrong_signature(
    valid_payload, tmp_path, monkeypatch
):
    test_path = tmp_path / "test.db"
    monkeypatch.setattr(
        "api_integrations.webhooks.webhook_api.registry.path", test_path
    )
    payload = valid_payload
    raw_body = json.dumps(payload).encode("utf-8")
    signature = "test_signature_123"
    headers = {"Content-Type": "application/json", "X-Webhook-Signature": signature}
    response = client.post(url="/webhook", content=raw_body, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid webhook signature"}


def test_receive_webhook_raises_http_401_on_expired_timestamp(
    valid_payload, tmp_path, monkeypatch
):
    test_path = tmp_path / "test.db"
    monkeypatch.setattr(
        "api_integrations.webhooks.webhook_api.registry.path", test_path
    )
    payload = valid_payload
    payload["timestamp"] = int(time.time()) - 600

    raw_body = json.dumps(payload).encode("utf-8")
    signature = calculate_signature(raw_body, secret)
    headers = headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
    }
    response = client.post(url="/webhook", headers=headers, content=raw_body)

    assert response.status_code == 401
    assert response.json() == {"detail": "Expired webhook timestamp"}


def test_receive_webhook_raises_http_409_on_duplicate_registry(
    valid_payload, tmp_path, monkeypatch
):
    test_path = tmp_path / "test.db"
    monkeypatch.setattr(
        "api_integrations.webhooks.webhook_api.registry.path", test_path
    )
    payload = valid_payload
    payload["event_id"] = f"evt_{uuid4()}"
    raw_body = json.dumps(valid_payload).encode("utf-8")
    signature = calculate_signature(raw_body, secret)
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
    }
    response_old = client.post(
        "/webhook",
        content=raw_body,
        headers=headers,
    )
    response_new = client.post(
        "/webhook",
        content=raw_body,
        headers=headers,
    )

    assert response_old.status_code == 200
    assert response_new.status_code == 409
    assert response_new.json() == {"detail": "Duplicate webhook event"}


def test_receive_webhook_raises_http_409_on_sqlite3_duplication_error(
    valid_payload, tmp_path, monkeypatch
):
    test_path = tmp_path / "test.db"
    monkeypatch.setattr(
        "api_integrations.webhooks.webhook_api.registry.path", test_path
    )
    monkeypatch.setattr(
        EventsRepository,
        "get_event_by_event_id",
        lambda self, event_id: None,
    )
    monkeypatch.setattr(
        EventsRepository,
        "save_event",
        lambda self, payload: (_ for _ in ()).throw(DuplicateEventError()),
    )
    payload = valid_payload
    payload["event_id"] = f"evt_{uuid4()}"
    raw_body = json.dumps(valid_payload).encode("utf-8")
    signature = calculate_signature(raw_body, secret)
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
    }
    response = client.post(
        "/webhook",
        content=raw_body,
        headers=headers,
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Duplicate webhook event"}


def test_receive_webhook_persists_history_across_registry_reinitialization(
    valid_payload, tmp_path, monkeypatch
):
    test_path = tmp_path / "test.db"
    monkeypatch.setattr(
        "api_integrations.webhooks.webhook_api.registry.path", test_path
    )

    payload = valid_payload.copy()
    payload["event_id"] = f"evt_{uuid4()}"
    raw_body = json.dumps(payload).encode("utf-8")
    signature = calculate_signature(raw_body, secret)
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
    }

    first_response = client.post(
        "/webhook",
        content=raw_body,
        headers=headers,
    )
    assert first_response.status_code == 200

    new_registry = EventRegistry()
    new_registry.path = test_path
    monkeypatch.setattr("api_integrations.webhooks.webhook_api.registry", new_registry)

    second_response = client.post(
        "/webhook",
        content=raw_body,
        headers=headers,
    )
    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Duplicate webhook event"}


def test_receive_webhook_concurrent_requests_real_sqlite_returns_200_and_409(
    valid_payload, tmp_path, monkeypatch
):
    test_path = tmp_path / "test_concurrent.db"
    monkeypatch.setattr(
        "api_integrations.webhooks.webhook_api.registry.path", test_path
    )

    payload = valid_payload.copy()
    payload["event_id"] = f"evt_{uuid4()}"
    raw_body = json.dumps(payload).encode("utf-8")
    signature = calculate_signature(raw_body, secret)
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
    }

    barrier = threading.Barrier(2)

    def send_concurrent_request():
        barrier.wait()
        return client.post(
            "/webhook",
            content=raw_body,
            headers=headers,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_1 = executor.submit(send_concurrent_request)
        future_2 = executor.submit(send_concurrent_request)
        responses = [future_1.result(), future_2.result()]

    status_codes = sorted([res.status_code for res in responses])

    assert status_codes == [200, 409]

    duplicate_response = next(res for res in responses if res.status_code == 409)
    assert duplicate_response.json() == {"detail": "Duplicate webhook event"}
