from fastapi.testclient import TestClient
from webhooks.webhook_api import app
import pytest

client = TestClient(app)


def test_webhook_returns_200(valid_payload):
    payload = valid_payload
    response = client.post(url="/webhook", json=payload)
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
    response = client.post(url="/webhook", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_webhook_returns_422_on_invalid_body():
    response = client.post(url="/webhook", json=[1, 2, 3])
    assert response.status_code == 422
