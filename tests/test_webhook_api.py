from fastapi.testclient import TestClient
from webhooks.webhook_api import app
from webhooks.webhook_api import secret
from webhooks.security import calculate_signature
import json
from pydantic import ValidationError

client = TestClient(app)


def test_webhook_returns_200(valid_payload):
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


def test_webhook_returns_422_on_wrong_event(valid_payload):
    payload = valid_payload
    payload["event"] = "alarm.deleted"
    raw_body = json.dumps(payload).encode("utf-8")
    signature = calculate_signature(raw_body, secret)
    headers = {"Content-Type": "application/json", "X-Webhook-Signature": signature}
    response = client.post(url="/webhook", content=raw_body, headers=headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid webhook payload"}


def test_webhook_returns_422_on_invalid_body():
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


def test_receive_webhook_raises_http_401_on_missing_header(valid_payload):
    payload = valid_payload
    raw_body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    response = client.post(url="/webhook", content=raw_body, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid webhook signature"}


def test_receive_webhook_raises_http_401_on_wrong_signature(valid_payload):
    payload = valid_payload
    raw_body = json.dumps(payload).encode("utf-8")
    signature = "test_signature_123"
    headers = {"Content-Type": "application/json", "X-Webhook-Signature": signature}
    response = client.post(url="/webhook", content=raw_body, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid webhook signature"}
